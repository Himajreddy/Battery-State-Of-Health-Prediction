"""Process the raw NASA .mat files into a single CSV.

Run this once after putting the .mat files in data/raw/.

    python scripts/load_data.py
"""
import sys
from pathlib import Path

import pandas as pd

# So that 'from src...' works when run as a script
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.data import add_soh, aggregate_to_cycle_level, load_battery_file


CELLS = ["B0005", "B0006", "B0007", "B0018"]
RAW_DIR = Path("data/raw")
OUT_PATH = Path("data/processed/cycles.csv")


def main():
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    all_cycles = []
    for cell_id in CELLS:
        mat_path = RAW_DIR / f"{cell_id}.mat"
        if not mat_path.exists():
            print(f"  !! {mat_path} not found, skipping")
            continue
        print(f"Loading {cell_id}...")
        all_cycles.append(load_battery_file(mat_path))

    if not all_cycles:
        print("\nNo .mat files found in data/raw/.")
        print("Download them from the NASA PCoE portal — see data/README.md")
        sys.exit(1)

    raw = pd.concat(all_cycles, ignore_index=True)
    print(f"Raw rows (charge + discharge phases): {len(raw)}")

    aggregated = aggregate_to_cycle_level(raw)
    aggregated = add_soh(aggregated)
    print(f"Cycle-level rows: {len(aggregated)}")

    aggregated.to_csv(OUT_PATH, index=False)
    print(f"Saved to {OUT_PATH}")


if __name__ == "__main__":
    main()
