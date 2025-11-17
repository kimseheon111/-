from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

def db():
    conn = sqlite3.connect("data.db")
    conn.row_factory = sqlite3.Row
    return conn

# -----------------------------
# DB 초기 테이블 생성
# -----------------------------
with db() as conn:
    conn.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        nickname TEXT,
        is_admin INTEGER DEFAULT 0
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS records(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT,
        nickname TEXT,
        item TEXT,
        time TEXT
    )
    """)

# 기본 관리자 계정 추가 (중복 생성 X)
with db() as conn:
    admin = conn.execute("SELECT * FROM users WHERE username = ?", ("blackstar",)).fetchone()
    if not admin:
        conn.execute("""
            INSERT INTO users (username, password, nickname, is_admin)
            VALUES (?, ?, ?, 1)
        """, ("blackstar", "Moon1422aa@!", "관리자"))
        conn.commit()
        print("기본 관리자 계정 생성 완료")

# -----------------------------
# 로그인
# -----------------------------
@app.post("/login")
def login():
    data = request.json
    with db() as conn:
        user = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (data["username"], data["password"])
        ).fetchone()

    if user:
        return jsonify({"success": True})
    return jsonify({"success": False})

# -----------------------------
# 회원가입
# -----------------------------
@app.post("/join")
def join():
    data = request.json
    try:
        with db() as conn:
            conn.execute("""
                INSERT INTO users (username, password, nickname, is_admin)
                VALUES (?, ?, ?, ?)
            """, (
                data["username"],
                data["password"],
                data["nickname"],
                1 if data.get("is_admin") else 0
            ))
        return jsonify({"success": True})
    except:
        return jsonify({"success": False})

# -----------------------------
# 장부 작성
# -----------------------------
@app.post("/add_record")
def add_record():
    data = request.json
    with db() as conn:
        conn.execute("""
            INSERT INTO records (code, nickname, item, time)
            VALUES (?, ?, ?, ?)
        """, (
            data["code"], data["nickname"], data["item"],
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
    return jsonify({"success": True})

# -----------------------------
# 장부 기록 조회 (★★ 중요 수정 ★★)
# -----------------------------
@app.get("/get_records")
def get_records():
    with db() as conn:
        rows = conn.execute("SELECT code, nickname, item FROM records ORDER BY id DESC").fetchall()

    result = []
    for r in rows:
        result.append({
            "code": r["code"],
            "nickname": r["nickname"],
            "item": r["item"]
        })

    return jsonify(result)  # ★ 리스트로 반환해야 app.py가 정상 작동함!

# -----------------------------
# 서버 실행
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
