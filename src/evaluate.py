"""Evaluation: metrics and diagnostic plots."""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def regression_metrics(y_true, y_pred):
    """RMSE and MAE measure error magnitude in SOH units (0–1 scale).
    R² says how much variance the model explains (1.0 = perfect).
    """
    return {
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "r2": float(r2_score(y_true, y_pred)),
    }


def plot_capacity_fade(df, out_path):
    """Capacity fade per cell — the first plot to make on this dataset."""
    fig, ax = plt.subplots(figsize=(8, 5))
    for cell_id, cell in df.groupby("cell_id"):
        cell = cell.sort_values("cycle")
        ax.plot(cell["cycle"], cell["soh"] * 100, label=cell_id, alpha=0.85)
    ax.axhline(80, color="red", linestyle="--", label="End-of-life (80%)")
    ax.set_xlabel("Cycle")
    ax.set_ylabel("SOH (%)")
    ax.set_title("Capacity fade across cells")
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=110, bbox_inches="tight")
    plt.close()


def plot_predicted_vs_actual(y_true, y_pred, title, out_path):
    """Points should sit on the y=x line. Systematic deviations (e.g. all
    predictions below the line above 90% SOH) indicate bias.
    """
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(y_true * 100, y_pred * 100, alpha=0.6, s=20)
    lo, hi = 70, 102
    ax.plot([lo, hi], [lo, hi], "r--", linewidth=1, label="Perfect prediction")
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_xlabel("True SOH (%)")
    ax.set_ylabel("Predicted SOH (%)")
    ax.set_title(title)
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=110, bbox_inches="tight")
    plt.close()


def plot_feature_importance(model, feature_names, out_path, top_k=15):
    """Which features did the model lean on most? Critical talking point."""
    importances = model.feature_importances_
    top_idx = np.argsort(importances)[::-1][:top_k][::-1]

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.barh(np.array(feature_names)[top_idx], importances[top_idx])
    ax.set_xlabel("Importance")
    ax.set_title(f"Top {top_k} features")
    ax.grid(alpha=0.3, axis="x")
    plt.tight_layout()
    plt.savefig(out_path, dpi=110, bbox_inches="tight")
    plt.close()


def plot_ablation_results(ablation_df, out_path):
    """Bar chart comparing the three feature groups by RMSE and R².

    `ablation_df` is the table written by scripts/ablation.py: one row
    per group, columns rmse / mae / r2 / n_features.
    """
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

    ax = axes[0]
    ax.bar(ablation_df["group"], ablation_df["rmse"], color="steelblue")
    ax.set_ylabel("RMSE (lower is better)")
    ax.set_title("Test RMSE on held-out cell B0018")
    ax.tick_params(axis="x", rotation=15)
    ax.grid(alpha=0.3, axis="y")

    ax = axes[1]
    ax.bar(ablation_df["group"], ablation_df["r2"], color="seagreen")
    ax.set_ylabel("R² (higher is better)")
    ax.set_ylim(0, 1)
    ax.set_title("Test R² on held-out cell B0018")
    ax.tick_params(axis="x", rotation=15)
    ax.grid(alpha=0.3, axis="y")

    plt.tight_layout()
    plt.savefig(out_path, dpi=110, bbox_inches="tight")
    plt.close()
