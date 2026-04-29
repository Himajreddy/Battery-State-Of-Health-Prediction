# Data

This project uses the **NASA Prognostics Center of Excellence (PCoE)
Lithium-Ion Battery Aging dataset**, by B. Saha and K. Goebel (2007).

## Download

The dataset is publicly available from the NASA PCoE data repository:

> https://www.nasa.gov/intelligent-systems-division/discovery-and-systems-health/pcoe/pcoe-data-set-repository/

Look for "Battery Data Set". The portal distributes the files as a
single zip archive; extract it and copy these four files into
`data/raw/`:

- `B0005.mat`
- `B0006.mat`
- `B0007.mat`
- `B0018.mat`

## After downloading

Run the loader once. It reads the `.mat` files, aggregates each
charge/discharge cycle into a single row, and writes one CSV that all
the other scripts use:

```
python scripts/load_data.py
```

This produces `data/processed/cycles.csv`.

## Schema of cycles.csv

| Column | Meaning |
|--------|---------|
| `cell_id` | "B0005" / "B0006" / "B0007" / "B0018" |
| `cycle` | 1-indexed cycle number within that cell |
| `voltage_mean` / `_min` / `_max` | discharge-phase voltage statistics (V) |
| `current_mean` | mean discharge current (A, negative = discharging) |
| `temperature_mean` / `_max` | discharge-phase cell temperature (°C) |
| `charge_duration_s` | length of charge phase (s) |
| `discharge_duration_s` | length of discharge phase (s) |
| `capacity` | measured discharge capacity (Ah) |
| `soh` | capacity / nominal_capacity (0–1) |

`soh` is what the regression models predict.
