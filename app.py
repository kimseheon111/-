import sys
import os
import json
import requests
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

SERVER_URL = "https://accomplished-endurance-production.up.railway.app"
LOGIN_FILE = "login.json"


# =========================================
#  로그인 창
# =========================================
class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("로그인")
        self.setGeometry(700, 300, 500, 360)

        self.setStyleSheet("""
            QWidget {
                background-color: #2A2D32;
                color: white;
                font-family: Malgun Gothic;
                font-size: 14px;
            }
            QLineEdit {
                background-color: #1B1E23;
                color: white;
                padding: 8px;
                border-radius: 5px;
                border: 1px solid #3A3D44;
            }
            QPushButton {
                background-color: #4A57FF;
                color: white;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #6A74FF;
            }
            QCheckBox {
                color: #CCCCCC;
            }
        """)

        layout = QVBoxLayout()

        title = QLabel("로그인")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 32px; color: white; margin-bottom: 10px;")
        layout.addWidget(title)

        self.username = QLineEdit()
        self.username.setPlaceholderText("고번 (아이디)")
        layout.addWidget(self.username)

        self.password = QLineEdit()
        self.password.setPlaceholderText("비밀번호")
        self.password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password)

        self.auto_login_chk = QCheckBox("자동 로그인")
        layout.addWidget(self.auto_login_chk)

        self.login_btn = QPushButton("로그인")
        self.login_btn.clicked.connect(self.try_login)
        layout.addWidget(self.login_btn)

        self.join_btn = QPushButton("회원가입")
        self.join_btn.clicked.connect(self.open_join)
        layout.addWidget(self.join_btn)

        layout.addStretch()
        self.setLayout(layout)

        # 저장된 로그인 정보가 있으면 로드
        self.load_saved_login()

    # --------------------------
    def load_saved_login(self):
        if not os.path.exists(LOGIN_FILE):
            return
        try:
            with open(LOGIN_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.username.setText(data.get("username", ""))
            self.password.setText(data.get("password", ""))
            auto = data.get("auto", False)
            self.auto_login_chk.setChecked(auto)
            if auto and self.username.text() and self.password.text():
                # 자동 로그인 시도
                self.try_login(auto=True)
        except Exception:
            pass

    def save_login(self):
        if self.auto_login_chk.isChecked():
            data = {
                "username": self.username.text(),
                "password": self.password.text(),
                "auto": True
            }
            with open(LOGIN_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
        else:
            if os.path.exists(LOGIN_FILE):
                os.remove(LOGIN_FILE)

    # --------------------------
    def try_login(self, auto=False):
        data = {
            "username": self.username.text(),
            "password": self.password.text()
        }
        try:
            res = requests.post(f"{SERVER_URL}/login", json=data, timeout=5)
            res = res.json()
        except Exception:
            if not auto:
                QMessageBox.warning(self, "오류", "서버에 접속할 수 없습니다.")
            return

        if res.get("success"):
            # 로그인 정보 저장/삭제
            self.save_login()

            nickname = res.get("nickname", "")
            is_admin = res.get("is_admin", False)

            self.main = MainWindow(
                username=self.username.text(),
                nickname=nickname,
                is_admin=is_admin
            )
            self.main.show()
            self.close()
        else:
            if not auto:
                QMessageBox.warning(self, "오류", "로그인 실패")

    def open_join(self):
        self.join = JoinWindow()
        self.join.show()


# =========================================
#  회원가입 창
# =========================================
class JoinWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("회원가입")
        self.setGeometry(750, 350, 400, 260)

        self.setStyleSheet("""
            QWidget { background-color: #2A2D32; color: white; }
            QLineEdit { background-color: #1B1E23; color: white; padding: 8px; border-radius: 5px; }
            QPushButton { background-color: #4A57FF; color:white; padding:10px; border-radius: 5px; }
        """)

        layout = QVBoxLayout()
        self.username = QLineEdit()
        self.username.setPlaceholderText("아이디")
        self.password = QLineEdit()
        self.password.setPlaceholderText("비밀번호")
        self.password.setEchoMode(QLineEdit.Password)
        self.nickname = QLineEdit()
        self.nickname.setPlaceholderText("닉네임")

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
            "nickname": self.nickname.text(),
        }
        try:
            res = requests.post(f"{SERVER_URL}/join", json=data, timeout=5).json()
        except Exception:
            QMessageBox.warning(self, "오류", "서버에 접속할 수 없습니다.")
            return

        if res.get("success"):
            QMessageBox.information(self, "알림", "가입 완료!")
            self.close()
        else:
            QMessageBox.warning(self, "오류", res.get("message", "가입 실패"))


# =========================================
#  메인 창
# =========================================
class MainWindow(QWidget):
    def __init__(self, username, nickname, is_admin):
        super().__init__()
        self.username = username
        self.nickname = nickname
        self.is_admin = is_admin

        self.setWindowTitle("장부 시스템")
        self.setGeometry(400, 150, 1100, 700)

        self.setStyleSheet("""
            QWidget { background-color: #2A2D32; color: white; font-size: 14px; }
            QListWidget {
                background-color: #1B1E23;
                color: white;
                font-size: 16px;
                border: none;
            }
            QListWidget::item {
                padding: 8px;
            }
            QListWidget::item:selected {
                background-color: #4A57FF;
            }
            QLineEdit { background-color: #1B1E23; color: white; padding: 10px; border-radius: 5px; }
            QPushButton { background-color: #4A57FF; color:white; padding:12px; border-radius: 5px; }
            QPushButton:hover { background-color:#6A74FF; }
            QTableWidget { background-color: #1B1E23; color:white; gridline-color:#333333; }
            QHeaderView::section { background-color:#111217; color:white; }
        """)

        main_layout = QHBoxLayout()

        # ----- 왼쪽 메뉴 -----
        self.menu = QListWidget()
        self.menu.setFixedWidth(200)
        self.menu.addItem("장부 작성")
        self.menu.addItem("장부 기록")
        self.menu.addItem("관리자 추가")
        self.menu.currentRowChanged.connect(self.change_page)

        # ----- 오른쪽 스택 -----
        self.stack = QStackedWidget()

        self.page_write = self.page_write_ui()
        self.page_records = self.page_records_ui()
        self.page_admin = self.page_admin_ui()

        self.stack.addWidget(self.page_write)
        self.stack.addWidget(self.page_records)
        self.stack.addWidget(self.page_admin)

        main_layout.addWidget(self.menu)
        main_layout.addWidget(self.stack)

        self.setLayout(main_layout)

    # -----------------------------
    #  장부 작성 페이지
    # -----------------------------
    def page_write_ui(self):
        w = QWidget()
        layout = QVBoxLayout()

        self.code = QLineEdit()
        self.code.setPlaceholderText("고유번호 (예: 인게임 ID 등)")
        self.nick = QLineEdit()
        self.nick.setPlaceholderText("닉네임")
        self.item = QLineEdit()
        self.item.setPlaceholderText("판매 항목")

        btn = QPushButton("작성하기")
        btn.clicked.connect(self.write_record)

        layout.addSpacing(40)
        layout.addWidget(self.code)
        layout.addWidget(self.nick)
        layout.addWidget(self.item)
        layout.addSpacing(20)
        layout.addWidget(btn)
        layout.addStretch()

        w.setLayout(layout)
        return w

    # -----------------------------
    #  장부 기록 페이지
    # -----------------------------
    def page_records_ui(self):
        w = QWidget()
        v = QVBoxLayout()

        self.table = QTableWidget()
        # 0: id (숨김), 1: 시간, 2: 고유번호, 3: 닉네임, 4: 항목
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "시간", "고유번호", "닉네임", "항목"])
        self.table.hideColumn(0)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.table.setColumnWidth(1, 200)  # 시간 전체 보이게
        self.table.setColumnWidth(2, 120)
        self.table.setColumnWidth(3, 120)

        btn_layout = QHBoxLayout()
        refresh_btn = QPushButton("새로고침")
        refresh_btn.clicked.connect(self.load_records)
        btn_layout.addWidget(refresh_btn)

        if self.is_admin:
            del_btn = QPushButton("선택 삭제")
            del_btn.clicked.connect(self.delete_selected_record)
            btn_layout.addWidget(del_btn)

        btn_layout.addStretch()

        v.addWidget(self.table)
        v.addLayout(btn_layout)
        w.setLayout(v)
        return w

    # -----------------------------
    #  관리자 추가 페이지
    # -----------------------------
    def page_admin_ui(self):
        w = QWidget()
        layout = QVBoxLayout()

        if not self.is_admin:
            label = QLabel("관리자만 사용할 수 있는 메뉴입니다.")
            layout.addSpacing(40)
            layout.addWidget(label)
            layout.addStretch()
            w.setLayout(layout)
            return w

        self.admin_user = QLineEdit()
        self.admin_user.setPlaceholderText("추가할 관리자 아이디")
        self.admin_pass = QLineEdit()
        self.admin_pass.setPlaceholderText("비밀번호")
        self.admin_pass.setEchoMode(QLineEdit.Password)
        self.admin_nick = QLineEdit()
        self.admin_nick.setPlaceholderText("닉네임")

        btn = QPushButton("관리자 추가")
        btn.clicked.connect(self.add_admin)

        layout.addSpacing(40)
        layout.addWidget(self.admin_user)
        layout.addWidget(self.admin_pass)
        layout.addWidget(self.admin_nick)
        layout.addSpacing(20)
        layout.addWidget(btn)
        layout.addStretch()

        w.setLayout(layout)
        return w

    # -----------------------------
    #  공용 기능
    # -----------------------------
    def change_page(self, idx):
        self.stack.setCurrentIndex(idx)

    # ----- 장부 작성 -----
    def write_record(self):
        data = {
            "code": self.code.text(),
            "nickname": self.nick.text(),
            "item": self.item.text(),
        }
        try:
            res = requests.post(f"{SERVER_URL}/add_record", json=data, timeout=5).json()
        except Exception:
            QMessageBox.warning(self, "오류", "서버에 접속할 수 없습니다.")
            return

        if res.get("success"):
            QMessageBox.information(self, "알림", "등록 완료!")
            self.code.clear()
            self.nick.clear()
            self.item.clear()
        else:
            QMessageBox.warning(self, "오류", "등록 실패")

    # ----- 장부 기록 불러오기 -----
    def load_records(self):
        try:
            data = requests.get(f"{SERVER_URL}/get_records", timeout=5).json()
        except Exception:
            QMessageBox.warning(self, "오류", "서버에 접속할 수 없습니다.")
            return

        self.table.setRowCount(len(data))
        for i, row in enumerate(data):
            self.table.setItem(i, 0, QTableWidgetItem(str(row["id"])))
            self.table.setItem(i, 1, QTableWidgetItem(row["time"]))
            self.table.setItem(i, 2, QTableWidgetItem(row["code"]))
            self.table.setItem(i, 3, QTableWidgetItem(row["nickname"]))
            self.table.setItem(i, 4, QTableWidgetItem(row["item"]))

    # ----- 선택 삭제 (관리자) -----
    def delete_selected_record(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "알림", "삭제할 행을 선택하세요.")
            return

        record_id_item = self.table.item(row, 0)
        if record_id_item is None:
            return
        record_id = int(record_id_item.text())

        reply = QMessageBox.question(
            self,
            "확인",
            "정말 삭제하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        data = {
            "username": self.username,
            "record_id": record_id
        }
        try:
            res = requests.post(f"{SERVER_URL}/delete_record", json=data, timeout=5).json()
        except Exception:
            QMessageBox.warning(self, "오류", "서버에 접속할 수 없습니다.")
            return

        if res.get("success"):
            QMessageBox.information(self, "알림", "삭제 완료")
            self.load_records()
        else:
            QMessageBox.warning(self, "오류", res.get("message", "삭제 실패"))

    # ----- 관리자 추가 -----
    def add_admin(self):
        data = {
            "admin_username": self.username,
            "username": self.admin_user.text(),
            "password": self.admin_pass.text(),
            "nickname": self.admin_nick.text(),
        }
        try:
            res = requests.post(f"{SERVER_URL}/add_admin", json=data, timeout=5).json()
        except Exception:
            QMessageBox.warning(self, "오류", "서버에 접속할 수 없습니다.")
            return

        if res.get("success"):
            QMessageBox.information(self, "알림", "관리자 추가 완료!")
            self.admin_user.clear()
            self.admin_pass.clear()
            self.admin_nick.clear()
        else:
            QMessageBox.warning(self, "오류", res.get("message", "추가 실패"))


# =========================================
#  실행
# =========================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = LoginWindow()
    win.show()
    sys.exit(app.exec_())
