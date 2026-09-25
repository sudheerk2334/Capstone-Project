"""
Titanic analytics and ML pipeline.

Run:
    python analytics/run_analytics.py
"""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "titanic.csv"
MODEL_PATH = BASE_DIR / "full_pipeline.joblib"


def load_data() -> pd.DataFrame:
    return pd.read_csv(CSV_PATH)


def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    # Support either a compact project dataset or the common Titanic column names.
    if "Age" in result:
        result["Age"] = pd.to_numeric(result["Age"], errors="coerce")
    if "Fare" in result:
        result["Fare"] = pd.to_numeric(result["Fare"], errors="coerce")

    if "Sex" in result:
        result["Sex"] = result["Sex"].fillna("unknown").str.lower()

    if "FamilySize" not in result:
        sib = result["SibSp"] if "SibSp" in result else 0
        par = result["Parch"] if "Parch" in result else 0
        result["FamilySize"] = sib.fillna(0) + par.fillna(0) + 1

    return result


def build_pipeline(numeric_features, categorical_features) -> Pipeline:
    numeric_pipe = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_pipe = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    preprocess = ColumnTransformer(
        [
            ("num", numeric_pipe, numeric_features),
            ("cat", categorical_pipe, categorical_features),
        ]
    )

    return Pipeline(
        [
            ("preprocess", preprocess),
            ("classifier", LogisticRegression(max_iter=1000)),
        ]
    )


def main() -> None:
    df = prepare_data(load_data())

    if "Survived" not in df:
        raise ValueError("Dataset must contain a Survived target column.")

    numeric_features = [c for c in ["Pclass", "Age", "SibSp", "Parch", "Fare", "FamilySize"] if c in df]
    categorical_features = [c for c in ["Sex", "Embarked"] if c in df]

    features = numeric_features + categorical_features
    X = df[features]
    y = df["Survived"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    model = build_pipeline(numeric_features, categorical_features)
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)

    joblib.dump(model, MODEL_PATH)

    print(f"Rows: {len(df)}")
    print(f"Survival rate: {df['Survived'].mean():.2%}")
    print(f"Test accuracy: {accuracy:.2%}")
    print("\nClassification report:")
    print(classification_report(y_test, predictions, zero_division=0))
    print(f"\nModel saved to: {MODEL_PATH}")


if __name__ == "__main__":
    main()
