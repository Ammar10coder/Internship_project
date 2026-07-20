from flask import Flask, render_template, request

from models.task01_linear_regression import predict_house_price
from models.task02_kmeans_clustering import predict_customer_segment
from werkzeug.utils import secure_filename
import os

from models.task03_svm_cats_dogs import predict_image

app = Flask(__name__)


# ==========================
# HOME
# ==========================

@app.route("/")
def home():
    return render_template("index.html")


# ==========================
# TASK 1
# ==========================

@app.route("/task1", methods=["GET", "POST"])
def task1():

    prediction = None

    if request.method == "POST":

        sqft = float(request.form["sqft"])
        bedrooms = int(request.form["bedrooms"])
        bathrooms = int(request.form["bathrooms"])

        prediction = predict_house_price(
            sqft,
            bedrooms,
            bathrooms
        )

    return render_template(
        "task-01-linear-regression.html",
        prediction=prediction
    )


# ==========================
# TASK 2
# ==========================

@app.route("/task2", methods=["GET", "POST"])
def task2():

    result = None

    if request.method == "POST":

        income = float(request.form["income"])
        spend = float(request.form["spend"])

        result = predict_customer_segment(income, spend)

    return render_template(
        "task-02-kmeans-clustering.html",
        result=result
    )
# ==========================
# TASK 3
# ==========================

@app.route("/task3", methods=["GET", "POST"])
def task3():

    result = None

    if request.method == "POST":

        file = request.files["image"]

        if file.filename != "":

            filename = secure_filename(file.filename)

            filepath = os.path.join("uploads", filename)

            file.save(filepath)

            result = predict_image(
                "svm_cats_dogs.joblib",
                filepath
            )

    return render_template(
        "task-03-svm-cats-dogs.html",
        result=result
    )

# ==========================
# TASK 4
# ==========================

@app.route("/task4")
def task4():
    return render_template("task-04-hand-gesture.html")


if __name__ == "__main__":
    app.run(debug=True)