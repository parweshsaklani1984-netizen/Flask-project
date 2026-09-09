import json
import os
from pathlib import Path

from flask import Flask, jsonify, redirect, render_template, request, url_for
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError


BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data.json"
load_dotenv(BASE_DIR / ".env")
load_dotenv(BASE_DIR / "atlas-credentials.env")


def create_app():
    app = Flask(__name__)
    app.config["MONGO_URI"] = os.getenv("MONGO_URI") or os.getenv("MONGODB_URI", "")
    app.config["MONGO_DB_NAME"] = os.getenv("MONGO_DB_NAME", "flask_app")
    app.config["MONGO_COLLECTION_NAME"] = os.getenv("MONGO_COLLECTION_NAME", "submissions")

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.route("/todo", methods=["GET", "POST"])
    def todo():
        form_data = request.form if request.method == "POST" else None
        return render_template(
            "todo.html",
            form_data=form_data,
            submitted=request.method == "POST",
        )

    @app.get("/api")
    def api():
        try:
            with DATA_FILE.open("r", encoding="utf-8") as data_file:
                data = json.load(data_file)
        except (OSError, json.JSONDecodeError):
            return jsonify({"error": "Unable to read API data."}), 500

        return jsonify(data)

    @app.post("/submit")
    def submit():
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()

        if not name or not email or not message:
            return render_template(
                "index.html",
                error="Please complete all fields before submitting.",
                form_data=request.form,
            ), 400

        mongo_uri = app.config["MONGO_URI"]
        if not mongo_uri:
            return render_template(
                "index.html",
                error="MongoDB is not configured. Add MONGO_URI to the .env file and restart the app.",
                form_data=request.form,
            ), 500

        client = None
        try:
            client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
            client.admin.command("ping")
            collection = client[app.config["MONGO_DB_NAME"]][
                app.config["MONGO_COLLECTION_NAME"]
            ]
            collection.insert_one(
                {
                    "name": name,
                    "email": email,
                    "message": message,
                }
            )
        except PyMongoError:
            return render_template(
                "index.html",
                error="Unable to submit your data right now. Please try again.",
                form_data=request.form,
            ), 500
        finally:
            if client is not None:
                client.close()

        return redirect(url_for("success"))

    @app.get("/success")
    def success():
        return render_template("success.html")

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
