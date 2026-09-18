from pathlib import Path

import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATASET_PATH = BASE_DIR / "data" / "dataset.xlsx"

MODEL_DIR = BASE_DIR / "models"
MODEL_DIR.mkdir(exist_ok=True)

MODEL_PATH = MODEL_DIR / "triage_model.joblib"


# =========================================================
# LOAD DATASET
# =========================================================

print("\nLoading dataset...")

if not DATASET_PATH.exists():
    raise FileNotFoundError(
        f"\nDataset not found:\n{DATASET_PATH}"
    )

df = pd.read_excel(DATASET_PATH)

print("Dataset loaded successfully.")
print("Rows:", len(df))
print("Columns:", len(df.columns))


# =========================================================
# DISPLAY COLUMNS
# =========================================================

print("\nColumn names:")

for column in df.columns:
    print("-", column)


# =========================================================
# TARGET COLUMN
# =========================================================

TARGET_COLUMN = "Triage acuity / urgency label"

if TARGET_COLUMN not in df.columns:
    raise ValueError(
        f"\nTarget column not found: {TARGET_COLUMN}"
    )

print("\nTarget column:", TARGET_COLUMN)


# =========================================================
# TARGET VALUES
# =========================================================

print("\nTarget values:")

print(
    df[TARGET_COLUMN].value_counts(
        dropna=False
    )
)


# =========================================================
# REMOVE MISSING TARGET ROWS
# =========================================================

df = df.dropna(
    subset=[TARGET_COLUMN]
)


# =========================================================
# FEATURES AND TARGET
# =========================================================

X = df.drop(
    columns=[TARGET_COLUMN]
)

y = df[TARGET_COLUMN]


# =========================================================
# REMOVE EMPTY COLUMNS
# =========================================================

empty_columns = [
    column
    for column in X.columns
    if X[column].isna().all()
]

if empty_columns:

    print("\nRemoving empty columns:")
    print(empty_columns)

    X = X.drop(
        columns=empty_columns
    )


# =========================================================
# NUMERIC FEATURES
# =========================================================

numeric_columns = X.select_dtypes(
    include=[
        "int64",
        "int32",
        "int16",
        "float64",
        "float32",
        "float16"
    ]
).columns.tolist()


# =========================================================
# CATEGORICAL FEATURES
# =========================================================

categorical_columns = X.select_dtypes(
    include=[
        "object",
        "category",
        "bool"
    ]
).columns.tolist()


print("\nNumeric features:")
print(numeric_columns)

print("\nCategorical features:")
print(categorical_columns)


# =========================================================
# NUMERIC PIPELINE
# =========================================================

numeric_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(
                strategy="median"
            )
        )
    ]
)


# =========================================================
# CATEGORICAL PIPELINE
# =========================================================

categorical_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(
                strategy="most_frequent"
            )
        ),

        (
            "encoder",
            OneHotEncoder(
                handle_unknown="ignore"
            )
        )
    ]
)


# =========================================================
# PREPROCESSOR
# =========================================================

preprocessor = ColumnTransformer(
    transformers=[
        (
            "numeric",
            numeric_pipeline,
            numeric_columns
        ),

        (
            "categorical",
            categorical_pipeline,
            categorical_columns
        )
    ]
)


# =========================================================
# RANDOM FOREST
# =========================================================

random_forest = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    class_weight="balanced",
    n_jobs=-1
)


# =========================================================
# COMPLETE PIPELINE
# =========================================================

pipeline = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor
        ),

        (
            "classifier",
            random_forest
        )
    ]
)


# =========================================================
# TRAIN / TEST SPLIT
# =========================================================

print("\nSplitting dataset...")

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))


# =========================================================
# TRAIN
# =========================================================

print("\nTraining Random Forest...")

pipeline.fit(
    X_train,
    y_train
)

print("Training completed.")


# =========================================================
# PREDICTION
# =========================================================

print("\nTesting model...")

predictions = pipeline.predict(
    X_test
)


# =========================================================
# ACCURACY
# =========================================================

accuracy = accuracy_score(
    y_test,
    predictions
)

print(
    f"\nValidation Accuracy: "
    f"{accuracy * 100:.2f}%"
)


# =========================================================
# CLASSIFICATION REPORT
# =========================================================

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        predictions,
        zero_division=0
    )
)


# =========================================================
# SAVE MODEL
# =========================================================

print("\nSaving model...")

joblib.dump(
    pipeline,
    MODEL_PATH
)


# =========================================================
# COMPLETE
# =========================================================

print("\n======================================")
print("   RANDOM FOREST TRAINING COMPLETE")
print("======================================")

print("\nModel saved at:")
print(MODEL_PATH)