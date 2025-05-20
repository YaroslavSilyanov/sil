import  pymysql

def get_db_connection():
    return pymysql.connect(
        host = "localhost",
        user = "root",
        password = "",
        database = "fabrik",
        cursorclass = pymysql.cursors.DictCursor
    )




from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QFormLayout, QPushButton, QMessageBox, QLabel
from PyQt6.QtCore import Qt

from db import get_db_connection


class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()

        # Настройка основного окна
        self.setWindowTitle("Авторизация")
        self.setFixedSize(200, 200)
        self.setWindowIcon(QIcon("aaa.png"))
        self.setStyleSheet("background-color: #FFFFFF; font-family: Segoe UI")

        layout = QVBoxLayout(self)

        # Создание и настройка логотипа
        logo = QLabel()
        logo.setPixmap(QPixmap("aaa.png").scaled(150, 50, Qt.AspectRatioMode.KeepAspectRatio))
        layout.addWidget(logo, alignment=Qt.AlignmentFlag.AlignCenter)

        # Поля для ввода логина и пароля
        self.login = QLineEdit()
        self.passw = QLineEdit()
        self.passw.setEchoMode(QLineEdit.EchoMode.Password)

        # Форма для полей ввода
        form = QFormLayout()
        form.addRow("Логин:", self.login)
        form.addRow("Пароль:", self.passw)
        layout.addLayout(form)

        # Кнопка входа
        btn = QPushButton("Войти")
        btn.clicked.connect(self.verifi)
        layout.addWidget(btn)

        btn.setStyleSheet("background: #67BA80; color: white; padding: 5px;")

    #Метод для проверки авторизации пользователя
    def verifi(self):
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("select login, password from manager where login = %s and password = %s",
                                (self.login.text(), self.passw.text()))
                    if cur.fetchone():
                        self.accept()
                    else:
                        QMessageBox.critical(self, "Ошибка", "Неправильный логин или пароль, возможно вы не заполнили поля")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка базы данных:{e}")











from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QHBoxLayout, QPushButton, QTableWidgetItem, QMessageBox, \
    QLabel
from PyQt6.QtCore import Qt


