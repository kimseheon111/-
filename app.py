# =============================================
# app.py  (PyQt5 클라이언트 / PostgreSQL 서버용)
# =============================================

import sys
import requests
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

SERVER_URL = "https://zonal-nature-production.up.railway.app"   # 네 서버 URL 넣기

# ---------------------------------------------
#  로그인 UI
# ---------------------------------------------
class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("로그인")
        self.setGeometry(700, 300, 480, 330)

        self.setStyleSheet("""
            QWidget { background:#2A2D32; color:white; font-size:16px; }
            QLineEdit { background:#1B1E23; padding:8px; border-radius:5px; }
            QPushButton { background:#4A57FF; padding:10px; border-radius:5px; }
        """)

        layout = QVBoxLayout()

        title = QLabel("로그인")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:32px; margin-bottom:20px;")
        layout.addWidget(title)

        self.username = QLineEdit(); self.username.setPlaceholderText("고번 (아이디)")
        self.password = QLineEdit(); self.password.setPlaceholderText("비밀번호")
        self.password.setEchoMode(QLineEdit.Password)

        layout.addWidget(self.username)
        layout.addWidget(self.password)

        self.save_check = QCheckBox("자동 로그인")
        layout.addWidget(self.save_check)

        btn = QPushButton("로그인")
        btn.clicked.connect(self.try_login)
        layout.addWidget(btn)

        join = QPushButton("회원가입")
        join.clicked.connect(self.open_join)
        layout.addWidget(join)

        self.setLayout(layout)

    def try_login(self):
        data = {
            "username": self.username.text(),
            "password": self.password.text()
        }
        res = requests.post(f"{SERVER_URL}/login", json=data).json()

        if res["success"]:
            self.main = MainWindow(self.username.text(), res["is_admin"])
            self.main.show()
            self.close()
        else:
            QMessageBox.warning(self, "오류", "로그인 실패")

    def open_join(self):
        self.join = JoinWindow()
        self.join.show()


# ---------------------------------------------
#  회원가입 UI
# ---------------------------------------------
class JoinWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("회원가입")
        self.setGeometry(720, 340, 380, 280)

        self.setStyleSheet("""
            QWidget { background:#2A2D32; color:white; }
            QLineEdit { background:#1B1E23; padding:8px; border-radius:5px; }
            QPushButton { background:#4A57FF; padding:10px; border-radius:5px; }
        """)

        layout = QVBoxLayout()

        self.username = QLineEdit(); self.username.setPlaceholderText("아이디")
        self.password = QLineEdit(); self.password.setPlaceholderText("비밀번호")
        self.nickname = QLineEdit(); self.nickname.setPlaceholderText("닉네임")

        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(self.nickname)

        btn = QPushButton("가입하기")
        btn.clicked.connect(self.join)
        layout.addWidget(btn)

        self.setLayout(layout)

    def join(self):
        data = {
            "username": self.username.text(),
            "password": self.password.text(),
            "nickname": self.nickname.text()
        }
        res = requests.post(f"{SERVER_URL}/join", json=data).json()

        if res["success"]:
            QMessageBox.information(self, "성공", "가입 완료!")
            self.close()
        else:
            QMessageBox.warning(self, "오류", "이미 존재하는 계정입니다.")


