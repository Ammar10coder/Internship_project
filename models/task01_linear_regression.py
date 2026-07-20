"""
Task 01 - House Price Prediction (Linear Regression)
Prodigy InfoTech ML Internship

Works both as:
1. Standalone Python script
2. Flask backend module
"""

import argparse
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error
import joblib

COLUMN_ALIASES = {
    "sqft": ["sqft", "grlivarea", "square_feet", "squarefootage"],
    "bedrooms": ["bedrooms", "bedroomabvgr", "beds"],
    "bathrooms": ["bathrooms", "fullbath", "baths"],
    "price": ["price", "saleprice"],
}


def _find_column(df: pd.DataFrame, aliases):
    lower_map = {c.lower(): c for c in df.columns}
    for alias in aliases:
        if alias in lower_map:
            return lower_map[alias]
    return None


def load_dataset(path=None, n=120, seed=42):
    """
    Loads a real housing dataset if supplied,
    otherwise generates a synthetic dataset.
    """

    if path:

        raw = pd.read_csv(path)

        cols = {}

        for key, aliases in COLUMN_ALIASES.items():

            found = _find_column(raw, aliases)

            if found is None:
                raise ValueError(
                    f"Could not find column '{key}' in dataset."
                )

            cols[key] = found

        df = raw[
            [
                cols["sqft"],
                cols["bedrooms"],
                cols["bathrooms"],
                cols["price"],
            ]
        ].copy()

        df.columns = [
            "sqft",
            "bedrooms",
            "bathrooms",
            "price",
        ]

        return df.dropna()

    rng = np.random.default_rng(seed)

    sqft = 600 + rng.random(n) * 4200

    beds = np.maximum(
        1,
        np.round(sqft / 750 + rng.normal(0, 0.6, n)),
    )

    baths = np.maximum(
        1,
        np.round(beds * 0.75 + rng.normal(0, 0.4, n)),
    )

    price = (
        25000
        + sqft * 118
        + beds * 9000
        + baths * 14000
        + rng.normal(0, 18000, n)
    )

    return pd.DataFrame(
        {
            "sqft": sqft,
            "bedrooms": beds,
            "bathrooms": baths,
            "price": price,
        }
    )


def train_model(df, test_size=0.2, seed=42):

    X = df[
        [
            "sqft",
            "bedrooms",
            "bathrooms",
        ]
    ]

    y = df["price"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=seed,
    )

    model = LinearRegression()

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    metrics = {
        "r2_train": model.score(X_train, y_train),
        "r2_test": r2_score(y_test, y_pred),
        "mae_test": mean_absolute_error(y_test, y_pred),
    }

    return model, metrics


def predict(model, sqft, bedrooms, bathrooms):

    sample = pd.DataFrame(
        [
            [
                sqft,
                bedrooms,
                bathrooms,
            ]
        ],
        columns=[
            "sqft",
            "bedrooms",
            "bathrooms",
        ],
    )

    return float(model.predict(sample)[0])


# ==================================================
# FLASK SUPPORT
# ==================================================

# Train the model once when Flask imports this file
_dataset = load_dataset()

_model, _metrics = train_model(_dataset)


def predict_house_price(sqft, bedrooms, bathrooms):
    """
    Used by Flask app.
    """

    return round(
        predict(
            _model,
            sqft,
            bedrooms,
            bathrooms,
        ),
        2,
    )


# ==================================================
# COMMAND LINE EXECUTION
# ==================================================

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--data", default=None)

    parser.add_argument("--sqft", type=float, default=1800)

    parser.add_argument("--beds", type=int, default=3)

    parser.add_argument("--baths", type=int, default=2)

    parser.add_argument(
        "--save-model",
        default=None,
    )

    args = parser.parse_args()

    df = load_dataset(args.data)

    model, metrics = train_model(df)

    print("\nModel Trained Successfully\n")

    print(f"Training Samples : {len(df)}")

    print(f"Train R² : {metrics['r2_train']:.3f}")

    print(f"Test R²  : {metrics['r2_test']:.3f}")

    print(f"MAE      : ${metrics['mae_test']:,.2f}")

    price = predict(
        model,
        args.sqft,
        args.beds,
        args.baths,
    )

    print(
        f"\nPredicted Price : ${price:,.2f}"
    )

    if args.save_model:

        joblib.dump(
            model,
            args.save_model,
        )

        print(
            f"\nModel saved to {args.save_model}"
        )


if __name__ == "__main__":
    main()