from add_product import AddProduct
from db import get_db_connection
from ceh import Ceh


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        #Настройка основного окна
        self.setWindowTitle("Главное окно продукции")
        self.setFixedSize(900, 600)
        self.setWindowIcon(QIcon("aaa.png"))
        self.setStyleSheet("background-color: #FFFFFF; font-family: Segoe UI")

        layout = QVBoxLayout(self)

        #Добавление логотипа
        logo = QLabel()
        logo.setPixmap(QPixmap("aaa.png").scaled(150, 50, Qt.AspectRatioMode.KeepAspectRatio))
        layout.addWidget(logo, alignment=Qt.AlignmentFlag.AlignCenter)

        #Создание таблицы для отображения продукции
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["Номер продукта", "Название", "Тип продукта", "Артикул", "Мин. цена для партнера", "Тип материала", "Время изготовления"])
        layout.addWidget(self.table)

        btn_la = QHBoxLayout()

        #Создание кнопок для управления
        add_pr = QPushButton("Добавить продукт")
        dlt_pr = QPushButton("Удалить продукт")
        edit_pr = QPushButton("Редактировать продукт")
        ceh = QPushButton("Посмотреть цеха")

        add_pr.clicked.connect(self.add_pr)
        dlt_pr.clicked.connect(self.dlt_pr)
        edit_pr.clicked.connect(self.edit_pr)
        ceh.clicked.connect(self.ceh)

        btn_la.addWidget(add_pr)
        btn_la.addWidget(dlt_pr)
        btn_la.addWidget(edit_pr)
        btn_la.addWidget(ceh)

        add_pr.setStyleSheet("background: #67BA80; color: white; padding: 5px;")
        dlt_pr.setStyleSheet("background: #67BA80; color: white; padding: 5px;")
        edit_pr.setStyleSheet("background: #2196F3; color: white; padding: 5px;")
        ceh.setStyleSheet("background: #67BA80; color: white; padding: 5px;")

        layout.addLayout(btn_la)

        #Загрузка данных в таблицу
        self.load()

    #Метод для редактирования выбранного продукта
    def edit_pr(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите продукт для редактирования")
            return

        product_id = self.table.item(selected_row, 0).text()

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""SELECT * FROM product WHERE id = %s""", (product_id,))
                    product_data = cur.fetchone()

                    if not product_data:
                        QMessageBox.warning(self, "Ошибка", "Продукт не найден")
                        return

                    dialog = AddProduct()
                    dialog.name.setText(product_data['name'])
                    dialog.articul.setText(product_data['articul'])
                    dialog.min.setText(product_data['min_cena'])

                    for i in range(dialog.tip_pr.count()):
                        if dialog.tip_pr.itemData(i) == product_data['tip_product']:
                            dialog.tip_pr.setCurrentIndex(i)
                            break

                    for i in range(dialog.tip_mat.count()):
                        if dialog.tip_mat.itemData(i) == product_data['tip_material']:
                            dialog.tip_mat.setCurrentIndex(i)
                            break

                    for i in range(dialog.ceh.count()):
                        if dialog.ceh.itemData(i) == product_data['ceh_id']:
                            dialog.ceh.setCurrentIndex(i)
                            break

                    if dialog.exec():
                        if dialog.success:
                            name, tip_pr, articul, min_cena, tip_mat, ceh = dialog.get_data()
                            cur.execute("""UPDATE product SET 
                                        name = %s, 
                                        tip_product = %s, 
                                        articul = %s, 
                                        min_cena = %s, 
                                        tip_material = %s, 
                                        ceh_id = %s 
                                        WHERE id = %s""",
                                        (name, tip_pr, articul, min_cena, tip_mat, ceh, product_id))
                            conn.commit()
                            self.load()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка базы данных: {e}")

    #Метод для открытия окна управления цехами
    def ceh(self):
        window = Ceh()
        window.exec()

    #Метод загрузки данных о продукции в таблицу
    def load(self):
        self.table.setRowCount(0)
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""select p.id, p.name, tp.name_product, p.articul, p.min_cena, m.name_material, c.vremya
                    from product p
                    join tip_product tp on p.tip_product = tp.id
                    join material m on p.tip_material = m.id
                    join ceh c on p.ceh_id = c.id""")
                    for row in cur.fetchall():
                        row_pos = self.table.rowCount()
                        self.table.insertRow(row_pos)
                        self.table.setItem(row_pos, 0, QTableWidgetItem(str(row["id"])))
                        self.table.setItem(row_pos, 1, QTableWidgetItem(row["name"]))
                        self.table.setItem(row_pos, 2, QTableWidgetItem(row["name_product"]))
                        self.table.setItem(row_pos, 3, QTableWidgetItem(row["articul"]))
                        self.table.setItem(row_pos, 4, QTableWidgetItem(row["min_cena"]))
                        self.table.setItem(row_pos, 5, QTableWidgetItem(row["name_material"]))
                        self.table.setItem(row_pos, 6, QTableWidgetItem(row["vremya"]))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка базы данных:{e}")

    #Метод для добавления нового продукта
    def add_pr(self):
        dialog = AddProduct()
        if dialog.exec():
            if dialog.success:
                name, tip_pr, articul, min_cena, tip_mat, ceh = dialog.get_data()
                try:
                    with get_db_connection() as conn:
                        with conn.cursor() as cur:
                            cur.execute("insert into product(name, tip_product, articul, min_cena, tip_material, ceh_id) values(%s, %s, %s, %s, %s, %s)",
                                        (name, tip_pr, articul, min_cena, tip_mat, ceh))
                            conn.commit()
                            self.load()
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка", f"Ошибка базы данных:{e}")

    #Метод для удаления продукта
    def dlt_pr(self):
        scrld = self.table.currentRow()
        if scrld >=0:
            try:
                id = self.table.item(scrld, 0).text()
                with get_db_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute("delete from product where id = %s", (id, ))
                        conn.commit()
                        self.load()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка базы данных:{e}")








from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QVBoxLayout, QTableWidget, QHBoxLayout, QPushButton, QTableWidgetItem, QMessageBox, \
    QDialog

from add_ceh import AddCeh
from db import get_db_connection


