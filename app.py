
from flask import Flask, render_template, request, jsonify
import mysql.connector

app = Flask(__name__)


# ==========================================
# DATABASE CONNECTION
# DO NOT CHANGE
# ==========================================

def get_db_connection():
    return mysql.connector.connect(
        host="test",
        user="ROOT",
        password="adeel",
        database="databse"
    )


# ==========================================
# HOME
# ==========================================

@app.route("/")
def home():
    return render_template("index.html")


# ==========================================
# PRODUCTS
# ==========================================

@app.route("/api/products", methods=["GET"])
def get_products():

    search = request.args.get("search", "").strip()
    category = request.args.get("category", "").strip()
    sort = request.args.get("sort", "latest").strip()
    deal = request.args.get("deal", "").strip().lower()

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        query = """
            SELECT
                id,
                name,
                description,
                price,
                category,
                icon,
                created_at
            FROM products
            WHERE 1=1
        """

        values = []

        if search:
            query += """
                AND (
                    name LIKE %s
                    OR description LIKE %s
                    OR category LIKE %s
                )
            """

            search_value = f"%{search}%"

            values.extend([
                search_value,
                search_value,
                search_value
            ])

        if category:
            query += " AND category = %s"
            values.append(category)

        if deal == "true":
            query += " AND price < 100"

        if sort == "price_low":
            query += " ORDER BY price ASC"

        elif sort == "price_high":
            query += " ORDER BY price DESC"

        elif sort == "name":
            query += " ORDER BY name ASC"

        else:
            query += " ORDER BY id DESC"

        cursor.execute(query, values)

        products = cursor.fetchall()

        return jsonify(products)

    finally:

        cursor.close()
        connection.close()


@app.route("/api/products/<int:product_id>", methods=["GET"])
def get_product(product_id):

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT
                id,
                name,
                description,
                price,
                category,
                icon,
                created_at
            FROM products
            WHERE id = %s
            """,
            (product_id,)
        )

        product = cursor.fetchone()

        if not product:
            return jsonify({
                "error": "Product not found"
            }), 404

        return jsonify(product)

    finally:

        cursor.close()
        connection.close()


# ==========================================
# CART
# ==========================================

@app.route("/api/cart", methods=["POST"])
def add_to_cart():

    data = request.get_json(silent=True) or {}

    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)

    if not product_id:
        return jsonify({
            "error": "Product ID is required"
        }), 400

    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        return jsonify({
            "error": "Quantity must be a number"
        }), 400

    if quantity < 1:
        return jsonify({
            "error": "Quantity must be at least 1"
        }), 400

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        cursor.execute(
            "SELECT id FROM products WHERE id = %s",
            (product_id,)
        )

        product = cursor.fetchone()

        if not product:
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

        return jsonify({
            "message": "Product added to cart"
        }), 201

    finally:

        cursor.close()
        connection.close()


@app.route("/api/cart", methods=["GET"])
def get_cart():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT
                c.id,
                c.product_id,
                c.quantity,
                p.name,
                p.price,
                p.icon
            FROM cart_items c
            INNER JOIN products p
                ON c.product_id = p.id
            ORDER BY c.id DESC
            """
        )

        items = cursor.fetchall()

        return jsonify(items)

    finally:

        cursor.close()
        connection.close()


@app.route("/api/cart/<int:item_id>", methods=["DELETE"])
def delete_cart_item(item_id):

    connection = get_db_connection()
    cursor = connection.cursor()

    try:

        cursor.execute(
            "DELETE FROM cart_items WHERE id = %s",
            (item_id,)
        )

        connection.commit()

        return jsonify({
            "message": "Cart item removed"
        })

    finally:

        cursor.close()
        connection.close()


# ==========================================
# NEWSLETTER
# ==========================================

@app.route("/api/subscribe", methods=["POST"])
def subscribe():

    data = request.get_json(silent=True) or {}

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
            INSERT INTO subscribers
            (email)
            VALUES (%s)
            """,
            (email,)
        )

        connection.commit()

        return jsonify({
            "message": "Subscribed successfully"
        }), 201

    except mysql.connector.IntegrityError:

        return jsonify({
            "error": "Email already subscribed"
        }), 409

    finally:

        cursor.close()
        connection.close()


# ==========================================
# CONTACT
# ==========================================

@app.route("/api/contact", methods=["POST"])
def contact():

    data = request.get_json(silent=True) or {}

    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    subject = data.get("subject", "").strip()
    message = data.get("message", "").strip()

    if not name or not email or not subject or not message:
        return jsonify({
            "error": "All contact fields are required"
        }), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO contact_messages
            (name, email, subject, message)
            VALUES (%s, %s, %s, %s)
            """,
            (name, email, subject, message)
        )

        connection.commit()

        return jsonify({
            "message": "Message sent successfully"
        }), 201

    finally:

        cursor.close()
        connection.close()


# ==========================================
# ORDERS
# ==========================================

@app.route("/api/orders", methods=["POST"])
def create_order():

    data = request.get_json(silent=True) or {}

    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    phone = data.get("phone", "").strip()
    city = data.get("city", "").strip()
    address = data.get("address", "").strip()
    items = data.get("items", [])

    if not all([name, email, phone, city, address]):
        return jsonify({
            "error": "All customer details are required"
        }), 400

    if not isinstance(items, list) or not items:
        return jsonify({
            "error": "Cart is empty"
        }), 400

    connection = get_db_connection()

    cursor = connection.cursor(dictionary=True)

    try:

        total = 0
        validated_items = []

        for item in items:

            product_id = item.get("product_id")
            quantity = item.get("quantity", 1)

            try:
                product_id = int(product_id)
                quantity = int(quantity)
            except (TypeError, ValueError):
                connection.rollback()

                return jsonify({
                    "error": "Invalid product or quantity"
                }), 400

            if quantity < 1:
                connection.rollback()

                return jsonify({
                    "error": "Quantity must be at least 1"
                }), 400

            cursor.execute(
                """
                SELECT
                    id,
                    name,
                    price
                FROM products
                WHERE id = %s
                """,
                (product_id,)
            )

            product = cursor.fetchone()

            if not product:
                connection.rollback()

                return jsonify({
                    "error": f"Product {product_id} not found"
                }), 404

            unit_price = float(product["price"])

            item_total = unit_price * quantity

            total += item_total

            validated_items.append({
                "product_id": product["id"],
                "quantity": quantity,
                "unit_price": unit_price
            })

        shipping = 0 if total >= 100 else 8

        grand_total = total + shipping

        cursor.execute(
            """
            INSERT INTO orders
            (
                customer_name,
                email,
                phone,
                city,
                address,
                subtotal,
                shipping,
                total,
                status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                name,
                email,
                phone,
                city,
                address,
                total,
                shipping,
                grand_total,
                "Pending"
            )
        )

        order_id = cursor.lastrowid

        for item in validated_items:

            cursor.execute(
                """
                INSERT INTO order_items
                (
                    order_id,
                    product_id,
                    quantity,
                    unit_price
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    order_id,
                    item["product_id"],
                    item["quantity"],
                    item["unit_price"]
                )
            )

        connection.commit()

        return jsonify({
            "message": "Order placed successfully",
            "order_id": order_id,
            "total": grand_total
        }), 201

    except Exception as error:

        connection.rollback()

        return jsonify({
            "error": str(error)
        }), 500

    finally:

        cursor.close()
        connection.close()


# ==========================================
# HEALTH
# ==========================================

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


# ==========================================
# APP START
# ==========================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=8000,
        debug=False
    )

