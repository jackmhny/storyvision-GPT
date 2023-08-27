from generate import generate
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)


@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        story_idea = request.form["story_idea"]
        location = generate(story_idea)
        return redirect(url_for("index", result=location))
    result = request.args.get("result")
    return render_template("index.html", result=result)
