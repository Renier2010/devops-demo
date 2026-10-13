import os
import psycopg2
from flask import Flask, jsonify, request

app = Flask(__name__)


def get_conn():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "db"),
        dbname=os.environ.get("DB_NAME", "todos"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASSWORD", "secret"),
    )


def query(sql, params=None, fetch=False):
    conn = get_conn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute(
                "CREATE TABLE IF NOT EXISTS todos "
                "(id serial PRIMARY KEY, title text NOT NULL)"
            )
            cur.execute(sql, params)
            return cur.fetchall() if fetch else None
    finally:
        conn.close()


@app.route("/")
def home():
    return jsonify(message=os.environ.get("MESSAGE", "Hello from my DevOps demo"))


@app.route("/health")
def health():
    return jsonify(status="ok")


@app.route("/todos", methods=["GET"])
def list_todos():
    rows = query("SELECT id, title FROM todos ORDER BY id", fetch=True)
    return jsonify([{"id": r[0], "title": r[1]} for r in rows])


@app.route("/todos", methods=["POST"])
def add_todo():
    data = request.get_json(silent=True) or {}
    title = data.get("title")
    if not title:
        return jsonify(error="title is required"), 400
    query("INSERT INTO todos (title) VALUES (%s)", (title,))
    return jsonify(title=title), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))