class Ceh(QDialog):
    def __init__(self):
        super().__init__()

        #Настройка основного окна
        self.setWindowTitle("Окно цехов")
        self.setFixedSize(500, 400)
        self.setWindowIcon(QIcon("aaa.png"))
        self.setStyleSheet("background-color: #FFFFFF; font-family: Segoe UI")

        layout = QVBoxLayout(self)

        #Создание таблицы для отображения цехов
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels (["Номер цеха", "Название цеха", "Количество человек", "Время затраченное на реализацию"])
        layout.addWidget(self.table)

        btn_la = QHBoxLayout()

        #Создание кнопок управления
        add_c = QPushButton("Добавить цех")
        dlt_c = QPushButton("Удалить цех")
        edit_c = QPushButton("Редактировать цех")

        add_c.clicked.connect(self.add_c)
        dlt_c.clicked.connect(self.dlt_c)
        edit_c.clicked.connect(self.edit_c)

        add_c.setStyleSheet("background: #67BA80; color: white; padding: 5px;")
        dlt_c.setStyleSheet("background: #67BA80; color: white; padding: 5px;")
        edit_c.setStyleSheet("background: #2196F3; color: white; padding: 5px;")

        btn_la.addWidget(add_c)
        btn_la.addWidget(dlt_c)
        btn_la.addWidget(edit_c)

        layout.addLayout(btn_la)

        #Загрузка данных в таблицу
        self.load()

    #Метод для редактирования выбранного цеха
    def edit_c(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите цех для редактирования")
            return

        ceh_id = self.table.item(selected_row, 0).text()

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""SELECT * FROM ceh WHERE id = %s""", (ceh_id,))
                    ceh_data = cur.fetchone()

                    if not ceh_data:
                        QMessageBox.warning(self, "Ошибка", "Цех не найден")
                        return

                    dialog = AddCeh()
                    dialog.name.setText(ceh_data['name_ceh'])
                    dialog.chelovek.setText(ceh_data['chelovek'])
                    dialog.vremya.setText(ceh_data['vremya'])

                    if dialog.exec():
                        if dialog.success:
                            name, chelovek, vremya = dialog.get_data()
                            cur.execute("""UPDATE ceh SET 
                                        name_ceh = %s, 
                                        chelovek = %s, 
                                        vremya = %s 
                                        WHERE id = %s""",
                                        (name, chelovek, vremya, ceh_id))
                            conn.commit()
                            self.load()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка базы данных: {e}")

    #Метод загрузки данных о цехах в таблицу
    def load(self):
        self.table.setRowCount(0)
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""select c.id, c.name_ceh, c.chelovek, c.vremya
                    from ceh c""")
                    for row in cur.fetchall():
                        row_pos = self.table.rowCount()
                        self.table.insertRow(row_pos)
                        self.table.setItem(row_pos, 0, QTableWidgetItem(str(row["id"])))
                        self.table.setItem(row_pos, 1, QTableWidgetItem(row["name_ceh"]))
                        self.table.setItem(row_pos, 2, QTableWidgetItem(row["chelovek"]))
                        self.table.setItem(row_pos, 3, QTableWidgetItem(row["vremya"]))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка базы данных:{e}")

    #Метод для добавления нового цеха
    def add_c(self):
        dialog = AddCeh()
        if dialog.exec():
            if dialog.success:
                name, chelovek, vremya  = dialog.get_data()
                try:
                    with get_db_connection() as conn:
                        with conn.cursor() as cur:
                            cur.execute ("insert into ceh(name_ceh, chelovek, vremya) values(%s, %s, %s)",
                                        (name, chelovek, vremya))
                            conn.commit()
                            self.load()
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка", f"Ошибка базы данных:{e}")

    #Метод для удаления цеха
    def dlt_c(self):
        scrld = self.table.currentRow()
        if scrld >=0:
            try:
                id = self.table.item(scrld, 0).text()
                with get_db_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute("delete from ceh where id = %s", (id,))
                        conn.commit()
                        self.load()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка базы данных:{e}")






                

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QLabel, QPushButton, QMessageBox


