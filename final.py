import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QVBoxLayout, QLabel, QTableWidgetItem
from design import Ui_MainWindow

conn = sqlite3.connect('movies_database.sqlite3')
cursor = conn.cursor()
class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.tabWidget.currentChanged.connect(self.on_tab_changed)

        # ღილაკებზე ქმედებების მიბმა
        self.ui.pushButton.clicked.connect(self.search_by_genre)
        self.ui.pushButton_2.clicked.connect(self.delete_movie)
        self.ui.pushButton_3.clicked.connect(self.add_movie)
        self.ui.pushButton_4.clicked.connect(self.update_description)

        self.populate_comboboxes()


    def search_by_genre(self):
        selected_items = self.ui.listWidget.selectedItems()
        if not selected_items:
            self.show_dialog("შეტყობინება", "გთხოვთ აირჩიოთ ერთი ან რამდენიმე ჟანრი")
            return

        genres = [item.text() for item in selected_items]

        # ვაგენერირებთ მრავალ ჟანრზე მოთხოვნას
        placeholders = " OR ".join(["Genres LIKE ?"] * len(genres))
        query = f"SELECT DISTINCT Film_title FROM Letterbox WHERE {placeholders}"
        values = [f"%{genre}%" for genre in genres]
        result = cursor.execute(query, values).fetchall()

        if result:
            titles = "\n".join([r[0] for r in result])
            genre_list = ", ".join(genres)
            message = f"არჩეული ჟანრები: {genre_list}\n\nნაპოვნია ფილმები:\n{titles}"
            self.show_dialog("ნაპოვნია", message)
        else:
            self.show_dialog("შედეგი", "ფილმები არჩეული ჟანრებით ვერ მოიძებნა")

    def on_tab_changed(self, index):
        if index == 1:  # თუ მეორე ტაბზე გადავიდა
            self.load_database_into_table()


    def load_database_into_table(self):
        cursor.execute("SELECT * FROM Letterbox")
        data = cursor.fetchall()
        headers = [description[0] for description in cursor.description]

        table = self.ui.tableWidget
        table.clear()
        table.setRowCount(len(data))
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)

        for row_idx, row_data in enumerate(data):
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                table.setItem(row_idx, col_idx, item)

        table.resizeColumnsToContents()

    def show_dialog(self, title, text):
        dialog = QDialog(self)
        dialog.setWindowTitle(title)

        layout = QVBoxLayout()
        label = QLabel(text)
        label.setWordWrap(True)
        layout.addWidget(label)

        dialog.setLayout(layout)
        dialog.resize(400, 300)
        dialog.exec_()

    def delete_movie(self):
        name = self.ui.comboBox.currentText().strip()
        if not name:
            self.ui.label_8.setText("შეიყვანეთ წასაშლელი ფილმის სახელი")
        else:
            cursor.execute("DELETE FROM Letterbox WHERE Film_title = ?", (name,))
            conn.commit()
            self.ui.label_8.setText(f"წაიშალა ფილმი: {name}")
            self.populate_comboboxes()

    def populate_comboboxes(self):
        titles = cursor.execute("SELECT Film_title FROM Letterbox").fetchall()
        self.ui.comboBox.clear()
        self.ui.comboBox_2.clear()
        for t in titles:
            self.ui.comboBox.addItem(t[0])
            self.ui.comboBox_2.addItem(t[0])

    def add_movie(self):
        title = self.ui.lineEdit_2.text().strip()
        desc = self.ui.lineEdit_3.text().strip()
        if not title:
            self.ui.label_6.setText("შეიყვანეთ ფილმის სახელი")
        else:
            cursor.execute("INSERT INTO Letterbox (Film_title, Description) VALUES (?, ?)", (title, desc))
            conn.commit()
            self.ui.label_6.setText("ფილმი დაემატა!")
            self.populate_comboboxes()

    def update_description(self):
        title = self.ui.comboBox_2.currentText().strip()
        new_desc = self.ui.lineEdit_5.text().strip()
        if not title or not new_desc:
            self.ui.label_9.setText("გთხოვთ შეავსოთ ორივე ველი")
        else:
            cursor.execute("UPDATE Letterbox SET Description = ? WHERE Film_title = ?", (new_desc, title))
            conn.commit()
            self.ui.label_9.setText("აღწერა შეიცვალა!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    exit_code = app.exec_()
    conn.close()
    sys.exit(exit_code)

