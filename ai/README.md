# VAYUNEXA AI Pipeline

This directory contains the machine-learning pipeline for the
VAYUNEXA energy-forecasting system.

The trained model will eventually be consumed by the FastAPI backend
forecast endpoints.

## Planned pipeline

```text
Telemetry + Weather
        ↓
Dataset generation
        ↓
Feature engineering
        ↓
Model training
        ↓
Evaluation
        ↓
Saved XGBoost model
        ↓
Backend forecast service
