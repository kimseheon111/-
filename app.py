import sys
import requests
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

SERVER_URL = "https://accomplished-endurance-production.up.railway.app"


# =========================================
#  로그인 UI
# =========================================
class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("로그인")
        self.setGeometry(700, 300, 500, 420)

        self.setStyleSheet("""
            QWidget {
                background-color: #2A2D32;
                color: white;
                font-family: Malgun Gothic;
                font-size: 16px;
            }
            QLineEdit {
                background-color: #1B1E23;
                color: white;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton {
                background-color: #4A57FF;
                padding: 12px;
                border-radius: 5px;
                color: white;
            }
            QPushButton:hover {
                background-color: #6A74FF;
            }
        """)

        layout = QVBoxLayout()

        title = QLabel("로그인")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 32px; margin-bottom: 15px;")
        layout.addWidget(title)

        self.username = QLineEdit()
        self.username.setPlaceholderText("고번 (아이디)")
        layout.addWidget(self.username)

        self.password = QLineEdit()
        self.password.setPlaceholderText("비밀번호")
        self.password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password)

        # 자동로그인 체크
        self.autoLogin = QCheckBox("자동 로그인")
        layout.addWidget(self.autoLogin)

        login_btn = QPushButton("로그인")
        login_btn.clicked.connect(self.try_login)
        layout.addWidget(login_btn)

        join_btn = QPushButton("회원가입")
        join_btn.clicked.connect(self.open_join)
        layout.addWidget(join_btn)

        self.setLayout(layout)

    def try_login(self):
        data = {
            "username": self.username.text(),
            "password": self.password.text()
        }
        res = requests.post(f"{SERVER_URL}/login", json=data).json()

        if res["success"]:
            self.main = MainWindow(self.username.text())
            self.main.show()
            self.close()
        else:
            QMessageBox.warning(self, "오류", "로그인 실패")

    def open_join(self):
        self.join = JoinWindow()
        self.join.show()


# =========================================
#  회원가입
# =========================================
class JoinWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("회원가입")
        self.setGeometry(750, 350, 400, 300)

        self.setStyleSheet("""
            QWidget { background-color: #2A2D32; color: white; }
            QLineEdit { background-color:#1B1E23; color:white; padding:10px; border-radius:5px; }
            QPushButton { background-color:#4A57FF; padding:10px; border-radius:5px; }
        """)

        layout = QVBoxLayout()

        self.username = QLineEdit(); self.username.setPlaceholderText("고번")
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
            QMessageBox.information(self, "알림", "가입 성공!")
            self.close()
        else:
            QMessageBox.warning(self, "오류", "이미 존재하는 계정입니다.")


# =========================================
#  메인 화면
# =========================================
class MainWindow(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username

        self.setWindowTitle("장부 시스템")
        self.setGeometry(400, 150, 1200, 750)

        self.setStyleSheet("""
            QWidget { background-color: #2A2D32; color: white; font-size: 15px; }
            QListWidget { background-color: #1B1E23; color: white; font-size: 17px; }
            QLineEdit { background-color:#1B1E23; color:white; padding:12px; border-radius:5px; }
            QPushButton { background-color:#4A57FF; padding:15px; border-radius:5px; color:white; }
            QTableWidget { background-color:#1B1E23; color:white; }
            QHeaderView::section { background-color:#111217; padding:5px; }
        """)

        main_layout = QHBoxLayout()

        # 메뉴
        self.menu = QListWidget()
        self.menu.addItem("장부 작성")
        self.menu.addItem("장부 기록")
        self.menu.addItem("관리자 추가")
        self.menu.setFixedWidth(200)
        self.menu.currentRowChanged.connect(self.change_page)

        self.stack = QStackedWidget()
        self.stack.addWidget(self.page_write_ui())
        self.stack.addWidget(self.page_records_ui())
        self.stack.addWidget(self.page_admin_ui())

        main_layout.addWidget(self.menu)
        main_layout.addWidget(self.stack)
        self.setLayout(main_layout)

    # 장부 작성 화면
    def page_write_ui(self):
        w = QWidget()
        layout = QVBoxLayout()

        self.code = QLineEdit(); self.code.setPlaceholderText("고유번호")
        self.nick = QLineEdit(); self.nick.setPlaceholderText("닉네임")
        self.item = QLineEdit(); self.item.setPlaceholderText("판매 항목")

        btn = QPushButton("작성하기")
        btn.clicked.connect(self.write_record)

        layout.addWidget(self.code)
        layout.addWidget(self.nick)
        layout.addWidget(self.item)
        layout.addWidget(btn)

        w.setLayout(layout)
        return w

    # 장부 기록 화면 (★ 날짜 열 추가)
    def page_records_ui(self):
        w = QWidget()
        layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["시간", "고유번호", "닉네임", "항목"])

        btn = QPushButton("새로고침")
        btn.clicked.connect(self.load_records)

        layout.addWidget(self.table)
        layout.addWidget(btn)
        w.setLayout(layout)
        return w

    # 관리자 추가
    def page_admin_ui(self):
        w = QWidget()
        layout = QVBoxLayout()

        self.admin_user = QLineEdit(); self.admin_user.setPlaceholderText("관리자 고번")
        self.admin_pass = QLineEdit(); self.admin_pass.setPlaceholderText("비밀번호")
        self.admin_nick = QLineEdit(); self.admin_nick.setPlaceholderText("닉네임")

        btn = QPushButton("관리자 추가")
        btn.clicked.connect(self.add_admin)

        layout.addWidget(self.admin_user)
        layout.addWidget(self.admin_pass)
        layout.addWidget(self.admin_nick)
        layout.addWidget(btn)
        w.setLayout(layout)
        return w

    def change_page(self, i):
        self.stack.setCurrentIndex(i)

    def write_record(self):
        data = {
            "code": self.code.text(),
            "nickname": self.nick.text(),
            "item": self.item.text()
        }
        requests.post(f"{SERVER_URL}/add_record", json=data)
        QMessageBox.information(self, "알림", "등록 완료!")

    # ★ 서버에서 time, code, nickname, item 받아오기
    def load_records(self):
        res = requests.get(f"{SERVER_URL}/get_records").json()

        self.table.setRowCount(len(res))

        for i, row in enumerate(res):
            self.table.setItem(i, 0, QTableWidgetItem(row["time"]))
            self.table.setItem(i, 1, QTableWidgetItem(row["code"]))
            self.table.setItem(i, 2, QTableWidgetItem(row["nickname"]))
            self.table.setItem(i, 3, QTableWidgetItem(row["item"]))

    def add_admin(self):
        data = {
            "username": self.admin_user.text(),
            "password": self.admin_pass.text(),
            "nickname": self.admin_nick.text(),
            "is_admin": 1
        }
        requests.post(f"{SERVER_URL}/join", json=data)
        QMessageBox.information(self, "알림", "관리자 추가 완료!")


# 실행
app = QApplication(sys.argv)
win = LoginWindow()
win.show()
sys.exit(app.exec_())
