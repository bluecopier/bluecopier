from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def index() -> str:
    name = "Rosalia"
    return render_template("index.html", title="Welcome", username=name)
