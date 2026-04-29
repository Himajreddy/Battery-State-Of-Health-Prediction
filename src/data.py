"""Load NASA battery .mat files into a tidy DataFrame.

The raw files have nested MATLAB structs. Each cell file contains a list
of cycles, and each cycle is either a charge phase, a discharge phase, or
an impedance measurement. Capacity (the thing we ultimately care about)
is recorded only on discharge phases, so we anchor on those.
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.io import loadmat


def load_battery_file(mat_path):
    """Read one cell's .mat file and return its cycles as a long DataFrame.

    One row per phase (so usually two rows per cycle: charge + discharge).
    The `type` column lets the next step pair them up.
    """
    cell_id = Path(mat_path).stem  # e.g. 'B0005'
    mat = loadmat(mat_path, simplify_cells=True)
    cycles = mat[cell_id]["cycle"]

    rows = []
    for i, cyc in enumerate(cycles, start=1):
        if cyc["type"] not in ("charge", "discharge"):
            continue  # skip impedance measurements

        d = cyc["data"]
        time = np.atleast_1d(d.get("Time", [0.0])).ravel()
        voltage = np.atleast_1d(d.get("Voltage_measured", [np.nan])).ravel()
        current = np.atleast_1d(d.get("Current_measured", [np.nan])).ravel()
        temp = np.atleast_1d(d.get("Temperature_measured", [np.nan])).ravel()

        row = {
            "cell_id": cell_id,
            "cycle": i,
            "type": cyc["type"],
            "duration_s": float(time[-1] - time[0]) if len(time) > 1 else 0.0,
            "voltage_mean": float(np.nanmean(voltage)),
            "voltage_min": float(np.nanmin(voltage)),
            "voltage_max": float(np.nanmax(voltage)),
            "current_mean": float(np.nanmean(current)),
            "temperature_mean": float(np.nanmean(temp)),
            "temperature_max": float(np.nanmax(temp)),
        }
        # Capacity is only recorded on the discharge phase
        if cyc["type"] == "discharge" and "Capacity" in d:
            row["capacity"] = float(d["Capacity"])
        rows.append(row)

    return pd.DataFrame(rows)


def aggregate_to_cycle_level(df):
    """Merge each (cell, cycle)'s charge and discharge phases into one row.

    We anchor on the discharge phase (it carries the capacity measurement)
    and pull the matching charge-phase duration alongside.
    """
    charge = df[df["type"] == "charge"].set_index(["cell_id", "cycle"])
    discharge = df[df["type"] == "discharge"].set_index(["cell_id", "cycle"])

    out = pd.DataFrame(index=discharge.index)
    out["voltage_mean"] = discharge["voltage_mean"]
    out["voltage_min"] = discharge["voltage_min"]
    out["voltage_max"] = discharge["voltage_max"]
    out["current_mean"] = discharge["current_mean"]
    out["temperature_mean"] = discharge["temperature_mean"]
    out["temperature_max"] = discharge["temperature_max"]
    out["discharge_duration_s"] = discharge["duration_s"]
    out["charge_duration_s"] = charge["duration_s"].reindex(out.index)
    out["capacity"] = discharge["capacity"]

    # A few cycles in the dataset have a discharge but no preceding charge
    # recorded (or vice versa). Fill rather than drop, so we don't lose data.
    out["charge_duration_s"] = out["charge_duration_s"].ffill().bfill()

    return out.reset_index().dropna(subset=["capacity"]).reset_index(drop=True)


def add_soh(df, n_reference_cycles=5):
    """Compute SOH = capacity / nominal_capacity for each cell.

    Using cycle 1 alone as the nominal is noisy. Averaging the first 5
    cycles is a common convention in the battery literature.
    """
    df = df.copy()
    df["soh"] = 0.0
    for cell_id in df["cell_id"].unique():
        mask = df["cell_id"] == cell_id
        cell = df.loc[mask].sort_values("cycle")
        nominal = cell["capacity"].iloc[:n_reference_cycles].mean()
        df.loc[mask, "soh"] = df.loc[mask, "capacity"] / nominal
    return df
