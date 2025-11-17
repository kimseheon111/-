from flask import Flask, request, jsonify
from datetime import datetime
import sqlite3

app = Flask(__name__)

def db():
    conn = sqlite3.connect("data.db")
    return conn


# --------------------------
# 🔥 DB 테이블 생성
# --------------------------
with db() as conn:
    # 유저 테이블 (admin 포함)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            is_admin INTEGER DEFAULT 0
        )
    """)

    # 장부 기록 테이블
    conn.execute("""
        CREATE TABLE IF NOT EXISTS records(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time TEXT,
            code TEXT,
            nickname TEXT,
            item TEXT
        )
    """)

    # 기본 관리자 계정 자동 생성
    cur = conn.execute("SELECT * FROM users WHERE username='blackstar'")
    if cur.fetchone() is None:
        conn.execute("""
            INSERT INTO users(username, password, is_admin)
            VALUES('blackstar', 'Moon1422aa@!', 1)
        """)
        print("기본 관리자 계정 생성됨: blackstar / Moon1422aa@!")


# --------------------------
# 1) 회원가입
# --------------------------
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data["username"]
    password = data["password"]

    try:
        with db() as conn:
            conn.execute("INSERT INTO users(username, password) VALUES (?, ?)", (username, password))
        return jsonify({"success": True})
    except:
        return jsonify({"success": False, "msg": "이미 존재하는 아이디입니다."})


# --------------------------
# 2) 로그인
# --------------------------
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data["username"]
    password = data["password"]

    with db() as conn:
        cur = conn.execute(
            "SELECT id, is_admin FROM users WHERE username=? AND password=?",
            (username, password)
        )
        user = cur.fetchone()

    if user:
        return jsonify({"success": True, "is_admin": user[1]})
    else:
        return jsonify({"success": False})


# --------------------------
# 3) 장부 작성
# --------------------------
@app.route("/add_record", methods=["POST"])
def add_record():
    data = request.json
    code = data["code"]
    nickname = data["nickname"]
    item = data["item"]
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with db() as conn:
        conn.execute(
            "INSERT INTO records(time, code, nickname, item) VALUES (?, ?, ?, ?)",
            (now, code, nickname, item)
        )

    return jsonify({"success": True})


# --------------------------
# 4) 장부 기록 조회
# --------------------------
@app.route("/get_records", methods=["GET"])
def get_records():
    with db() as conn:
        cur = conn.execute("SELECT time, code, nickname, item FROM records ORDER BY id DESC")
        rows = cur.fetchall()

    return jsonify(rows)


# --------------------------
# 5) 관리자 기능 - 유저 목록
# --------------------------
@app.route("/admin/users", methods=["GET"])
def list_users():
    with db() as conn:
        cur = conn.execute("SELECT username, is_admin FROM users ORDER BY id DESC")
        rows = cur.fetchall()

    return jsonify(rows)


# --------------------------
# 6) 관리자 기능 - 유저 관리자 승격
# --------------------------
@app.route("/admin/promote", methods=["POST"])
def promote_user():
    data = request.json
    username = data["username"]

    with db() as conn:
        conn.execute("UPDATE users SET is_admin=1 WHERE username=?", (username,))

    return jsonify({"success": True})


# --------------------------
# Flask 실행
# --------------------------
if __name__ == "__main__":
    app.run()
