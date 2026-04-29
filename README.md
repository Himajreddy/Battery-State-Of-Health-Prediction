# Battery State of Health Prediction using Machine Learning

## Project Overview

Lithium-ion batteries degrade over time due to repeated charging and discharging cycles. This degradation directly affects battery performance, efficiency, and lifespan.

This project focuses on estimating battery **State of Health (SOH)** using machine learning models trained on battery cycle data.

The objective is to build a predictive system capable of learning degradation patterns from operational battery signals and estimating battery health with high accuracy.

This project combines data engineering, feature extraction, model training, and performance evaluation into a complete applied machine learning workflow.

---

## Problem Context

Battery degradation is one of the most important challenges in modern energy systems.

In applications such as:

* electric vehicles
* renewable energy storage
* portable electronics
* industrial battery systems

accurately monitoring battery health is critical.

Traditional SOH estimation methods often rely on expensive hardware or rule-based systems.

This project demonstrates how machine learning can provide scalable, data-driven battery health estimation.

---

## Project Objective

Build an ML pipeline that:

* predicts battery health degradation
* estimates State of Health continuously
* identifies key degradation features
* benchmarks multiple models
* visualizes prediction quality

---

## Dataset

The dataset contains battery cycle-level operational measurements across multiple charging and discharging cycles.

Each cycle contains electrical and physical indicators such as:

* voltage
* current
* charge capacity
* discharge capacity
* cycle number
* internal resistance

Target:

State of Health (SOH)

SOH is defined as the ratio of current battery capacity to original battery capacity.

---

## Pipeline Architecture

Raw Battery Data
↓
Data Cleaning
↓
Cycle Extraction
↓
Feature Engineering
↓
Feature Grouping
↓
Train/Test Split
↓
Model Training
↓
Performance Evaluation
↓
Feature Importance Analysis
↓
Prediction Visualization

---

## Feature Engineering Strategy

This project uses three feature groups:

### Raw Features

Direct battery operational measurements.

Examples:

* voltage
* current
* capacity

---

### Rolling Statistical Features

Historical behavior summaries.

Examples:

* rolling mean
* rolling standard deviation
* degradation trend

---

### Physics-Inspired Features

Domain-driven battery degradation signals.

Examples:

* resistance growth
* capacity fade rate
* cycle aging indicators

---

## Models Used

The system benchmarks:

* Random Forest Regressor
* XGBoost Regressor

Model selection is based on:

* RMSE
* MAE
* R² score

---

## Results

Best model performance:

R² Score: 0.9318
RMSE: 0.0219
MAE: 0.0173

These results indicate strong predictive capability for battery health estimation.

---

## Key Highlights

### Multi-feature learning

Combines raw, statistical, and domain-driven features.

### Feature ablation

Tests contribution of different feature groups.

### Battery degradation visualization

Shows actual capacity fade behavior.

### Feature importance analysis

Identifies the strongest degradation predictors.

---

## Tech Stack

Language:

Python

Libraries:

* Pandas
* NumPy
* Scikit-learn
* XGBoost
* Matplotlib
* Joblib

---

## Repository Structure

battery-soh/

README.md
requirements.txt

data/
scripts/
src/
models/
results/

src/
├── data.py

├── features.py

├── models.py

├── evaluate.py

scripts/

├── load_data.py

├── train.py

├── ablation.py

---

## Installation

Clone repository:

git clone <repository-url>

Move into project:

cd battery-soh

Create environment:

python -m venv venv

Activate:

venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt

---

## Run Data Preparation

python scripts/load_data.py

---

## Train Model

python scripts/train.py

---

## Run Feature Ablation

python scripts/ablation.py

---

## Why This Project Matters

Battery intelligence is essential for:

* electric mobility
* smart grids
* energy optimization
* battery lifecycle management

This system demonstrates how machine learning can improve battery reliability and forecasting.

---

## Future Improvements

* LSTM-based SOH forecasting
* Transformer-based sequence modeling
* real-time BMS integration
* battery anomaly detection

---

## Author

Himaj Reddy

Machine Learning | Energy AI | Predictive Systems
