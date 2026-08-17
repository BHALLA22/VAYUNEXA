from pathlib import Path

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split


# ============================================================
# VAYUNEXA AI MODEL TRAINING
# ============================================================

DATA_PATH = Path(
    "ai/data/training_dataset.csv"
)

MODEL_PATH = Path(
    "ai/models/power_predictor.joblib"
)


# ============================================================
# FEATURES
# ============================================================

FEATURES = [
    "wind_speed",
    "wind_direction",
    "rpm",
    "temperature",
    "humidity",
    "flap_angle",
]

TARGET = "power"


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 60)
print("VAYUNEXA AI MODEL TRAINING")
print("=" * 60)

print(
    f"Loading dataset: {DATA_PATH}"
)

data = pd.read_csv(
    DATA_PATH
)

print(
    f"Samples loaded: {len(data)}"
)


# ============================================================
# PREPARE FEATURES
# ============================================================

X = data[
    FEATURES
]

y = data[
    TARGET
]


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
)


# ============================================================
# MODEL
# ============================================================

model = RandomForestRegressor(
    n_estimators=250,
    max_depth=18,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1,
)


print()
print("Training Random Forest...")

model.fit(
    X_train,
    y_train,
)


# ============================================================
# EVALUATION
# ============================================================

predictions = model.predict(
    X_test
)

mae = mean_absolute_error(
    y_test,
    predictions,
)

r2 = r2_score(
    y_test,
    predictions,
)


print()
print("MODEL PERFORMANCE")
print("-" * 40)

print(
    f"MAE: {mae:.3f} W"
)

print(
    f"R²:  {r2:.4f}"
)


# ============================================================
# SAVE MODEL
# ============================================================

MODEL_PATH.parent.mkdir(
    parents=True,
    exist_ok=True,
)

joblib.dump(
    {
        "model": model,
        "features": FEATURES,
        "target": TARGET,
        "model_version": "vayu-rf-v1",
    },
    MODEL_PATH,
)


print()
print(
    f"Model saved to: {MODEL_PATH}"
)

print("=" * 60)