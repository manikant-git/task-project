from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import psycopg2.extras
import os
import time

app = Flask(__name__)
CORS(app)

# ──────────────────────────────────────────────
# Database connection
# ──────────────────────────────────────────────
def get_db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "taskflow"),
        user=os.getenv("DB_USER", "taskuser"),
        password=os.getenv("DB_PASSWORD", "taskpass")
    )

def init_db():
    """Create tables if they don't exist."""
    for attempt in range(10):
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id          SERIAL PRIMARY KEY,
                    title       VARCHAR(255) NOT NULL,
                    description TEXT,
                    priority    VARCHAR(10)  DEFAULT 'medium'
                                CHECK (priority IN ('low','medium','high')),
                    status      VARCHAR(10)  DEFAULT 'pending'
                                CHECK (status  IN ('pending','done')),
                    created_at  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
            cur.close()
            conn.close()
            print("✅  Database initialised successfully.")
            return
        except psycopg2.OperationalError as e:
            print(f"⏳  DB not ready (attempt {attempt+1}/10): {e}")
            time.sleep(3)
    raise RuntimeError("Could not connect to the database after 10 attempts.")

# ──────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "taskflow-api"})


@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM tasks ORDER BY created_at DESC;")
    tasks = cur.fetchall()
    cur.close(); conn.close()
    # Convert datetime to string for JSON
    for t in tasks:
        t["created_at"] = t["created_at"].isoformat()
    return jsonify(list(tasks))


@app.route("/api/tasks", methods=["POST"])
def create_task():
    data = request.get_json()
    title       = data.get("title", "").strip()
    description = data.get("description", "").strip()
    priority    = data.get("priority", "medium")

    if not title:
        return jsonify({"error": "title is required"}), 400
    if priority not in ("low", "medium", "high"):
        return jsonify({"error": "priority must be low/medium/high"}), 400

    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        "INSERT INTO tasks (title, description, priority) VALUES (%s, %s, %s) RETURNING *;",
        (title, description, priority)
    )
    task = cur.fetchone()
    conn.commit(); cur.close(); conn.close()
    task["created_at"] = task["created_at"].isoformat()
    return jsonify(dict(task)), 201


@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data   = request.get_json()
    status = data.get("status")

    if status not in ("pending", "done"):
        return jsonify({"error": "status must be pending or done"}), 400

    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        "UPDATE tasks SET status=%s WHERE id=%s RETURNING *;",
        (status, task_id)
    )
    task = cur.fetchone()
    conn.commit(); cur.close(); conn.close()

    if not task:
        return jsonify({"error": "task not found"}), 404
    task["created_at"] = task["created_at"].isoformat()
    return jsonify(dict(task))


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id=%s RETURNING id;", (task_id,))
    deleted = cur.fetchone()
    conn.commit(); cur.close(); conn.close()

    if not deleted:
        return jsonify({"error": "task not found"}), 404
    return jsonify({"message": "Task deleted", "id": task_id})


# ──────────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=False)
