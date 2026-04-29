# [Project title — write your own]
*Predicting Lithium-Ion Battery State of Health from Cycle-Level Data*

**Author:** [Your name] · [Month Year]
**Code:** [link to your GitHub repo]

---

> **How to use this template.** This is the structure for your write-up.
> Each section header has a target length and prompts for what to put in.
> Total length should land around 4 pages (≈ 1500–1800 words) when
> exported to PDF. Delete every italicised prompt before submitting.
> Replace bracketed placeholders like `[XX]` with your real numbers from
> `results/`.

---

## 1. Introduction (½ page)

*Open with the practical problem. Two or three sentences on why battery
SOH prediction matters (electric vehicles, grid storage, consumer
electronics — pick the angle you find most interesting).*

*Then state your research question explicitly. The one this project
answers is something like:*

> *"How well can a tree-based regression model predict Li-ion battery
> SOH from cycle-level features, and how much does each family of
> features (raw measurements, rolling statistics, physics-derived)
> contribute to that prediction?"*

*Close with one sentence on what you found, in plain English. The
ablation table from `results/ablation.md` is what makes this sentence
non-trivial.*

## 2. Dataset and method (1 page)

### 2.1 Dataset

*Three sentences on the NASA PCoE dataset: what cells, what test
conditions, how many cycles. Cite Saha & Goebel 2007.*

### 2.2 Labelling

*State of Health = capacity / nominal capacity. Explain why you used
the mean of the first 5 cycles for the nominal capacity instead of just
cycle 1.*

### 2.3 Train/test split

*The most important methodological choice in this project. Explain that
you split by cell, not by cycle, and held out B0018 entirely. Explain
why a random split would inflate the metrics — cycles within a single
cell are highly correlated, so a random split essentially lets the model
memorise neighbours of test points.*

### 2.4 Features

*One short paragraph on each of the three feature groups. The point of
this section is for the reader to understand the feature groups well
enough that the ablation in Section 3 makes sense.*

- *Group A — raw cycle features:* what they are, why they're the obvious starting point.
- *Group B — A + rolling statistics:* why rolling windows help (single-cycle noise, short-term memory).
- *Group C — B + physics-derived features:* enumerate `charge_to_discharge_ratio`, `temp_rise_vs_baseline`, `voltage_decline`. For each, give the one-sentence electrochemistry justification (you have the citations from Severson et al. and Dubarry et al. — use them).

### 2.5 Models

*Random Forest and XGBoost, with the hyperparameters you used. Mention
that you didn't do hyperparameter tuning and explain why this is
honest (small dataset, exploratory study) rather than lazy. Tuning is
in future work.*

## 3. Experiments and results (1½ pages)

### 3.1 Ablation study

*This is the centrepiece. Paste the table from `results/ablation.md`
and the figure from `results/ablation.png`. Then write 2–3 paragraphs
interpreting the numbers:*

- *What's the delta from A to B? What does that say about how much
  short-term memory helps?*
- *What's the delta from B to C? Did your physics features add anything
  on top of generic statistics — yes or no? Either answer is interesting
  if you explain why.*
- *Look at the feature-importance plot for the best model
  (`results/random_forest__C_..._feature_importance.png`). Which features
  ended up mattering most? Was it what you expected from the EDA?*

### 3.2 Random Forest vs XGBoost

*Run `python scripts/train.py --model xgboost --features <best_group>`
and compare against the RF row in your ablation. One paragraph: did
boosting help, and is the difference meaningful given that there's no
hyperparameter tuning on either side?*

### 3.3 Where the model gets it wrong

*Look at the predicted-vs-actual plot for your best model. The interesting
errors usually cluster in one region of SOH (commonly: near the knee
where the held-out cell starts fading rapidly). Describe what you see.
Suggest one concrete reason — for example, the model has only seen the
training cells' knees, which sit at different cycle counts than B0018's.*

## 4. Discussion and limitations (½ page)

*Be specific. Avoid the generic "this is just a small dataset" line.
Better limitations to mention, with one sentence each:*

- *Single chemistry. NASA cells are NMC; LFP cells degrade differently.*
- *Capacity-recovery effect (the bumps you saw in the EDA) isn't modeled
  — the cycle-aggregated features don't capture rest-time information.*
- *No incremental capacity (dQ/dV) features. These are well-established
  in the literature (Dubarry et al.) and would be a natural addition.*
- *Hyperparameters not tuned. So the RF-vs-XGBoost comparison should be
  read as "with default settings", not as a definitive ranking.*

## 5. What I'd do next (½ page)

*Three or four concrete extensions. Each should be specific enough that
a reader can imagine the experiment.*

- *Hyperparameter tuning with `GridSearchCV` and a `TimeSeriesSplit`,
  reporting both the tuned numbers and the search space.*
- *Add IC features: compute `dQ/dV` curves from the raw voltage/current
  traces during charging, extract peak height and area as features, and
  re-run the ablation with a Group D.*
- *Try a sequence model. SOH evolves smoothly over cycles, so an LSTM
  fed a window of the last K cycles should beat the per-cycle tabular
  models. Severson et al. 2019 used exactly this kind of sequence framing.*
- *Test on a second chemistry. The Toyota/Stanford LFP dataset
  (Severson et al.) is a natural follow-up — same problem, different
  cell chemistry, would tell us how transferable these features are.*

## References

*Three is enough. Keep them tight.*

1. B. Saha and K. Goebel, "Battery Data Set", NASA Prognostics Data Repository, NASA Ames Research Center, 2007.
2. K. Severson et al., "Data-driven prediction of battery cycle life before capacity degradation", *Nature Energy*, 4(5):383–391, 2019.
3. M. Dubarry, C. Truchot, B. Y. Liaw, "Synthesize battery degradation modes via a diagnostic and prognostic model", *Journal of Power Sources*, 219:204–216, 2012.
