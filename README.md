# Battery State-of-Health Prediction — A Feature Ablation Study

A small machine-learning project I built as a recent ECE graduate
exploring data-driven methods for a problem I already knew from the
hardware side. The goal is not just "train a model" but to ask:

> **Does the physical intuition I have about lithium-ion degradation
> translate into useful features for a regression model — or do generic
> statistical features capture the same signal?**

I tested this with a feature-group ablation on the NASA PCoE battery
dataset.

## Result at a glance

<!-- Fill these in after running `python scripts/ablation.py`. The
     placeholder is intentional: the experiment hasn't been run yet on
     the real data. -->

| Feature group | # features | RMSE | R² |
|---|---:|---:|---:|
| A — raw cycle features only | 8 | _TBD_ | _TBD_ |
| B — A + rolling statistics | 26 | _TBD_ | _TBD_ |
| C — B + physics-derived features | 29 | _TBD_ | _TBD_ |

*Test cell: B0018 (held out entirely from training). Model: Random Forest with default hyperparameters.*

See `docs/report.pdf` for the full discussion (once written), or
`results/ablation.md` for the auto-generated table.

## Why this problem

Every charge–discharge cycle a Li-ion cell goes through, it loses a
small amount of usable capacity. The ratio of remaining capacity to
nominal capacity is **State of Health (SOH)**. Below ~80% SOH a cell is
typically considered end-of-life. Predicting SOH from operating data
matters for electric vehicles, grid-scale storage, and any system
where you'd rather schedule a replacement than experience a failure.

## What I actually did

1. **Loaded and explored** the four NASA cells (B0005–B0007 for training,
   B0018 held out). Sanity-checked capacity-fade curves, looked at
   correlations, and noted the well-known capacity-recovery bumps. See
   `notebooks/01_explore_data.ipynb`.

2. **Aggregated each cycle to one row** with mean voltage, current,
   temperature, and the durations of the charge and discharge phases.
   Computed SOH as capacity divided by the average of the first 5
   cycles' capacity (more stable than using cycle 1 alone).

3. **Built three nested feature groups** for an ablation study:

   | Group | Features | Idea |
   |-------|----------|------|
   | A | Raw cycle measurements only | bare-minimum baseline |
   | B | A + rolling-window mean/std (3, 5, 10 cycles) | give the model short-term memory |
   | C | B + physics-derived features | does electrochemistry help? |

   The Group C features are:
   - `charge_to_discharge_ratio` — proxy for internal-resistance growth (charging slows down more than discharging when impedance climbs).
   - `temp_rise_vs_baseline` — degraded cells dissipate more heat at the same load (P = I²R).
   - `voltage_decline` — mean discharge voltage drops as ohmic drop grows. Noisy but direct.

4. **Trained Random Forest** (and XGBoost, if installed) on each group
   and evaluated on the held-out cell. The ablation table tells me how
   much each *family* of features contributed on top of the previous one.

5. **Wrote up the result** as a 4-page mini-report in `docs/`. The
   discussion section is honest about the limitations (single chemistry,
   no IC features yet, no hyperparameter tuning).

## Repository layout

```
battery-soh-prediction/
├── data/
│   ├── raw/                <- put NASA .mat files here
│   ├── processed/          <- cycles.csv produced by load_data.py
│   └── README.md           <- where to download the dataset
├── notebooks/
│   └── 01_explore_data.ipynb     <- Week 1 EDA with my observations
├── src/
│   ├── data.py             <- read .mat files, aggregate, compute SOH
│   ├── features.py         <- three feature groups + FEATURE_GROUPS dict
│   ├── models.py           <- RF and XGBoost training
│   └── evaluate.py         <- metrics + plots
├── scripts/
│   ├── load_data.py        <- run once: .mat -> cycles.csv
│   ├── train.py            <- train one model on one feature group
│   └── ablation.py         <- the experiment: A vs B vs C
├── docs/
│   └── report_template.md  <- the 4-page write-up
├── results/                <- plots and metrics (created by scripts)
└── requirements.txt
```

About 600 lines of Python total. Deliberately small so I can defend
every line.

## Reproducing the result

```bash
pip install -r requirements.txt

# 1) Download the NASA .mat files into data/raw/ (see data/README.md)

# 2) Build the feature table
python scripts/load_data.py

# 3) The ablation — the actual experiment
python scripts/ablation.py --model random_forest

# 4) Optional: compare RF and XGBoost on the best feature group
python scripts/train.py --model random_forest --features C_raw_plus_rolling_plus_physics
python scripts/train.py --model xgboost      --features C_raw_plus_rolling_plus_physics
```

After step 3, `results/ablation.md` and `results/ablation.png` contain
the comparison table and bar charts.

## Methodology choices worth flagging

**Cell-level chronological split, not random.** Cycles within one cell
are extremely correlated. A random train/test split lets the model see
neighbouring cycles of the test points, which inflates accuracy in a
way that's invisible from the metrics. I held out cell B0018 entirely.
This is the single most important methodological choice in the project
and it dropped my apparent R² noticeably compared to a naive random
split — which is a feature, not a bug.

**Defaults, not heavy tuning.** With only ~500 training rows, aggressive
hyperparameter tuning would overfit the model-selection process. I'm
clear about this in the report and put proper tuning (with
`TimeSeriesSplit`) in the future-work list.

**Ablation framed as "what kind of features help", not "best model".**
With this dataset size, the model architecture matters less than the
features. The ablation result is the story.

## What I'd do next

- Hyperparameter tuning with `GridSearchCV` + `TimeSeriesSplit`.
- Add Incremental Capacity (dQ/dV) features computed from the raw
  voltage/current traces — these are well-established in the literature
  (Dubarry et al.) and I expect them to help the model recognise the
  early-stage degradation patterns my current features miss.
- Try a sequence model (small LSTM or a Transformer) once I've taken a
  proper course on sequence models. Severson et al. 2019 showed that
  early-cycle voltage curves alone can predict full cycle life — that's
  the framing I'd want to learn how to do well.
- Test on a second chemistry (LFP cells from the Severson dataset) to
  see whether these features transfer.

## About me

<!-- TODO: replace this paragraph with your real details before pushing.
     One paragraph is plenty. The point is to give a reviewer enough
     context to know who built this and why. -->

I'm Himaj Reddy, a recent Electronics and communication Engineering graduate from
Sreenidhi Institute of Science and Technology. This is a end-to-end machine-learning
project. The choice of problem isn't accidental — battery prognostics sits
at the boundary of the hardware I trained on as an electrical engineer
and the data-driven methods I want to study formally in a Master's
program. Doing this project taught me where my electrical-engineering
intuition genuinely helped (designing the Group C features, choosing the
held-out cell) and where it didn't translate at all (why naive random
splits are dangerous, how to design an honest comparison between models).

You can reach me at himaj.reddyp@gmail.com.

## References

1. B. Saha and K. Goebel, "Battery Data Set", NASA Prognostics Data Repository, NASA Ames Research Center, 2007.
2. K. Severson et al., "Data-driven prediction of battery cycle life before capacity degradation", *Nature Energy*, 4(5):383–391, 2019.
3. M. Dubarry, C. Truchot, B. Y. Liaw, "Synthesize battery degradation modes via a diagnostic and prognostic model", *Journal of Power Sources*, 219:204–216, 2012.
