import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/landing")
def landing_page():
    return render_template("landing.html")


@app.route("/meals")
def meals():
    meals = list(mongo.db.meals.find())
    return render_template("meals.html", meals=meals)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}".format(request.form.get("username")))
                return redirect(url_for("profile", username=session["user"]))
            else:
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login.html"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        return render_template("profile.html", username=username)

    return redirect(url_for("login"))


@app.route("/add_meal", methods=["GET", "POST"])
def add_meal():
    if request.method == "POST":
        meal = {
            "meal_category": request.form.get("meal_category"),
            "image_url": request.form.get("image_url"),
            "recipe_name": request.form.get("recipe_name"),
            "recipe_url": request.form.get("recipe_url"),
            "prep_time": request.form.get("prep_time"),
            "cook_time": request.form.get("cook_time"),
            "servings": request.form.get("servings"),
            "ingredients": request.form.get("ingredients"),
            "method": request.form.getlist("method"),
            "created_by": session["user"]
        }

        mongo.db.meals.insert_one(meal)
        flash("Meal Sucessfully Added")
        return redirect(url_for("meals"))

    meal_categories = mongo.db.meal_categories.find().sort("meal_category", 1)
    return render_template("add_meal.html", meal_categories=meal_categories)


@app.route("/edit_meal/<meal_id>", methods=["GET", "POST"])
def edit_meal(meal_id):
    meal = mongo.db.meals.find_one({"_id": ObjectId(meal_id)})
    meal_categories = mongo.db.meal_categories.find().sort("meal_category", 1)
    return render_template(
        "edit_meal.html", meal=meal, meal_categories=meal_categories)


@app.route("/full_recipe/<meal_id>")
def full_recipe(meal_id):
    meal = mongo.db.meals.find_one({"_id": ObjectId(meal_id)})
    return render_template("full_recipe.html", meal=meal)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
