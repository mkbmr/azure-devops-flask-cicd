from flask import Flask, redirect, render_template, request, url_for

# from datetime import datetime

app = Flask(__name__)
app.config["DEBUG"] = True


@app.route("/")
def index():
    return redirect(url_for("home"))


@app.route("/home")
def home():
    go here =
    return render_template("home.html")


@app.route("/projects")
def projects():
    return render_template("projects.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
