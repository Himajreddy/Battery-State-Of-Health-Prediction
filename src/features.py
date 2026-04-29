"""Feature engineering — organised into groups for the ablation study.

The whole point of this project is to compare what happens when we add
different *kinds* of features. So the features are split into three named
groups and the FEATURE_GROUPS dict at the bottom defines what's in each.

Group A — raw cycle features.
    The bare minimum: what the cell's voltage, current, and temperature
    looked like on this single cycle, plus how long charging and
    discharging took.

Group B — A + rolling statistics.
    A single cycle is noisy. Rolling-window means and standard deviations
    over the last 3, 5, and 10 cycles give the model short-term memory of
    the trajectory.

Group C — B + physics-derived features.
    These come from electrochemistry intuition rather than statistics:

    - charge_to_discharge_ratio: As a cell ages, its internal resistance
      grows. Internal resistance slows charging more than it slows
      discharging (constant-current discharge is rate-limited by the
      protocol, not the cell), so the ratio drifts upward with age.

    - temp_rise_vs_baseline: Power dissipated as heat is I^2 * R_internal.
      Higher internal resistance means more heat at the same current, so a
      degraded cell runs hotter than its own younger self.

    - voltage_decline: Mean discharge voltage falls as ohmic drop grows.
      A direct, if noisy, signal of impedance growth.
"""
import pandas as pd


ROLLING_WINDOWS = (3, 5, 10)
ROLLING_COLUMNS = ("capacity", "voltage_mean", "temperature_mean")


# --- Group A: raw cycle features ------------------------------------------

GROUP_A_FEATURES = [
    "voltage_mean",
    "voltage_min",
    "voltage_max",
    "current_mean",
    "temperature_mean",
    "temperature_max",
    "charge_duration_s",
    "discharge_duration_s",
]


# --- Group B: A + rolling statistics --------------------------------------

def add_rolling_features(df):
    """Mean and std for each ROLLING_COLUMN over each ROLLING_WINDOWS.

    Computed per cell so windows never cross cell boundaries.
    """
    df = df.sort_values(["cell_id", "cycle"]).copy()
    for col in ROLLING_COLUMNS:
        for w in ROLLING_WINDOWS:
            grouped = df.groupby("cell_id")[col]
            df[f"{col}_rmean_{w}"] = (
                grouped.rolling(w, min_periods=1).mean().reset_index(level=0, drop=True)
            )
            df[f"{col}_rstd_{w}"] = (
                grouped.rolling(w, min_periods=2).std().reset_index(level=0, drop=True)
            ).fillna(0.0)
    return df


GROUP_B_EXTRA = [
    f"{col}_{stat}_{w}"
    for col in ROLLING_COLUMNS
    for w in ROLLING_WINDOWS
    for stat in ("rmean", "rstd")
]


# --- Group C: B + physics-derived features --------------------------------

def add_physics_features(df):
    """Hand-crafted features motivated by Li-ion electrochemistry.

    See module docstring for the reasoning behind each one.
    """
    df = df.copy()
    df["charge_to_discharge_ratio"] = (
        df["charge_duration_s"] / df["discharge_duration_s"].clip(lower=1)
    )

    # Per cell, baseline = mean of first 5 cycles. Subsequent cycles are
    # measured against this cell's own young self, so we don't conflate
    # cell-to-cell offsets with degradation.
    def _baselined(group, col):
        baseline = group[col].iloc[:5].mean()
        return group[col] - baseline

    df["temp_rise_vs_baseline"] = (
        df.groupby("cell_id", group_keys=False)
        .apply(lambda g: _baselined(g, "temperature_mean"))
        .reset_index(drop=True)
    )
    df["voltage_decline"] = (
        df.groupby("cell_id", group_keys=False)
        .apply(lambda g: _baselined(g, "voltage_mean"))
        .reset_index(drop=True)
    )
    return df


GROUP_C_EXTRA = [
    "charge_to_discharge_ratio",
    "temp_rise_vs_baseline",
    "voltage_decline",
]


# --- Pipeline -------------------------------------------------------------

def build_features(df):
    """Apply all feature blocks. The ablation script picks subsets
    via FEATURE_GROUPS below; this function just makes sure every column
    exists after one pass.
    """
    df = add_rolling_features(df)
    df = add_physics_features(df)
    return df


# What goes into each ablation group. Group B is a superset of A; Group C
# is a superset of B. The ablation tells us how much each *added* family
# of features actually contributes.
FEATURE_GROUPS = {
    "A_raw": GROUP_A_FEATURES,
    "B_raw_plus_rolling": GROUP_A_FEATURES + GROUP_B_EXTRA,
    "C_raw_plus_rolling_plus_physics": GROUP_A_FEATURES + GROUP_B_EXTRA + GROUP_C_EXTRA,
}
