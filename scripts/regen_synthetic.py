"""Tier 1 — regenerate synthetic samples with the already-fixed generator code.

Loads the notebook, filters to cells 0-17 (config, imports, data, model defs,
checkpoint loading) + cells 20 (generation functions) + 22 (generation loop),
patches FORCE_GENERATE=True and all FORCE_TRAIN_*=False, writes to a temp
notebook, executes it with nbclient.

After the execution the script loads every .npz under checkpoints/synthetic/
and compares its growth-rate statistics against the real series. Writes a JSON
report to results/smoke_test_tier1.json and prints pass/fail per model.

Runs in foreground; expected wall-clock is tens of minutes to a few hours
depending on qGAN/qVAE circuit simulation speed. Use run_in_background=True
from the outside if you need it non-blocking.

Usage:
    .venv/bin/python scripts/regen_synthetic.py
"""

from __future__ import annotations

import json
import os
import pathlib
import shutil
import sys
import tempfile
from dataclasses import dataclass

ROOT = pathlib.Path(__file__).resolve().parents[1]
os.chdir(ROOT)
NB_PATH = ROOT / "hqss_experiment.ipynb"
TMP_PATH = ROOT / ".regen_tmp.ipynb"
RESULTS_DIR = ROOT / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# Cells to keep:
#   0-17: config, imports, data loading, preprocessing, model classes,
#         checkpoint loading (FORCE_TRAIN_* all False, so this only loads)
#   20:   main generation functions (_qgan_generate_one etc.)
#   22:   generation loop that writes checkpoints/synthetic/*
#
# Skipped:
#   18, 19: no-PAR qGAN/cGAN retrain/load (ablation, not needed for Tier 1)
#   21:     no-PAR generation functions (ablation)
#   23+:    visualization, LSTM, analysis, IBM — all downstream of Tier 1
KEEP_CELLS = list(range(0, 18)) + [20, 22]


def build_trimmed_notebook() -> dict:
    nb = json.loads(NB_PATH.read_text())
    cells = [nb["cells"][i] for i in KEEP_CELLS]

    # Config cell is index 2 in original and remains index 2 after filtering.
    cfg = cells[2]
    src = "".join(cfg["source"])
    if "FORCE_GENERATE     = False" not in src:
        raise RuntimeError(
            "Config cell layout changed — expected `FORCE_GENERATE     = False`. "
            "Update scripts/regen_synthetic.py before running."
        )
    src = src.replace("FORCE_GENERATE     = False", "FORCE_GENERATE     = True")
    # Defensive: make sure no training is triggered regardless of notebook WIP
    for flag in [
        "FORCE_TRAIN_QGAN",
        "FORCE_TRAIN_QVAE",
        "FORCE_TRAIN_CGAN",
        "FORCE_TRAIN_CVAE",
    ]:
        src = src.replace(f"{flag}   = True", f"{flag}   = False")
    cfg["source"] = src.splitlines(keepends=True)

    nb["cells"] = cells
    return nb


def execute_notebook(nb: dict) -> dict:
    from nbclient import NotebookClient
    from nbclient.exceptions import CellExecutionError
    import nbformat

    nb_node = nbformat.from_dict(nb)
    client = NotebookClient(
        nb_node,
        timeout=None,
        kernel_name="python3",
        resources={"metadata": {"path": str(ROOT)}},
    )
    try:
        client.execute()
    except CellExecutionError as e:
        # Persist partial notebook for inspection
        TMP_PATH.write_text(nbformat.writes(nb_node))
        raise RuntimeError(
            f"Notebook execution failed. Partial state saved to {TMP_PATH}.\n{e}"
        ) from e
    return nb_node


