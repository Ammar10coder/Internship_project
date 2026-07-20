"""
Task 02 - Customer Segmentation (K-Means Clustering)
Prodigy InfoTech ML Internship

Real scikit-learn pipeline behind the task-02-kmeans-clustering.html demo.
The HTML page implements Lloyd's algorithm by hand in JavaScript for a live
in-browser demo; this script is the actual Python model, including an elbow
plot to justify the choice of k, matching the classic "Mall_Customers.csv"
style dataset (Annual Income, Spending Score).

Usage:
    python task02_kmeans_clustering.py --income 60 --spend 55 --k 5
    python task02_kmeans_clustering.py --data Mall_Customers.csv --income 60 --spend 55 --k 5
    python task02_kmeans_clustering.py --elbow --elbow-out elbow.png

Expected --data CSV columns (case-insensitive, first match wins):
    income  / "annual income (k$)" / annualincome
    spend   / "spending score (1-100)" / spendingscore
"""

import argparse
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


COLUMN_ALIASES = {
    "income": ["income", "annual income (k$)", "annualincome", "annual_income"],
    "spend": ["spend", "spending score (1-100)", "spendingscore", "spending_score"],
}


def _find_column(df: pd.DataFrame, aliases):
    lower_map = {c.lower(): c for c in df.columns}
    for alias in aliases:
        if alias in lower_map:
            return lower_map[alias]
    return None


def load_dataset(path: str = None, n: int = 200, seed: int = 7) -> pd.DataFrame:
    """Load a real Mall_Customers-style CSV, or generate synthetic data
    mirroring the five-blob distribution used in the browser demo."""
    if path:
        raw = pd.read_csv(path)
        cols = {}
        for key, aliases in COLUMN_ALIASES.items():
            found = _find_column(raw, aliases)
            if found is None:
                raise ValueError(f"Could not find a column for '{key}' in {path}")
            cols[key] = found
        df = raw[[cols["income"], cols["spend"]]].copy()
        df.columns = ["income", "spend"]
        return df.dropna()

    rng = np.random.default_rng(seed)
    blobs = [(25, 20), (25, 80), (60, 50), (100, 20), (100, 80)]
    rows = []
    for i in range(n):
        ci, cs = blobs[i % len(blobs)]
        rows.append((rng.normal(ci, 8), rng.normal(cs, 10)))
    return pd.DataFrame(rows, columns=["income", "spend"])


def label_for(centroid) -> dict:
    income, spend = centroid
    if income < 45 and spend < 45:
        return {"name": "Careful Spenders", "desc": "Lower income, low spending."}
    if income < 45 and spend >= 45:
        return {"name": "Aspirational Spenders", "desc": "Lower income, high spending score."}
    if 45 <= income < 80:
        return {"name": "Balanced Shoppers", "desc": "Mid income, moderate spending."}
    if income >= 80 and spend < 45:
        return {"name": "Cautious High Earners", "desc": "High income, low spending."}
    return {"name": "Premium Customers", "desc": "High income and high spending."}


def elbow_plot(df: pd.DataFrame, k_range=range(1, 11), out_path="elbow.png"):
    X = df[["income", "spend"]].values
    inertias = []
    for k in k_range:
        km = KMeans(n_clusters=k, n_init=10, random_state=42)
        km.fit(X)
        inertias.append(km.inertia_)
    plt.figure(figsize=(6, 4))
    plt.plot(list(k_range), inertias, marker="o")
    plt.xlabel("k")
    plt.ylabel("Inertia (within-cluster sum of squares)")
    plt.title("Elbow method for choosing k")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    print(f"Elbow plot saved to {out_path}")
    return inertias


def train_model(df: pd.DataFrame, k: int, seed: int = 42) -> KMeans:
    X = df[["income", "spend"]].values
    model = KMeans(n_clusters=k, n_init=10, random_state=seed)
    model.fit(X)
    return model


def assign_segment(model: KMeans, income: float, spend: float) -> dict:
    cluster = int(model.predict([[income, spend]])[0])
    centroid = model.cluster_centers_[cluster]
    label = label_for(centroid)
    return {"cluster": cluster, "centroid": centroid.tolist(), **label}


def main():
    parser = argparse.ArgumentParser(description="Task 02 - Customer segmentation with K-means")
    parser.add_argument("--data", type=str, default=None, help="Path to a customers CSV (optional)")
    parser.add_argument("--income", type=float, default=60)
    parser.add_argument("--spend", type=float, default=55)
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--elbow", action="store_true", help="Also produce an elbow plot")
    parser.add_argument("--elbow-out", type=str, default="elbow.png")
    args = parser.parse_args()

    df = load_dataset(args.data)
    print(f"Loaded {len(df)} customers")

    if args.elbow:
        elbow_plot(df, out_path=args.elbow_out)

    model = train_model(df, args.k)
    print(f"Fitted k-means with k={args.k}, inertia={model.inertia_:,.1f}")

    result = assign_segment(model, args.income, args.spend)
    print()
    print(f"New customer (income={args.income}, spend={args.spend}) "
          f"-> cluster {result['cluster']}: {result['name']}")
    print(f"  {result['desc']}")


# =====================================================
# FLASK SUPPORT
# =====================================================

# Train the model once when Flask imports this module
_dataset = load_dataset()
_model = train_model(_dataset, k=5)

def predict_customer_segment(income, spend):
    """
    Predict the customer segment for the Flask web app.
    """
    return assign_segment(_model, income, spend)


# =====================================================
# COMMAND LINE
# =====================================================

if __name__ == "__main__":
    main()