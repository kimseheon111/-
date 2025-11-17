from flask import Flask, request, jsonify
from datetime import datetime
import sqlite3

app = Flask(__name__)

# DB 연결 함수
def db():
    conn = sqlite3.connect("data.db")
    return conn

# 유저 테이블
with db() as conn:
    conn.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

# 장부 테이블
with db() as conn:
    conn.execute("""
    CREATE TABLE IF NOT EXISTS records(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        time TEXT,
        code TEXT,
        nickname TEXT,
        item TEXT
    )
    """)

# ✅ 회원가입 API
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data["username"]
    password = data["password"]

    with db() as conn:
        try:
            conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password),
            )
        except sqlite3.IntegrityError:
            # 이미 있는 아이디인 경우
            return jsonify({"success": False, "error": "duplicate"})

    return jsonify({"success": True})

# ✅ 로그인 API
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data["username"]
    password = data["password"]

    with db() as conn:
        cur = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password),
        )
        user = cur.fetchone()

    if user:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})

# ✅ 장부 작성 API
@app.route("/add_record", methods=["POST"])
def add_record():
    data = request.json
    code = data["code"]
    nickname = data["nickname"]
    item = data["item"]
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with db() as conn:
        conn.execute(
            "INSERT INTO records (time, code, nickname, item) VALUES (?, ?, ?, ?)",
            (now, code, nickname, item),
        )

    return jsonify({"success": True})

# ✅ 장부 기록 조회 API
@app.route("/get_records", methods=["GET"])
def get_records():
    with db() as conn:
        cur = conn.execute(
            "SELECT time, code, nickname, item FROM records ORDER BY id DESC"
        )
        rows = cur.fetchall()

    return jsonify(rows)

if __name__ == "__main__":
    app.run()
