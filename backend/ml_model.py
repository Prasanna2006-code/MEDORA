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
        f"Dataset not found:\n{DATASET_PATH}"
    )

df = pd.read_excel(DATASET_PATH)

print("Dataset loaded successfully.")
print("Rows:", len(df))
print("Columns:", len(df.columns))

print("\nColumn names:")
print(df.columns.tolist())


# =========================================================
# FIND TARGET COLUMN
# =========================================================

possible_targets = [
    "Triage Acuity",
    "Triage acuity",
    "Urgency",
    "urgency",
    "Triage",
    "Label",
    "label"
]

target_column = None

for column in possible_targets:
    if column in df.columns:
        target_column = column
        break


if target_column is None:
    raise ValueError(
        "\nCould not find the triage target column.\n"
        "Available columns are:\n"
        + str(df.columns.tolist())
    )


print("\nTarget column:", target_column)


# =========================================================
# SHOW TARGET VALUES
# =========================================================

print("\nTarget values:")

print(
    df[target_column]
    .value_counts(dropna=False)
)


# =========================================================
# REMOVE ROWS WITHOUT TARGET
# =========================================================

df = df.dropna(
    subset=[target_column]
)


# =========================================================
# SEPARATE FEATURES AND TARGET
# =========================================================

X = df.drop(
    columns=[target_column]
)

y = df[target_column]


# =========================================================
# REMOVE COMPLETELY EMPTY COLUMNS
# =========================================================

empty_columns = [
    column
    for column in X.columns
    if X[column].isna().all()
]

if empty_columns:

    print(
        "\nRemoving completely empty columns:"
    )

    print(empty_columns)

    X = X.drop(
        columns=empty_columns
    )


# =========================================================
# IDENTIFY NUMERIC COLUMNS
# =========================================================

numeric_columns = X.select_dtypes(
    include=[
        "int64",
        "int32",
        "float64",
        "float32"
    ]
).columns.tolist()


# =========================================================
# IDENTIFY CATEGORICAL COLUMNS
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
# RANDOM FOREST MODEL
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
# TRAIN RANDOM FOREST
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
    f"\nValidation Accuracy: {accuracy * 100:.2f}%"
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


print("\n===================================")
print("MODEL TRAINED SUCCESSFULLY")
print("===================================")

print(
    "Model saved at:"
)

print(MODEL_PATH)

print("\nYou can now use this model with:")
print("backend/ml_model.py")