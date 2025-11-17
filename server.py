from flask import Flask, request, jsonify
from datetime import datetime
import sqlite3

app = Flask(__name__)

# DB 연결 함수
def get_db():
    conn = sqlite3.connect("data.db")
    conn.row_factory = sqlite3.Row
    return conn


# DB 초기 구성 (users + records)
with get_db() as conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            nickname TEXT,
            is_admin INTEGER DEFAULT 0
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time TEXT,
            code TEXT,
            nickname TEXT,
            item TEXT
        )
    """)

    # 기본 관리자 계정
    try:
        conn.execute("""
            INSERT INTO users (username, password, nickname, is_admin)
            VALUES ('blackstar', 'Moon1422aa@!', '관리자', 1)
        """)
    except:
        pass


# -----------------------------------
# 로그인 API
# -----------------------------------
@app.post("/login")
def login():
    data = request.json
    username = data["username"]
    password = data["password"]

    with get_db() as conn:
        user = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        ).fetchone()

    if user:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})


# -----------------------------------
# 회원가입 API
# -----------------------------------
@app.post("/join")
def join():
    data = request.json
    username = data["username"]
    password = data["password"]
    nickname = data["nickname"]
    is_admin = data.get("is_admin", 0)

    with get_db() as conn:
        try:
            conn.execute(
                "INSERT INTO users (username, password, nickname, is_admin) VALUES (?, ?, ?, ?)",
                (username, password, nickname, is_admin)
            )
            return jsonify({"success": True})
        except:
            return jsonify({"success": False})


# -----------------------------------
# 장부 추가 (★ 날짜 자동 저장)
# -----------------------------------
@app.post("/add_record")
def add_record():
    data = request.json
    code = data["code"]
    nickname = data["nickname"]
    item = data["item"]
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with get_db() as conn:
        conn.execute(
            "INSERT INTO records (time, code, nickname, item) VALUES (?, ?, ?, ?)",
            (now, code, nickname, item)
        )
    return jsonify({"success": True})


# -----------------------------------
# 장부 목록 가져오기
# -----------------------------------
@app.get("/get_records")
def get_records():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM records ORDER BY id DESC"
        ).fetchall()

    return jsonify([dict(row) for row in rows])


# -----------------------------------
# 실행
# -----------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
