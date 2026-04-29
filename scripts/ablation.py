"""Ablation study — the experimental core of this project.

Trains the same model on three nested feature groups:

    A: raw cycle features only
    B: A + rolling-window statistics
    C: B + physics-derived features (charge/discharge ratio,
       temperature rise vs baseline, voltage decline)

…and reports test-set RMSE, MAE, and R² for each. The deltas between
groups tell us what each *family* of features adds on top of the
previous one.

    python scripts/ablation.py --model random_forest

Outputs:
    results/ablation.csv
    results/ablation.md     (markdown table — paste into the report)
    results/ablation.png    (RMSE and R² bar charts)
"""
import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.evaluate import plot_ablation_results, regression_metrics
from src.features import FEATURE_GROUPS, build_features
from src.models import (
    XGBOOST_AVAILABLE,
    train_random_forest,
    train_xgboost,
)


DATA_PATH = Path("data/processed/cycles.csv")
RESULTS_DIR = Path("results")
TRAIN_CELLS = ["B0005", "B0006", "B0007"]
TEST_CELLS = ["B0018"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model",
        choices=["random_forest", "xgboost"],
        default="random_forest",
    )
    args = parser.parse_args()

    if not DATA_PATH.exists():
        print(f"{DATA_PATH} not found. Run scripts/load_data.py first.")
        sys.exit(1)

    if args.model == "xgboost" and not XGBOOST_AVAILABLE:
        print("xgboost is not installed. Install it or use --model random_forest.")
        sys.exit(1)

    train_fn = train_random_forest if args.model == "random_forest" else train_xgboost

    print(f"Loading {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)
    df = build_features(df)

    train_df = df[df["cell_id"].isin(TRAIN_CELLS)]
    test_df = df[df["cell_id"].isin(TEST_CELLS)]
    print(f"Train: {len(train_df)} rows | Test (held-out {TEST_CELLS}): {len(test_df)} rows")
    print(f"Model: {args.model}\n")

    rows = []
    for group_name, feature_cols in FEATURE_GROUPS.items():
        X_train = train_df[feature_cols]
        y_train = train_df["soh"]
        X_test = test_df[feature_cols]
        y_test = test_df["soh"]

        model = train_fn(X_train, y_train)
        preds = model.predict(X_test)
        m = regression_metrics(y_test, preds)
        rows.append({
            "group": group_name,
            "n_features": len(feature_cols),
            "rmse": m["rmse"],
            "mae": m["mae"],
            "r2": m["r2"],
        })
        print(f"  {group_name:<40}  n={len(feature_cols):>3}  "
              f"RMSE={m['rmse']:.4f}  MAE={m['mae']:.4f}  R²={m['r2']:.4f}")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    df_results = pd.DataFrame(rows)
    df_results.to_csv(RESULTS_DIR / "ablation.csv", index=False)

    md = ["# Ablation results", "",
          f"Model: **{args.model}** | Held-out cell: **{TEST_CELLS[0]}**", "",
          "| Feature group | # features | RMSE | MAE | R² |",
          "|---|---:|---:|---:|---:|"]
    for r in rows:
        md.append(f"| {r['group']} | {r['n_features']} | "
                  f"{r['rmse']:.4f} | {r['mae']:.4f} | {r['r2']:.4f} |")
    (RESULTS_DIR / "ablation.md").write_text("\n".join(md) + "\n")

    plot_ablation_results(df_results, RESULTS_DIR / "ablation.png")

    print(f"\nWrote results/ablation.csv, ablation.md, ablation.png")
    print("\nNext step: open results/ablation.md, copy the table into your report,")
    print("and write 1-2 paragraphs interpreting the deltas between groups.")


if __name__ == "__main__":
    main()