def smoke_check() -> dict:
    """Load every .npz in checkpoints/synthetic and summarise growth-rate stats.

    Acceptance rules:
    - at least 1 .npz per model
    - growth-rate std within [0.25x, 4x] of real std (strict: [0.5x, 2x])
    - growth-rate mean within |3 * real_std| of real mean (rules out sign-biased output)
    - no all-positive or all-negative model output when real spans both signs
    """
    import numpy as np
    import pandas as pd

    df = pd.read_csv(ROOT / "data.csv")
    raw_od = df["OD"].to_numpy(dtype=float)
    # Mirror notebook: growth_rate = log-diff after dithering
    # Use the same DITHER as notebook default (0.005). Dithering is stochastic but
    # stats are stable to within percent, which is enough for a smoke check.
    rng = np.random.default_rng(0)
    dithered = raw_od + rng.uniform(-0.005, 0.005, size=raw_od.shape)
    real_gr = np.diff(np.log(np.clip(dithered, 1e-6, None)))
    real_mean = float(real_gr.mean())
    real_std = float(real_gr.std(ddof=1))

    synth_root = ROOT / "checkpoints" / "synthetic"
    report = {
        "real_growth_rate": {"mean": real_mean, "std": real_std, "n": len(real_gr)},
        "models": {},
        "overall_pass": True,
    }

    for model_dir in sorted(synth_root.iterdir()):
        if not model_dir.is_dir():
            continue
        model_name = model_dir.name
        files = sorted(model_dir.glob("*.npz"))
        if not files:
            report["models"][model_name] = {"pass": False, "reason": "no files"}
            report["overall_pass"] = False
            continue

        gr_all = []
        for f in files:
            with np.load(f, allow_pickle=True) as data:
                ld_curves = data["ld_curves"]
                for curve in ld_curves:
                    curve = np.asarray(curve, dtype=float)
                    gr_all.append(curve)
        if not gr_all:
            report["models"][model_name] = {"pass": False, "reason": "empty curves"}
            report["overall_pass"] = False
            continue

        gr_flat = np.concatenate(gr_all)
        m_mean = float(gr_flat.mean())
        m_std = float(gr_flat.std(ddof=1))
        m_min = float(gr_flat.min())
        m_max = float(gr_flat.max())
        ratio = m_std / real_std if real_std > 0 else float("nan")

        strict_pass = 0.5 <= ratio <= 2.0
        loose_pass = 0.25 <= ratio <= 4.0
        mean_ok = abs(m_mean - real_mean) <= 3 * real_std
        sign_ok = (m_min < 0) and (m_max > 0)

        report["models"][model_name] = {
            "n_files": len(files),
            "n_curves": len(gr_all),
            "n_points": len(gr_flat),
            "mean": m_mean,
            "std": m_std,
            "min": m_min,
            "max": m_max,
            "std_ratio_to_real": ratio,
            "strict_pass": bool(strict_pass and mean_ok and sign_ok),
            "loose_pass": bool(loose_pass and mean_ok and sign_ok),
            "mean_ok": bool(mean_ok),
            "sign_ok": bool(sign_ok),
        }
        # Overall pass is "loose" — we want to catch the 10x-compression regression,
        # not fail on minor architectural differences between models.
        if not (loose_pass and mean_ok and sign_ok):
            report["overall_pass"] = False

    return report


def main():
    print(f"[Tier 1] Building trimmed notebook ({len(KEEP_CELLS)} cells)...")
    nb = build_trimmed_notebook()
    TMP_PATH.write_text(json.dumps(nb))

    print(f"[Tier 1] Executing via nbclient (this will take a while)...")
    try:
        execute_notebook(nb)
    finally:
        # Leave TMP_PATH for debugging if exec failed; remove on success
        if TMP_PATH.exists() and not os.environ.get("KEEP_TMP_NOTEBOOK"):
            try:
                TMP_PATH.unlink()
            except OSError:
                pass

    print("[Tier 1] Generation done. Running smoke check...")
    report = smoke_check()

    out = RESULTS_DIR / "smoke_test_tier1.json"
    out.write_text(json.dumps(report, indent=2))
    print(f"[Tier 1] Wrote {out}")

    print()
    print(f"Real growth-rate  mean={report['real_growth_rate']['mean']:+.5f}  std={report['real_growth_rate']['std']:.5f}")
    print(f"{'model':<8} {'mean':>10} {'std':>9} {'ratio':>7} {'strict':>7} {'loose':>6}")
    for name, m in report["models"].items():
        if "reason" in m:
            print(f"{name:<8} FAIL — {m['reason']}")
            continue
        print(f"{name:<8} {m['mean']:+10.5f} {m['std']:9.5f} {m['std_ratio_to_real']:7.2f} "
              f"{str(m['strict_pass']):>7} {str(m['loose_pass']):>6}")

    if not report["overall_pass"]:
        print("\nOVERALL: FAIL — at least one model's output is outside acceptance range.")
        sys.exit(2)
    print("\nOVERALL: PASS")


if __name__ == "__main__":
    main()
