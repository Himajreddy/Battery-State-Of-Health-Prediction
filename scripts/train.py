"""Train one model on one feature group. The Week 2 baseline runs:

    python scripts/train.py --model random_forest --features C_raw_plus_rolling_plus_physics

For the Week 3 ablation, use scripts/ablation.py instead — it loops over
all three feature groups and writes a comparison table.
"""
import argparse
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.evaluate import (
    plot_capacity_fade,
    plot_feature_importance,
    plot_predicted_vs_actual,
    regression_metrics,
)
from src.features import FEATURE_GROUPS, build_features
from src.models import (
    XGBOOST_AVAILABLE,
    save_model,
    train_random_forest,
    train_xgboost,
)


DATA_PATH = Path("data/processed/cycles.csv")
RESULTS_DIR = Path("results")
MODELS_DIR = Path("models")

# Cell-level chronological split. Never shuffle randomly: cycles within
# one cell are highly correlated, so a random split lets the model "see
# the future" of cells in the training set, inflating accuracy. See
# README's Method section for the full reasoning.
TRAIN_CELLS = ["B0005", "B0006", "B0007"]
TEST_CELLS = ["B0018"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model",
        choices=["random_forest", "xgboost"],
        default="random_forest",
    )
    parser.add_argument(
        "--features",
        choices=list(FEATURE_GROUPS.keys()),
        default="C_raw_plus_rolling_plus_physics",
        help="Which feature group to train on.",
    )
    args = parser.parse_args()

    if not DATA_PATH.exists():
        print(f"{DATA_PATH} not found. Run scripts/load_data.py first.")
        sys.exit(1)

    if args.model == "xgboost" and not XGBOOST_AVAILABLE:
        print("xgboost is not installed. Install it or use --model random_forest.")
        sys.exit(1)

    print(f"Loading {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)
    print(f"  {len(df)} rows across {df['cell_id'].nunique()} cells")

    print("Building features...")
    df = build_features(df)
    feature_cols = FEATURE_GROUPS[args.features]
    print(f"  Group: {args.features} ({len(feature_cols)} features)")

    train_df = df[df["cell_id"].isin(TRAIN_CELLS)]
    test_df = df[df["cell_id"].isin(TEST_CELLS)]
    if len(test_df) == 0:
        print(f"No rows for held-out cells {TEST_CELLS}.")
        sys.exit(1)

    X_train, y_train = train_df[feature_cols], train_df["soh"]
    X_test, y_test = test_df[feature_cols], test_df["soh"]
    print(f"  Train: {len(X_train)} rows from {TRAIN_CELLS}")
    print(f"  Test : {len(X_test)} rows from {TEST_CELLS}")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    plot_capacity_fade(df, RESULTS_DIR / "capacity_fade.png")

    train_fn = train_random_forest if args.model == "random_forest" else train_xgboost
    print(f"\nTraining {args.model}...")
    model = train_fn(X_train, y_train)

    preds = model.predict(X_test)
    metrics = regression_metrics(y_test, preds)
    print(f"  RMSE={metrics['rmse']:.4f}  MAE={metrics['mae']:.4f}  R2={metrics['r2']:.4f}")

    tag = f"{args.model}__{args.features}"
    save_model(model, MODELS_DIR / f"{tag}.joblib")
    plot_predicted_vs_actual(
        y_test, preds,
        title=f"{args.model} ({args.features}) — R²={metrics['r2']:.3f}",
        out_path=RESULTS_DIR / f"{tag}_pred_vs_actual.png",
    )
    plot_feature_importance(
        model, feature_cols,
        out_path=RESULTS_DIR / f"{tag}_feature_importance.png",
    )

    out_json = RESULTS_DIR / f"{tag}_metrics.json"
    with open(out_json, "w") as f:
        json.dump({"model": args.model, "features": args.features, **metrics}, f, indent=2)

    print(f"\nSaved model to     models/{tag}.joblib")
    print(f"Saved plots to     results/{tag}_*.png")
    print(f"Saved metrics to   {out_json}")


if __name__ == "__main__":
    main()