class AddCeh(QDialog):
    def __init__(self):
        super().__init__()

        # Настройка основного окна
        self.setWindowTitle("Добавление цеха")
        self.setFixedSize(500, 500)
        self.setWindowIcon(QIcon("aaa.png"))
        self.setStyleSheet("background-color: #FFFFFF; font-family: Segoe UI")

        layout = QVBoxLayout(self)

        # Создание полей ввода
        self.name = QLineEdit()
        self.chelovek = QLineEdit()
        self.vremya = QLineEdit()

        # Добавление подписей и полей ввода в layout
        layout.addWidget(QLabel("Введите название цеха:"))
        layout.addWidget(self.name)

        layout.addWidget(QLabel("Введите количество человек в цеху:"))
        layout.addWidget(self.chelovek)

        layout.addWidget(QLabel("Введите время на создание в минутах:"))
        layout.addWidget(self.vremya)

        # Создание и настройка кнопки сохранения
        btn = QPushButton("Сохранить")
        btn.clicked.connect(self.save)
        layout.addWidget(btn)
        btn.setStyleSheet("background: #67BA80; color: white; padding: 5px;")

        # Флаг успешного сохранения
        self.success = False

    def save(self):
        # Проверка, что все поля заполнены
        if not self.name.text() or not self.chelovek.text() or not self.vremya.text():
            QMessageBox.critical(self, "Ошибка заполнения полей", "Заполните все поля")
            return

        self.success = True

        self.accept()

    def get_data(self):
        return (
            self.name.text(),
            self.chelovek.text(),
            self.vremya.text()
        )





from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QComboBox, QLabel, QPushButton, QMessageBox


from db import get_db_connection


class AddProduct(QDialog):
    def __init__(self):
        super().__init__()

        # Настройка основного окна
        self.setWindowTitle("Добавление продукта")
        self.setFixedSize(300, 300)
        self.setWindowIcon(QIcon("aaa.png"))
        self.setStyleSheet("background-color: #FFFFFF; font-family: Segoe UI")

        layout = QVBoxLayout(self)

        # Создание полей ввода и выбора
        self.name = QLineEdit()
        self.tip_pr = QComboBox()
        self.articul = QLineEdit()
        self.min = QLineEdit()
        self.tip_mat = QComboBox()
        self.ceh = QComboBox()

        #Заполнение выпадающих списков
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("select id, name_product from tip_product")
                for row in cur.fetchall():
                    self.tip_pr.addItem(row["name_product"], row["id"])

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("select id, name_material from material")
                for row in cur.fetchall():
                    self.tip_mat.addItem(row["name_material"], row["id"])

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("select id, name_ceh from ceh")
                for row in cur.fetchall():
                    self.ceh.addItem(row["name_ceh"], row["id"])

        # Добавление элементов в layout с подписями
        layout.addWidget(QLabel("Введите название продукта:"))
        layout.addWidget(self.name)

        layout.addWidget(QLabel("Выберите тип родукта:"))
        layout.addWidget(self.tip_pr)

        layout.addWidget(QLabel("Введите артикул:"))
        layout.addWidget(self.articul)

        layout.addWidget(QLabel("Введите минимальную стоимость для партнера:"))
        layout.addWidget(self.min)

        layout.addWidget(QLabel("Выберите тип материала:"))
        layout.addWidget(self.tip_mat)

        layout.addWidget(QLabel("Выберите цех изготовитель:"))
        layout.addWidget(self.ceh)

        # Кнопка сохранения
        btn = QPushButton("Сохранить")
        btn.clicked.connect(self.save)

        btn.setStyleSheet("background: #67BA80; color: white; padding: 5px;")

        layout.addWidget(btn)

        self.success = False

    def save(self):
        # Проверка, что все поля заполнены
        if not self.name.text() or not self.articul.text() or not self.min.text():
            QMessageBox.critical(self, "Ошибка заполнения полей", "Заполните все поля")
            return
        self.success = True
        self.accept()

    def get_data(self):
        return(
            self.name.text(),
            self.tip_pr.currentData(),
            self.articul.text(),
            self.min.text(),
            self.tip_mat.currentData(),
            self.ceh.currentData()
        )








import sys

from PyQt6.QtWidgets import QApplication

from login_dialog import LoginDialog
from main_window import MainWindow

app = QApplication(sys.argv)
login = LoginDialog()
if login.exec():
    window = MainWindow()
    window.show()
    sys.exit(app.exec())



pip install pyinstaller
pyinstaller --onefile --windowed main.py
