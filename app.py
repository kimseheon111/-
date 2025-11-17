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
        self.setGeometry(700, 300, 500, 380)

        self.setStyleSheet("""
            QWidget {
                background-color: #2A2D32;
                color: white;
                font-size: 16px;
            }
            QLineEdit {
                background-color: #1B1E23;
                color: white;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton {
                background-color: #4A57FF;
                padding: 10px;
                border-radius: 5px;
            }
        """)

        layout = QVBoxLayout()
        title = QLabel("로그인")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 32px; margin-bottom: 20px;")
        layout.addWidget(title)

        self.username = QLineEdit(); self.username.setPlaceholderText("아이디")
        self.password = QLineEdit(); self.password.setPlaceholderText("비밀번호"); self.password.setEchoMode(QLineEdit.Password)
        self.auto_login = QCheckBox("자동 로그인"); self.auto_login.setStyleSheet("margin-bottom: 10px;")

        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(self.auto_login)

        login_btn = QPushButton("로그인")
        login_btn.clicked.connect(self.try_login)
        layout.addWidget(login_btn)

        join_btn = QPushButton("회원가입")
        join_btn.clicked.connect(self.open_join)
        layout.addWidget(join_btn)

        self.setLayout(layout)

    def try_login(self):
        data = { "username": self.username.text(), "password": self.password.text() }
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



# =========================================
# 회원가입
# =========================================
class JoinWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("회원가입")
        self.setGeometry(750, 350, 400, 300)

        layout = QVBoxLayout()
        self.username = QLineEdit(); self.username.setPlaceholderText("아이디")
        self.password = QLineEdit(); self.password.setPlaceholderText("비밀번호")
        self.nickname = QLineEdit(); self.nickname.setPlaceholderText("닉네임")

        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(self.nickname)

        btn = QPushButton("가입")
        btn.clicked.connect(self.join)
        layout.addWidget(btn)

        self.setLayout(layout)

    def join(self):
        data = {
            "username": self.username.text(),
            "password": self.password.text(),
            "nickname": self.nickname.text(),
        }

        res = requests.post(f"{SERVER_URL}/join", json=data).json()
        if res["success"]:
            QMessageBox.information(self, "완료", "가입 성공!")
            self.close()
        else:
            QMessageBox.warning(self, "오류", "이미 존재하는 계정")


# =========================================
# 메인 프로그램
# =========================================
class MainWindow(QWidget):
    def __init__(self, username, is_admin):
        super().__init__()
        self.username = username
        self.is_admin = is_admin

        self.setWindowTitle("장부 시스템")
        self.setGeometry(500, 200, 1200, 700)

        main_layout = QHBoxLayout()

        # 메뉴
        self.menu = QListWidget()
        self.menu.addItem("장부 작성")
        self.menu.addItem("장부 기록")
        if is_admin:
            self.menu.addItem("관리자 추가")
        self.menu.currentRowChanged.connect(self.change_page)

        # 페이지
        self.stack = QStackedWidget()
        self.stack.addWidget(self.page_write())
        self.stack.addWidget(self.page_records())
        if is_admin:
            self.stack.addWidget(self.page_admin())

        main_layout.addWidget(self.menu, 1)
        main_layout.addWidget(self.stack, 4)

        self.setLayout(main_layout)

    # -----------------------------------
    # 장부 작성
    def page_write(self):
        w = QWidget()
        layout = QVBoxLayout()

        self.code = QLineEdit(); self.code.setPlaceholderText("고유번호")
        self.nickname = QLineEdit(); self.nickname.setPlaceholderText("닉네임")
        self.item = QLineEdit(); self.item.setPlaceholderText("판매 항목")

        btn = QPushButton("작성하기")
        btn.clicked.connect(self.write_record)

        layout.addWidget(self.code)
        layout.addWidget(self.nickname)
        layout.addWidget(self.item)
        layout.addWidget(btn)

        w.setLayout(layout)
        return w

    # -----------------------------------
    # 장부 기록
    def page_records(self):
        w = QWidget()
        layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "시간", "고유번호", "닉네임", "항목"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        refresh = QPushButton("새로고침")
        refresh.clicked.connect(self.load_records)

        if self.is_admin:
            del_btn = QPushButton("선택 삭제")
            del_btn.clicked.connect(self.delete_record)
            layout.addWidget(del_btn)

        layout.addWidget(self.table)
        layout.addWidget(refresh)
        w.setLayout(layout)
        return w

    # -----------------------------------
    # 관리자 추가
    def page_admin(self):
        w = QWidget()
        layout = QVBoxLayout()

        self.admin_id = QLineEdit(); self.admin_id.setPlaceholderText("관리자 아이디")
        self.admin_pw = QLineEdit(); self.admin_pw.setPlaceholderText("비밀번호")
        self.admin_nick = QLineEdit(); self.admin_nick.setPlaceholderText("닉네임")

        btn = QPushButton("관리자 추가")
        btn.clicked.connect(self.add_admin)

        layout.addWidget(self.admin_id)
        layout.addWidget(self.admin_pw)
        layout.addWidget(self.admin_nick)
        layout.addWidget(btn)

        w.setLayout(layout)
        return w

    # -----------------------------------
    # 기능들
    def write_record(self):
        data = {
            "code": self.code.text(),
            "nickname": self.nickname.text(),
            "item": self.item.text(),
        }
        requests.post(f"{SERVER_URL}/add_record", json=data)
        QMessageBox.information(self, "완료", "등록 성공")

    def load_records(self):
        data = requests.get(f"{SERVER_URL}/get_records").json()
        self.table.setRowCount(len(data))

        for i, row in enumerate(data):
            self.table.setItem(i, 0, QTableWidgetItem(str(row["id"])))
            self.table.setItem(i, 1, QTableWidgetItem(row["time"]))
            self.table.setItem(i, 2, QTableWidgetItem(row["code"]))
            self.table.setItem(i, 3, QTableWidgetItem(row["nickname"]))
            self.table.setItem(i, 4, QTableWidgetItem(row["item"]))

    def delete_record(self):
        selected = self.table.currentRow()
        if selected < 0:
            return

        record_id = self.table.item(selected, 0).text()
        requests.post(f"{SERVER_URL}/delete_record", json={"id": record_id})

        QMessageBox.information(self, "삭제", "삭제 완료")
        self.load_records()

    def add_admin(self):
        data = {
            "username": self.admin_id.text(),
            "password": self.admin_pw.text(),
            "nickname": self.admin_nick.text(),
            "is_admin": True
        }
        requests.post(f"{SERVER_URL}/join", json=data)
        QMessageBox.information(self, "추가", "관리자 추가 완료")


# =========================================
# 실행
# =========================================
app = QApplication(sys.argv)
w = LoginWindow()
w.show()
sys.exit(app.exec_())
