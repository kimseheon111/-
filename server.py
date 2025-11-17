from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import os

app = Flask(__name__)

# ================================
# PostgreSQL 접속 함수
# ================================
def get_conn():
    return psycopg2.connect(
        host=os.environ.get("PGHOST"),
        dbname=os.environ.get("PGDATABASE"),
        user=os.environ.get("PGUSER"),
        password=os.environ.get("PGPASSWORD"),
        port=os.environ.get("PGPORT")
    )

# ================================
# 테이블 생성
# ================================
def init_tables():
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

    # 장부 기록 테이블
    cur.execute("""
        CREATE TABLE IF NOT EXISTS records(
            id SERIAL PRIMARY KEY,
            time TEXT,
            code TEXT,
            nickname TEXT,
            item TEXT
        );
    """)

    # 기본 관리자 계정 생성
    cur.execute("SELECT * FROM users WHERE username='blackstar'")
    if cur.fetchone() is None:
        cur.execute("""
            INSERT INTO users (username, password, nickname, is_admin)
            VALUES ('blackstar', 'Moon1422aa@!', '관리자', TRUE);
        """)

    conn.commit()
    cur.close()
    conn.close()

init_tables()

# ================================
# 로그인
# ================================
@app.post("/login")
def login():
    data = request.json
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT * FROM users WHERE username=%s AND password=%s",
                (data["username"], data["password"]))

    user = cur.fetchone()
    cur.close()
    conn.close()

    if user:
        return jsonify({"success": True, "is_admin": user["is_admin"]})
    else:
        return jsonify({"success": False})

# ================================
# 회원가입
# ================================
@app.post("/join")
def join():
    data = request.json
    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO users (username, password, nickname, is_admin)
            VALUES (%s, %s, %s, %s)
        """, (data["username"], data["password"], data["nickname"], data.get("is_admin", False)))

        conn.commit()
        result = True

    except:
        result = False

    cur.close()
    conn.close()
    return jsonify({"success": result})

# ================================
# 장부 추가
# ================================
@app.post("/add_record")
def add_record():
    data = request.json
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO records (time, code, nickname, item)
        VALUES (%s, %s, %s, %s)
    """, (now, data["code"], data["nickname"], data["item"]))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"success": True})

# ================================
# 장부 기록 가져오기
# ================================
@app.get("/get_records")
def get_records():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT * FROM records ORDER BY id DESC")
    rows = cur.fetchall()

    cur.close()
    conn.close()
    return jsonify(rows)

# ================================
# 기록 삭제 (관리자 전용)
# ================================
@app.post("/delete_record")
def delete_record():
    data = request.json  # id 값 받음

    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute("DELETE FROM records WHERE id=%s", (data["id"],))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"success": True})

# ================================
# 서버 시작
# ================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

