
import argparse
import glob
import os
import numpy as np
import cv2
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, accuracy_score
import joblib

IMG_SIZE = 64
CLASSES = ["cat", "dog"]


def extract_hog_features(image_path: str) -> np.ndarray:
    """Load an image, resize it, and extract a HOG feature vector."""
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image: {image_path}")
    img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    hog = cv2.HOGDescriptor(
        _winSize=(IMG_SIZE, IMG_SIZE),
        _blockSize=(16, 16),
        _blockStride=(8, 8),
        _cellSize=(8, 8),
        _nbins=9,
    )
    features = hog.compute(gray)
    return features.flatten()


def load_dataset(data_dir: str):
    X, y = [], []
    for label, class_name in enumerate(CLASSES):
        pattern = os.path.join(data_dir, f"{class_name}*", "*")
        # support either data/cats/*.jpg or data/cat*.jpg flat layouts
        paths = glob.glob(pattern) + glob.glob(os.path.join(data_dir, f"{class_name}.*"))
        if not paths:
            paths = glob.glob(os.path.join(data_dir, class_name, "*"))
        for p in paths:
            try:
                X.append(extract_hog_features(p))
                y.append(label)
            except ValueError:
                continue
    if not X:
        raise FileNotFoundError(
            f"No images found under {data_dir}. Expected data/cats/*.jpg and data/dogs/*.jpg"
        )
    return np.array(X), np.array(y)


def train(data_dir: str, model_out: str, test_size: float = 0.2, seed: int = 42):
    print(f"Loading images from {data_dir} ...")
    X, y = load_dataset(data_dir)
    print(f"Loaded {len(X)} images ({(y == 0).sum()} cats, {(y == 1).sum()} dogs)")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, stratify=y, random_state=seed
    )

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    print("Training linear SVM...")
    model = SVC(kernel="linear", C=1.0, probability=True, random_state=seed)
    model.fit(X_train_s, y_train)

    y_pred = model.predict(X_test_s)
    print(f"Test accuracy: {accuracy_score(y_test, y_pred):.3f}")
    print(classification_report(y_test, y_pred, target_names=CLASSES))

    joblib.dump({"model": model, "scaler": scaler}, model_out)
    print(f"Saved trained model + scaler to {model_out}")


def predict(model_path: str, image_path: str):
    bundle = joblib.load(model_path)
    model, scaler = bundle["model"], bundle["scaler"]

    features = extract_hog_features(image_path).reshape(1, -1)
    features_s = scaler.transform(features)

    pred = model.predict(features_s)[0]
    proba = model.predict_proba(features_s)[0]

    print(f"Prediction: {CLASSES[pred]}")
    for cls, p in zip(CLASSES, proba):
        print(f"  {cls}: {p * 100:.1f}%")


def main():
    parser = argparse.ArgumentParser(description="Task 03 - Cats vs Dogs SVM (HOG features)")
    parser.add_argument("--data-dir", type=str, default="data", help="Folder with cats/ and dogs/ subfolders")
    parser.add_argument("--model", type=str, default="svm_cats_dogs.joblib")
    parser.add_argument("--train", action="store_true", help="Train and save a model")
    parser.add_argument("--predict", type=str, default=None, help="Path to an image to classify")
    args = parser.parse_args()

    if args.train:
        train(args.data_dir, args.model)
    elif args.predict:
        predict(args.model, args.predict)
    else:
        parser.print_help()


# =====================================================
# FLASK SUPPORT
# =====================================================

def predict_image(model_path, image_path):

    bundle = joblib.load(model_path)

    model = bundle["model"]
    scaler = bundle["scaler"]

    features = extract_hog_features(image_path).reshape(1, -1)
    features = scaler.transform(features)

    pred = model.predict(features)[0]
    prob = model.predict_proba(features)[0]

    return {
        "label": CLASSES[pred],
        "cat": round(prob[0] * 100, 2),
        "dog": round(prob[1] * 100, 2)
    }


if __name__ == "__main__":
    main()