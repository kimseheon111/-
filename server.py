# ============================
# server.py  (POSTGRESQL 버전)
# ============================

from flask import Flask, request, jsonify
from datetime import datetime
import psycopg2
import psycopg2.extras
import os

app = Flask(__name__)

# ---------------------------
#  PostgreSQL 연결 함수
# ---------------------------
def get_conn():
    return psycopg2.connect(
        os.environ.get("DATABASE_URL"),   # Railway 환경 변수에서 자동 불러옴
        cursor_factory=psycopg2.extras.RealDictCursor
    )

# ---------------------------
#  DB 테이블 생성
# ---------------------------
def init_db():
    conn = get_conn()
    cur = conn.cursor()

    # 유저 테이블
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT,
            nickname TEXT,
            is_admin BOOLEAN DEFAULT FALSE
        );
    """)

    # 기본 관리자 계정 생성
    cur.execute("""
        INSERT INTO users (username, password, nickname, is_admin)
        VALUES ('blackstar', 'Moon1422aa@!', '관리자', TRUE)
        ON CONFLICT (username) DO NOTHING;
    """)

    # 장부 기록 테이블
    cur.execute("""
        CREATE TABLE IF NOT EXISTS records(
            id SERIAL PRIMARY KEY,
            code TEXT,
            nickname TEXT,
            item TEXT,
            time TEXT
        );
    """)

    conn.commit()
    cur.close()
    conn.close()

# ---------------------------
#  로그인
# ---------------------------
@app.post("/login")
def login():
    data = request.json
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE username=%s AND password=%s",
                (data["username"], data["password"]))
    user = cur.fetchone()

    cur.close()
    conn.close()

    if user:
        return jsonify({"success": True, "is_admin": user["is_admin"]})
    return jsonify({"success": False})

# ---------------------------
#  회원가입
# ---------------------------
@app.post("/join")
def join():
    data = request.json
    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO users(username, password, nickname, is_admin)
            VALUES (%s, %s, %s, %s)
        """, (data["username"], data["password"],
              data["nickname"], data.get("is_admin", False)))

        conn.commit()
        ok = True

    except:
        ok = False

    cur.close()
    conn.close()
    return jsonify({"success": ok})

# ---------------------------
#  장부 작성
# ---------------------------
@app.post("/add_record")
def add_record():
    data = request.json
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO records(code, nickname, item, time)
        VALUES (%s, %s, %s, %s)
    """, (data["code"], data["nickname"], data["item"], now))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"success": True})

# ---------------------------
#  장부 목록 불러오기
# ---------------------------
@app.get("/get_records")
def get_records():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM records ORDER BY id DESC")
    rows = cur.fetchall()

    cur.close()
    conn.close()
    return jsonify(rows)

# ---------------------------
#  장부 삭제 (관리자 전용)
# ---------------------------
@app.post("/delete_record")
def delete_record():
    data = request.json
    record_id = data["id"]

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("DELETE FROM records WHERE id = %s", (record_id,))
    conn.commit()

    cur.close()
    conn.close()

    return jsonify({"success": True})


# ---------------------------
#  서버 실행
# ---------------------------
if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)

