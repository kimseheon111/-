from flask import Flask, request, jsonify
from datetime import datetime
import sqlite3

app = Flask(__name__)


# -------------------------
# DB 연결
# -------------------------
def db():
    conn = sqlite3.connect("data.db")
    conn.row_factory = sqlite3.Row  # dict처럼 사용 가능
    return conn


# -------------------------
# DB 초기화 + 컬럼 보정
# -------------------------
def init_db():
    with db() as conn:
        # 기본 테이블 생성
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
            time TEXT,
            code TEXT,
            nickname TEXT,
            item TEXT
        )
        """)

        # 예전 DB에 컬럼이 없을 수도 있으니 보정
        try:
            conn.execute("SELECT is_admin FROM users LIMIT 1")
        except sqlite3.OperationalError:
            conn.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")

        try:
            conn.execute("SELECT time FROM records LIMIT 1")
        except sqlite3.OperationalError:
            conn.execute("ALTER TABLE records ADD COLUMN time TEXT")

    # 기본 관리자 계정 생성 (없으면)
    with db() as conn:
        cur = conn.execute("SELECT id FROM users WHERE username = ?", ("blackstar",))
        if cur.fetchone() is None:
            conn.execute(
                "INSERT INTO users (username, password, nickname, is_admin) VALUES (?, ?, ?, ?)",
                ("blackstar", "Moon1422aa@!", "관리자", 1)
            )


init_db()


# ------------------------------------
# 로그인
# ------------------------------------
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    with db() as conn:
        cur = conn.execute(
            "SELECT username, nickname, is_admin FROM users WHERE username=? AND password=?",
            (username, password)
        )
        user = cur.fetchone()

    if user:
        return jsonify({
            "success": True,
            "username": user["username"],
            "nickname": user["nickname"],
            "is_admin": bool(user["is_admin"])
        })
    else:
        return jsonify({"success": False})


# ------------------------------------
# 회원가입 (일반 유저)
# ------------------------------------
@app.route("/join", methods=["POST"])
def join():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    nickname = data.get("nickname")

    if not username or not password or not nickname:
        return jsonify({"success": False, "message": "필수값 누락"})

    try:
        with db() as conn:
            conn.execute(
                "INSERT INTO users (username, password, nickname, is_admin) VALUES (?, ?, ?, 0)",
                (username, password, nickname)
            )
        return jsonify({"success": True})
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "message": "이미 존재하는 아이디입니다."})


# ------------------------------------
# 관리자 추가 (관리자만 가능)
# ------------------------------------
@app.route("/add_admin", methods=["POST"])
def add_admin():
    data = request.json
    admin_username = data.get("admin_username")  # 요청 보낸 사람
    username = data.get("username")
    password = data.get("password")
    nickname = data.get("nickname")

    if not admin_username or not username or not password or not nickname:
        return jsonify({"success": False, "message": "필수값 누락"})

    with db() as conn:
        cur = conn.execute(
            "SELECT is_admin FROM users WHERE username=?",
            (admin_username,)
        )
        u = cur.fetchone()
        if not u or not bool(u["is_admin"]):
            return jsonify({"success": False, "message": "관리자 권한 없음"})

        try:
            conn.execute(
                "INSERT INTO users (username, password, nickname, is_admin) VALUES (?, ?, ?, 1)",
                (username, password, nickname)
            )
            return jsonify({"success": True})
        except sqlite3.IntegrityError:
            return jsonify({"success": False, "message": "이미 존재하는 아이디입니다."})


# ------------------------------------
# 장부 작성
# ------------------------------------
@app.route("/add_record", methods=["POST"])
def add_record():
    data = request.json
    code = data.get("code")
    nickname = data.get("nickname")
    item = data.get("item")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with db() as conn:
        conn.execute(
            "INSERT INTO records (time, code, nickname, item) VALUES (?, ?, ?, ?)",
            (now, code, nickname, item)
        )

    return jsonify({"success": True})


# ------------------------------------
# 장부 기록 조회
# ------------------------------------
@app.route("/get_records", methods=["GET"])
def get_records():
    with db() as conn:
        cur = conn.execute(
            "SELECT id, time, code, nickname, item FROM records ORDER BY id DESC"
        )
        rows = cur.fetchall()

    records = []
    for r in rows:
        records.append({
            "id": r["id"],
            "time": r["time"],
            "code": r["code"],
            "nickname": r["nickname"],
            "item": r["item"],
        })

    return jsonify(records)


# ------------------------------------
# 기록 삭제 (관리자만)
# ------------------------------------
@app.route("/delete_record", methods=["POST"])
def delete_record():
    data = request.json
    username = data.get("username")
    record_id = data.get("record_id")

    if username is None or record_id is None:
        return jsonify({"success": False, "message": "잘못된 요청"})

    with db() as conn:
        # 삭제 요청한 사람이 관리자냐?
        cur = conn.execute(
            "SELECT is_admin FROM users WHERE username=?",
            (username,)
        )
        u = cur.fetchone()
        if not u or not bool(u["is_admin"]):
            return jsonify({"success": False, "message": "관리자 권한 없음"})

        conn.execute("DELETE FROM records WHERE id=?", (record_id,))

    return jsonify({"success": True})


if __name__ == "__main__":
    app.run()

