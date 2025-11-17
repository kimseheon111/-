from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

# =========================
# DB 연결
# =========================
def get_db():
    conn = sqlite3.connect("data.db")
    conn.row_factory = sqlite3.Row
    return conn

# =========================
# DB 초기 생성
# =========================
with get_db() as db:
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            nickname TEXT,
            is_admin INTEGER DEFAULT 0
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time TEXT,
            username TEXT,
            nickname TEXT,
            item TEXT
        )
    """)
    db.commit()


# =========================
# 로그인 API
# =========================
@app.post("/login")
def login():
    data = request.json
    username = data["username"]
    password = data["password"]

    with get_db() as db:
        user = db.execute("SELECT * FROM users WHERE username=? AND password=?",
                          (username, password)).fetchone()
        if user:
            return jsonify({"success": True, "is_admin": user["is_admin"]})
        return jsonify({"success": False})


# =========================
# 회원가입 / 관리자 추가
# =========================
@app.post("/join")
def join():
    data = request.json
    username = data["username"]
    password = data["password"]
    nickname = data["nickname"]
    is_admin = int(data.get("is_admin", 0))

    try:
        with get_db() as db:
            db.execute(
                "INSERT INTO users (username, password, nickname, is_admin) VALUES (?, ?, ?, ?)",
                (username, password, nickname, is_admin)
            )
            db.commit()
        return jsonify({"success": True})
    except:
        return jsonify({"success": False})


# =========================
# 기록 추가
# =========================
@app.post("/add_record")
def add_record():
    data = request.json
    username = data["username"]
    nickname = data["nickname"]
    item = data["item"]
    now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with get_db() as db:
        db.execute(
            "INSERT INTO records (time, username, nickname, item) VALUES (?, ?, ?, ?)",
            (now_time, username, nickname, item)
        )
        db.commit()

    return jsonify({"success": True})


# =========================
# 기록 조회
# =========================
@app.get("/get_records")
def get_records():
    with get_db() as db:
        rows = db.execute("SELECT * FROM records ORDER BY id DESC").fetchall()
        return jsonify([dict(row) for row in rows])


# =========================
# 관리자 — 기록 삭제
# =========================
@app.post("/delete_record")
def delete_record():
    data = request.json
    record_id = data["id"]

    with get_db() as db:
        db.execute("DELETE FROM records WHERE id=?", (record_id,))
        db.commit()

    return jsonify({"success": True})


# =========================
# 실행
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
