import sys
import requests
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

SERVER_URL = "https://accomplished-endurance-production.up.railway.app/"

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AOI 시스템 로그인")
        self.setFixedSize(380, 300)
        self.setStyleSheet("background-color: #1c1c1c; color: white;")

        layout = QVBoxLayout()

        title = QLabel("AOI 시스템")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; margin-top: 10px;")
        layout.addWidget(title)

        self.username = QLineEdit()
        self.username.setPlaceholderText("아이디")
        layout.addWidget(self.username)

        self.password = QLineEdit()
        self.password.setPlaceholderText("비밀번호")
        self.password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password)

        btn_login = QPushButton("로그인")
        btn_login.clicked.connect(self.login)
        layout.addWidget(btn_login)

        btn_register = QPushButton("회원가입")
        btn_register.clicked.connect(self.open_register)
        layout.addWidget(btn_register)

        self.setLayout(layout)

    def open_register(self):
        self.reg = RegisterWindow()
        self.reg.show()

    def login(self):
        data = {
            "username": self.username.text(),
            "password": self.password.text()
        }

        r = requests.post(SERVER_URL + "login", json=data).json()

        if r["success"]:
            if r.get("admin", False):
                self.close()
                self.admin = AdminMainWindow()
                self.admin.show()
            else:
                self.close()
                self.main = MainWindow()
                self.main.show()
        else:
            QMessageBox.warning(self, "오류", "로그인 실패")


class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("회원가입")
        self.setFixedSize(350, 260)
        self.setStyleSheet("background-color:#222; color:white;")
        layout = QVBoxLayout()

        self.username = QLineEdit()
        self.username.setPlaceholderText("새 아이디")
        layout.addWidget(self.username)

        self.password = QLineEdit()
        self.password.setPlaceholderText("새 비밀번호")
        self.password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password)

        btn = QPushButton("가입하기")
        btn.clicked.connect(self.register)
        layout.addWidget(btn)

        self.setLayout(layout)

    def register(self):
        data = {
            "username": self.username.text(),
            "password": self.password.text()
        }

        r = requests.post(SERVER_URL + "register", json=data).json()

        if r["success"]:
            QMessageBox.information(self, "완료", "가입 성공")
            self.close()
        else:
            QMessageBox.warning(self, "오류", "이미 존재하는 아이디입니다.")


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AOI 메인")
        self.setFixedSize(750, 550)

        layout = QHBoxLayout()

        self.menu = QListWidget()
        self.menu.addItem("장부 작성")
        self.menu.addItem("장부 기록")
        self.menu.clicked.connect(self.menu_clicked)

        layout.addWidget(self.menu)

        self.stacked = QStackedWidget()
        self.page_write = WritePage()
        self.page_records = RecordPage()
        self.stacked.addWidget(self.page_write)
        self.stacked.addWidget(self.page_records)

        layout.addWidget(self.stacked)
        self.setLayout(layout)

    def menu_clicked(self):
        idx = self.menu.currentRow()
        self.stacked.setCurrentIndex(idx)


class WritePage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.code = QLineEdit()
        self.code.setPlaceholderText("고유번호")
        layout.addWidget(self.code)

        self.nickname = QLineEdit()
        self.nickname.setPlaceholderText("닉네임")
        layout.addWidget(self.nickname)

        self.item = QLineEdit()
        self.item.setPlaceholderText("판매한 물품")
        layout.addWidget(self.item)

        btn = QPushButton("장부 저장")
        btn.clicked.connect(self.save)
        layout.addWidget(btn)

        self.setLayout(layout)

    def save(self):
        data = {
            "code": self.code.text(),
            "nickname": self.nickname.text(),
            "item": self.item.text()
        }

        r = requests.post(SERVER_URL + "add_record", json=data).json()

        if r["success"]:
            QMessageBox.information(self, "완료", "저장됨")
        else:
            QMessageBox.warning(self, "오류", "저장 실패")


class RecordPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["시간", "고유번호", "닉네임", "물품"])
        layout.addWidget(self.table)

        btn = QPushButton("새로고침")
        btn.clicked.connect(self.load)
        layout.addWidget(btn)

        self.setLayout(layout)
        self.load()

    def load(self):
        r = requests.get(SERVER_URL + "get_records").json()
        self.table.setRowCount(len(r))

        for i, row in enumerate(r):
            for j, col in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(col)))


### -------------------------
### 🟥 관리자 메인 화면
### -------------------------
class AdminMainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AOI 관리자 시스템")
        self.setFixedSize(800, 600)

        layout = QHBoxLayout()

        self.menu = QListWidget()
        self.menu.addItem("장부 기록 전체보기")
        self.menu.addItem("관리자 추가")
        self.menu.clicked.connect(self.menu_clicked)

        layout.addWidget(self.menu)

        self.stacked = QStackedWidget()
        self.page_records = RecordPage()
        self.page_admin_add = AdminAddPage()
        self.stacked.addWidget(self.page_records)
        self.stacked.addWidget(self.page_admin_add)

        layout.addWidget(self.stacked)
        self.setLayout(layout)

    def menu_clicked(self):
        self.stacked.setCurrentIndex(self.menu.currentRow())


class AdminAddPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.username = QLineEdit()
        self.username.setPlaceholderText("관리자 아이디")
        layout.addWidget(self.username)

        self.password = QLineEdit()
        self.password.setPlaceholderText("관리자 비밀번호")
        layout.addWidget(self.password)

        btn = QPushButton("관리자 추가")
        btn.clicked.connect(self.add_admin)
        layout.addWidget(btn)

        self.setLayout(layout)

    def add_admin(self):
        data = {
            "username": self.username.text(),
            "password": self.password.text(),
            "admin": True
        }

        r = requests.post(SERVER_URL + "admin/add", json=data).json()

        if r["success"]:
            QMessageBox.information(self, "완료", "관리자 추가됨")
        else:
            QMessageBox.warning(self, "오류", "추가 실패 (ID 중복?)")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = LoginWindow()
    win.show()
    sys.exit(app.exec_())
