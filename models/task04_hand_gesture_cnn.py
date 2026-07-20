"""
Task 04 - Hand Gesture Recognition (CNN)
Prodigy InfoTech ML Internship

Real TensorFlow/Keras pipeline behind the task-04-hand-gesture.html demo.
The HTML page uses a hand-written skin-segmentation + rule-based classifier
for an offline in-browser demo (it says so explicitly, since it can't
download the LeapGestRecog dataset in a sandboxed browser). This script
trains an actual CNN image classifier.

Expected dataset layout (e.g. the Kaggle "LeapGestRecog" dataset, or your
own photos), one subfolder per gesture class:
    data/
      palm/
        img001.jpg
        ...
      fist/
        img001.jpg
        ...
      peace/
        ...
      thumbs_up/
        ...

Usage:
    python task04_hand_gesture_cnn.py --data-dir data --train
    python task04_hand_gesture_cnn.py --model gesture_cnn.keras --predict path/to/photo.jpg

Requires: pip install tensorflow
"""

import argparse
import os
import numpy as np

IMG_SIZE = 96


def _lazy_import_tf():
    import tensorflow as tf
    return tf


def build_model(num_classes: int, img_size: int = IMG_SIZE):
    tf = _lazy_import_tf()
    from tensorflow.keras import layers, models

    model = models.Sequential([
        layers.Input(shape=(img_size, img_size, 3)),
        layers.Rescaling(1.0 / 255),
        layers.Conv2D(32, 3, activation="relu"),
        layers.MaxPooling2D(),
        layers.Conv2D(64, 3, activation="relu"),
        layers.MaxPooling2D(),
        layers.Conv2D(64, 3, activation="relu"),
        layers.MaxPooling2D(),
        layers.Flatten(),
        layers.Dropout(0.3),
        layers.Dense(128, activation="relu"),
        layers.Dense(num_classes, activation="softmax"),
    ])
    model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    return model


def train(data_dir: str, model_out: str, epochs: int = 12, batch_size: int = 32, seed: int = 42):
    tf = _lazy_import_tf()

    train_ds = tf.keras.utils.image_dataset_from_directory(
        data_dir,
        validation_split=0.2,
        subset="training",
        seed=seed,
        image_size=(IMG_SIZE, IMG_SIZE),
        batch_size=batch_size,
    )
    val_ds = tf.keras.utils.image_dataset_from_directory(
        data_dir,
        validation_split=0.2,
        subset="validation",
        seed=seed,
        image_size=(IMG_SIZE, IMG_SIZE),
        batch_size=batch_size,
    )

    class_names = train_ds.class_names
    print(f"Classes found: {class_names}")

    train_ds = train_ds.prefetch(tf.data.AUTOTUNE)
    val_ds = val_ds.prefetch(tf.data.AUTOTUNE)

    model = build_model(num_classes=len(class_names))
    history = model.fit(train_ds, validation_data=val_ds, epochs=epochs)

    val_acc = history.history["val_accuracy"][-1]
    print(f"Final validation accuracy: {val_acc:.3f}")

    model.save(model_out)
    class_names_path = model_out + ".classes.txt"
    with open(class_names_path, "w") as f:
        f.write("\n".join(class_names))
    print(f"Saved model to {model_out}")
    print(f"Saved class names to {class_names_path}")


def predict(model_path: str, image_path: str):
    tf = _lazy_import_tf()

    model = tf.keras.models.load_model(model_path)
    class_names_path = model_path + ".classes.txt"
    if os.path.exists(class_names_path):
        with open(class_names_path) as f:
            class_names = [line.strip() for line in f if line.strip()]
    else:
        class_names = [f"class_{i}" for i in range(model.output_shape[-1])]

    img = tf.keras.utils.load_img(image_path, target_size=(IMG_SIZE, IMG_SIZE))
    arr = tf.keras.utils.img_to_array(img)
    arr = np.expand_dims(arr, axis=0)

    probs = model.predict(arr, verbose=0)[0]
    best_idx = int(np.argmax(probs))

    print(f"Prediction: {class_names[best_idx]} ({probs[best_idx] * 100:.1f}% confidence)")
    for name, p in sorted(zip(class_names, probs), key=lambda t: -t[1]):
        print(f"  {name:12s}: {p * 100:5.1f}%")


def main():
    parser = argparse.ArgumentParser(description="Task 04 - Hand gesture recognition CNN")
    parser.add_argument("--data-dir", type=str, default="data", help="Folder with one subfolder per gesture class")
    parser.add_argument("--model", type=str, default="gesture_cnn.keras")
    parser.add_argument("--epochs", type=int, default=12)
    parser.add_argument("--train", action="store_true")
    parser.add_argument("--predict", type=str, default=None, help="Path to a hand photo to classify")
    args = parser.parse_args()

    if args.train:
        train(args.data_dir, args.model, epochs=args.epochs)
    elif args.predict:
        predict(args.model, args.predict)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()