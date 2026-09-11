
from flask import Flask, render_template, request, jsonify
import mysql.connector

app = Flask(__name__)


def get_db_connection():
    return mysql.connector.connect(
        host="test",
        user="ROOT",
        password="adeel",
        database="databse"
    )


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/products", methods=["GET"])
def get_products():

    search = request.args.get("search", "").strip()
    category = request.args.get("category", "").strip()

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            id,
            name,
            description,
            price,
            category,
            icon
        FROM products
        WHERE 1=1
    """

    values = []

    if search:
        query += """
            AND (
                name LIKE %s
                OR description LIKE %s
            )
        """

        search_value = f"%{search}%"

        values.append(search_value)
        values.append(search_value)

    if category:
        query += " AND category = %s"
        values.append(category)

    query += " ORDER BY id DESC"

    cursor.execute(query, values)

    products = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(products)


@app.route("/api/cart", methods=["POST"])
def add_to_cart():

    data = request.get_json()

    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)

    if not product_id:
        return jsonify({
            "error": "Product ID is required"
        }), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id FROM products WHERE id = %s",
        (product_id,)
    )

    product = cursor.fetchone()

    if not product:
        cursor.close()
        connection.close()

        return jsonify({
            "error": "Product not found"
        }), 404

    cursor.execute(
        """
        INSERT INTO cart_items
        (product_id, quantity)
        VALUES (%s, %s)
        """,
        (product_id, quantity)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Product added to cart"
    }), 201


@app.route("/api/subscribe", methods=["POST"])
def subscribe():

    data = request.get_json()

    email = data.get("email", "").strip()

    if not email:
        return jsonify({
            "error": "Email is required"
        }), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO subscribers (email)
            VALUES (%s)
            """,
            (email,)
        )

        connection.commit()

    except mysql.connector.IntegrityError:

        cursor.close()
        connection.close()

        return jsonify({
            "error": "Email already subscribed"
        }), 409

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Subscribed successfully"
    }), 201


@app.route("/health", methods=["GET"])
def health():

    try:

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT 1")
        cursor.fetchone()

        cursor.close()
        connection.close()

        return jsonify({
            "status": "healthy",
            "database": "connected"
        })

    except Exception as error:

        return jsonify({
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(error)
        }), 500


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=8000,
        debug=False
    )