# ---------------------------------------------
#  메인 프로그램
# ---------------------------------------------
class MainWindow(QWidget):
    def __init__(self, username, is_admin):
        super().__init__()
        self.username = username
        self.is_admin = is_admin

        self.setWindowTitle("장부 시스템")
        self.setGeometry(500, 200, 1100, 700)

        self.setStyleSheet("""
            QWidget { background:#2A2D32; color:white; }
            QListWidget { background:#1B1E23; font-size:16px; }
            QLineEdit { background:#1B1E23; padding:10px; border-radius:5px; }
            QPushButton { background:#4A57FF; padding:14px; border-radius:5px; }
            QTableWidget { background:#1B1E23; }
            QHeaderView::section { background:#111217; color:white; }
        """)

        main = QHBoxLayout()

        # 메뉴
        self.menu = QListWidget()
        self.menu.addItem("장부 작성")
        self.menu.addItem("장부 기록")
        if is_admin:
            self.menu.addItem("관리자 추가")
        self.menu.currentRowChanged.connect(self.change_page)

        # 페이지 스택
        self.stack = QStackedWidget()

        self.stack.addWidget(self.page_write_ui())
        self.stack.addWidget(self.page_records_ui())
        if is_admin:
            self.stack.addWidget(self.page_admin_ui())

        main.addWidget(self.menu)
        main.addWidget(self.stack)
        self.setLayout(main)

    # -----------------------------
    #  장부 작성 UI
    # -----------------------------
    def page_write_ui(self):
        w = QWidget()
        v = QVBoxLayout()

        self.code = QLineEdit(); self.code.setPlaceholderText("고유번호")
        self.nick = QLineEdit(); self.nick.setPlaceholderText("닉네임")
        self.item = QLineEdit(); self.item.setPlaceholderText("판매 항목")

        btn = QPushButton("작성하기")
        btn.clicked.connect(self.write_record)

        v.addWidget(self.code)
        v.addWidget(self.nick)
        v.addWidget(self.item)
        v.addWidget(btn)

        w.setLayout(v)
        return w

    # -----------------------------
    #  장부 기록 UI
    # -----------------------------
    def page_records_ui(self):
        w = QWidget()
        v = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "고유번호", "닉네임", "항목", "시간"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        refresh = QPushButton("새로고침")
        refresh.clicked.connect(self.load_records)

        delete = QPushButton("선택 삭제 (관리자)")
        delete.clicked.connect(self.delete_record)
        if not self.is_admin:
            delete.setDisabled(True)

        v.addWidget(self.table)
        v.addWidget(refresh)
        v.addWidget(delete)

        w.setLayout(v)
        return w

    # -----------------------------
    #  관리자 추가 UI
    # -----------------------------
    def page_admin_ui(self):
        w = QWidget()
        v = QVBoxLayout()

        self.admin_user = QLineEdit(); self.admin_user.setPlaceholderText("관리자 아이디")
        self.admin_pass = QLineEdit(); self.admin_pass.setPlaceholderText("비밀번호")
        self.admin_nick = QLineEdit(); self.admin_nick.setPlaceholderText("닉네임")

        btn = QPushButton("관리자 추가")
        btn.clicked.connect(self.add_admin)

        v.addWidget(self.admin_user)
        v.addWidget(self.admin_pass)
        v.addWidget(self.admin_nick)
        v.addWidget(btn)
        w.setLayout(v)

        return w

    # =============================
    # 기능들
    # =============================
    def change_page(self, idx):
        self.stack.setCurrentIndex(idx)

    def write_record(self):
        data = {
            "code": self.code.text(),
            "nickname": self.nick.text(),
            "item": self.item.text()
        }
        requests.post(f"{SERVER_URL}/add_record", json=data)
        QMessageBox.information(self, "성공", "작성 완료!")

    def load_records(self):
        data = requests.get(f"{SERVER_URL}/get_records").json()

        self.table.setRowCount(len(data))
        for i, row in enumerate(data):
            self.table.setItem(i, 0, QTableWidgetItem(str(row["id"])))
            self.table.setItem(i, 1, QTableWidgetItem(row["code"]))
            self.table.setItem(i, 2, QTableWidgetItem(row["nickname"]))
            self.table.setItem(i, 3, QTableWidgetItem(row["item"]))
            self.table.setItem(i, 4, QTableWidgetItem(row["time"]))

    def delete_record(self):
        row = self.table.currentRow()
        if row < 0:
            return

        record_id = self.table.item(row, 0).text()
        requests.post(f"{SERVER_URL}/delete_record", json={"id": record_id})
        QMessageBox.information(self, "삭제", "삭제 완료!")
        self.load_records()

    def add_admin(self):
        data = {
            "username": self.admin_user.text(),
            "password": self.admin_pass.text(),
            "nickname": self.admin_nick.text(),
            "is_admin": True
        }
        requests.post(f"{SERVER_URL}/join", json=data)
        QMessageBox.information(self, "성공", "관리자 추가 완료!")


# ---------------------------------------------
# 실행
# ---------------------------------------------
app = QApplication(sys.argv)
win = LoginWindow()
win.show()
sys.exit(app.exec_())
