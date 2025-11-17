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
        self.setGeometry(700, 300, 500, 350)

        self.setStyleSheet("""
            QWidget { background-color: #2A2D32; color: white; font-size: 16px; }
            QLineEdit {
                background-color: #1B1E23; color: white;
                padding: 10px; border-radius: 5px;
            }
            QPushButton {
                background-color: #4A57FF; color: white;
                padding: 12px; border-radius: 5px;
            }
        """)

        layout = QVBoxLayout()
        title = QLabel("로그인")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 32px; margin-bottom: 20px;")
        layout.addWidget(title)

        self.username = QLineEdit(); self.username.setPlaceholderText("아이디")
        self.password = QLineEdit(); self.password.setEchoMode(QLineEdit.Password); self.password.setPlaceholderText("비밀번호")

        layout.addWidget(self.username)
        layout.addWidget(self.password)

        self.login_btn = QPushButton("로그인")
        self.login_btn.clicked.connect(self.try_login)
        layout.addWidget(self.login_btn)

        self.join_btn = QPushButton("회원가입")
        self.join_btn.clicked.connect(self.open_join)
        layout.addWidget(self.join_btn)

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


# =========================================
#  회원가입 UI
# =========================================
class JoinWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("회원가입")
        self.setGeometry(750, 350, 400, 300)

        self.setStyleSheet("""
            QWidget { background-color: #2A2D32; color: white; }
            QLineEdit { background-color: #1B1E23; color: white; padding: 8px; border-radius: 5px; }
            QPushButton { background-color: #4A57FF; color:white; padding:10px; border-radius: 5px; }
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
            "nickname": self.nickname.text(),
        }
        res = requests.post(f"{SERVER_URL}/join", json=data).json()

        if res["success"]:
            QMessageBox.information(self, "알림", "가입 완료!")
            self.close()
        else:
            QMessageBox.warning(self, "오류", "이미 존재하는 계정입니다.")


# =========================================
#  메인 UI
# =========================================
class MainWindow(QWidget):
    def __init__(self, username, is_admin):
        super().__init__()
        self.username = username
        self.is_admin = is_admin

        self.setWindowTitle("장부 시스템")
        self.setGeometry(450, 150, 1200, 700)

        self.setStyleSheet("""
            QWidget { background-color: #2A2D32; color: white; font-size: 15px; }
            QListWidget { background-color: #1B1E23; color: white; font-size: 16px; min-width:200px; }
            QLineEdit { background-color: #1B1E23; color: white; padding: 10px; border-radius: 5px; }
            QPushButton { background-color: #4A57FF; color:white; padding:15px; border-radius: 5px; }
            QTableWidget { background-color: #1B1E23; color:white; }
            QHeaderView::section { background-color:#111217; color:white; }
        """)

        main = QHBoxLayout()

        # 좌측 메뉴
        self.menu = QListWidget()
        self.menu.addItem("장부 작성")
        self.menu.addItem("장부 기록")
        self.menu.addItem("관리자 추가")
        self.menu.currentRowChanged.connect(self.change_page)

        self.stack = QStackedWidget()

        self.stack.addWidget(self.page_write_ui())
        self.stack.addWidget(self.page_records_ui())
        self.stack.addWidget(self.page_admin_ui())

        main.addWidget(self.menu)
        main.addWidget(self.stack)
        self.setLayout(main)

    # ===========================
    # 페이지들
    # ===========================
    def page_write_ui(self):
        w = QWidget()
        layout = QVBoxLayout()

        self.nick = QLineEdit(); self.nick.setPlaceholderText("닉네임")
        self.item = QLineEdit(); self.item.setPlaceholderText("판매 항목")

        btn = QPushButton("작성하기")
        btn.clicked.connect(self.write_record)

        layout.addWidget(self.nick)
        layout.addWidget(self.item)
        layout.addWidget(btn)
        w.setLayout(layout)
        return w

    def page_records_ui(self):
        w = QWidget()
        layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "시간", "닉네임", "항목"])

        # 관리자일 때만 삭제 버튼
        if self.is_admin:
            del_btn = QPushButton("선택 항목 삭제")
            del_btn.clicked.connect(self.delete_record)
            layout.addWidget(del_btn)

        refresh_btn = QPushButton("새로고침")
        refresh_btn.clicked.connect(self.load_records)

        layout.addWidget(self.table)
        layout.addWidget(refresh_btn)
        w.setLayout(layout)
        return w

    def page_admin_ui(self):
        w = QWidget()
        layout = QVBoxLayout()

        if not self.is_admin:
            layout.addWidget(QLabel("관리자만 접근 가능합니다."))
            w.setLayout(layout)
            return w

        self.admin_user = QLineEdit(); self.admin_user.setPlaceholderText("관리자 아이디")
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

    # ===========================
    # 기능들
    # ===========================
    def change_page(self, idx):
        self.stack.setCurrentIndex(idx)

    def write_record(self):
        data = {
            "username": self.username,
            "nickname": self.nick.text(),
            "item": self.item.text(),
        }
        requests.post(f"{SERVER_URL}/add_record", json=data)
        QMessageBox.information(self, "알림", "작성 완료!")

    def load_records(self):
        res = requests.get(f"{SERVER_URL}/get_records").json()
        self.table.setRowCount(len(res))

        for r, row in enumerate(res):
            self.table.setItem(r, 0, QTableWidgetItem(str(row["id"])))
            self.table.setItem(r, 1, QTableWidgetItem(row["time"]))  
            self.table.setItem(r, 2, QTableWidgetItem(row["nickname"]))
            self.table.setItem(r, 3, QTableWidgetItem(row["item"]))

        self.table.resizeColumnsToContents()

    def delete_record(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "오류", "삭제할 항목을 선택하세요.")
            return

        record_id = self.table.item(row, 0).text()

        requests.post(f"{SERVER_URL}/delete_record", json={"id": record_id})
        QMessageBox.information(self, "알림", "삭제 완료!")

        self.load_records()

    def add_admin(self):
        data = {
            "username": self.admin_user.text(),
            "password": self.admin_pass.text(),
            "nickname": self.admin_nick.text(),
            "is_admin": True
        }
        res = requests.post(f"{SERVER_URL}/join", json=data).json()

        if res["success"]:
            QMessageBox.information(self, "알림", "관리자 추가 완료!")
        else:
            QMessageBox.warning(self, "오류", "이미 존재하는 아이디입니다.")


# =========================================
# 실행
# =========================================
app = QApplication(sys.argv)
win = LoginWindow()
win.show()
sys.exit(app.exec_())
