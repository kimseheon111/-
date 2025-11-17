import sys
import requests
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

SERVER_URL = "https://accomplished-endurance-production.up.railway.app/"

class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("회원가입")
        self.setFixedSize(350, 350)

        layout = QVBoxLayout()

        title = QLabel("회원가입")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; color: white;")
        layout.addWidget(title)

        self.username = QLineEdit()
        self.username.setPlaceholderText("아이디")
        layout.addWidget(self.username)

        self.password = QLineEdit()
        self.password.setPlaceholderText("비밀번호")
        self.password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password)

        btn = QPushButton("회원가입 완료")
        btn.clicked.connect(self.register)
        layout.addWidget(btn)

        self.setLayout(layout)
        self.setStyleSheet("background-color: #2f2f2f; color: white;")

    def register(self):
        data = {
            "username": self.username.text(),
            "password": self.password.text()
        }

        r = requests.post(SERVER_URL + "register", json=data).json()

        if r["success"]:
            QMessageBox.information(self, "성공", "회원가입 완료")
            self.close()
        else:
            QMessageBox.warning(self, "실패", "이미 있는 아이디입니다.")


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("아오이 인트라넷 로그인")
        self.setFixedSize(350, 300)

        layout = QVBoxLayout()

        title = QLabel("AOI INTRANET")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; color: white;")
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
        self.setStyleSheet("background-color: #2f2f2f; color: white;")

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
            self.close()
            self.main = MainWindow()
            self.main.show()
        else:
            QMessageBox.warning(self, "오류", "로그인 실패")


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("아오이 장부 시스템")
        self.setFixedSize(700, 500)

        layout = QHBoxLayout()
        self.menu = QListWidget()
        self.menu.addItem("장부 작성")
        self.menu.addItem("장부 기록")
        self.menu.clicked.connect(self.menu_clicked)
        layout.addWidget(self.menu)

        self.stacked = QStackedWidget()
        self.write_page = WritePage()
        self.record_page = RecordPage()

        self.stacked.addWidget(self.write_page)
        self.stacked.addWidget(self.record_page)

        layout.addWidget(self.stacked)
        self.setLayout(layout)

    def menu_clicked(self):
        self.stacked.setCurrentIndex(self.menu.currentRow())


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
        self.item.setPlaceholderText("판매한 물건")
        layout.addWidget(self.item)

        btn = QPushButton("장부 저장")
        btn.clicked.connect(self.add_record)
        layout.addWidget(btn)

        self.setLayout(layout)

    def add_record(self):
        data = {
            "code": self.code.text(),
            "nickname": self.nickname.text(),
            "item": self.item.text()
        }

        r = requests.post(SERVER_URL + "add_record", json=data).json()

        if r["success"]:
            QMessageBox.information(self, "완료", "장부 저장 완료")
        else:
            QMessageBox.warning(self, "오류", "저장 실패")


class RecordPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["시간", "고유번호", "닉네임", "판매 물건"])
        layout.addWidget(self.table)

        btn = QPushButton("새로고침")
        btn.clicked.connect(self.load_records)
        layout.addWidget(btn)

        self.setLayout(layout)
        self.load_records()

    def load_records(self):
        r = requests.get(SERVER_URL + "get_records").json()
        self.table.setRowCount(len(r))

        for i, row in enumerate(r):
            for j, col in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(col)))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = LoginWindow()
    win.show()
    sys.exit(app.exec_())
