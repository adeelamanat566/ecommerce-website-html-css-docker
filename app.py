from flask import Flask, render_template, request
import mysql.connector

app = Flask(__name__)


def get_db_connection():
    return mysql.connector.connect(
        host="db",
        user="myuser",
        password="mypassword",
        database="mydatabase"
    )


@app.route("/", methods=["GET", "POST"])
def home():
    message = None

    if request.method == "POST":
        name = request.form.get("name")

        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute(
            "INSERT INTO users (name) VALUES (%s)",
            (name,)
        )

        db.commit()

        cursor.close()
        db.close()

        message = f"Hello, {name}! Your name has been saved."

    return render_template("index.html", message=message)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)