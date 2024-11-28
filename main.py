import math
import sys

import matplotlib.pyplot as plt
from PIL import Image
from PyQt6 import QtWidgets
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QMessageBox
from matplotlib import ticker
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from main_window import Ui_MainWindow

alphabet = 'абвгдеёжзийклмнопрстуфхцчшщьыъэюя'


def setup_table(table: QtWidgets.QTableWidget, columns: int, rows: int, list_headers: list):
    """setup_table(table, columns, rows, list_headers) инициализирует таблицу table
        с columns стоблцами и rows рядами, а также с заголовками столбцов list_headers
    """
    table.setEnabled(True)
    table.setRowCount(0)
    table.setColumnCount(columns)
    table.setRowCount(rows)
    table.setHorizontalHeaderLabels(list_headers)
    for i in range(columns):
        (table.horizontalHeader().
         setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeMode.ResizeToContents))
    table.horizontalHeader().setStretchLastSection(True)


class PlotWidget(FigureCanvas):
    """График"""

    def __init__(self, parent=None):
        fig = plt.figure(figsize=(5, 5))
        super(PlotWidget, self).__init__(fig)
        self.ax = fig.add_subplot(111)
        self.setParent(parent)

    def plot(self, probabilities, title):
        """plot(text) отображает график с частотным анализом текста text"""
        self.ax.clear()

        sorted_letters = sorted(probabilities.keys())
        sorted_counts = [probabilities[letter] for letter in sorted_letters]

        plt.bar(sorted_letters, sorted_counts, color='skyblue')
        ax = plt.gca()
        ax.yaxis.set_major_locator(ticker.MultipleLocator(0.01))
        plt.ylabel("Вероятность")

        plt.title(title)
        plt.grid(axis='y')

        y = [round(probabilities[x], 2) for x in probabilities]
        for i in range(len(y)):
            plt.text(i, y[i], y[i], ha='center')

        self.draw()


def error(message: str):
    """error(message) выводит сообщение message в появляющемся окне"""
    msgBox = QMessageBox()
    msgBox.setWindowTitle("Внимание!")
    msgBox.setText(message)
    msgBox.exec()


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        # self.widgetLetters.setLayout(QVBoxLayout())
        # self.widgetLetters_2.setLayout(QVBoxLayout())

        self.was_analyzed_book = False
        self.was_analyzed_image = False

        self.loadBookButton.clicked.connect(self.load_book)
        self.analyzeBookButton.clicked.connect(self.process_book)
        self.apprx_text_dict = {k: 0 for k in alphabet}
        self.exact_text_dict = {k: 0 for k in alphabet}

        self.loadImageButton.clicked.connect(self.load_image)
        self.analyzeImageButton.clicked.connect(self.analyze_image)

        self.text = ""
        self.image = ''
        self.pixels = []
        self.allCount = 0

    def load_book(self):
        try:
            self.was_analyzed_book = False
            self.labelAprxBook.setText("Грубая оценка энтропии:")
            self.labelExactBook.setText("Точная оценка энтропии:")
            #if self.widgetLetters.layout().count() != 0:
            #    self.widgetLetters.layout().itemAt(0).widget().setParent(None)
            #if self.widgetLetters_2.layout().count() != 0:
            #    self.widgetLetters_2.layout().itemAt(0).widget().setParent(None)

            file, _ = QtWidgets.QFileDialog.getOpenFileName(self,
                                                            'Open File',
                                                            './',
                                                            'Text Files (*.txt)')
            if not file:
                return
            f = open(file, 'r')
            self.text = f.read()
            self.textBrowser.setText(self.text)
            self.analyzeBookButton.setEnabled(True)
        except Exception as e:
            error(str(e))
        finally:
            f.close()

    def process_book(self):
        try:
            if self.was_analyzed_book:
                error("Вы уже анализировали книгу!")
                return
            count = 0
            demo = []
            for x in self.text:
                if x.lower() in alphabet:
                    demo.append(x.lower())
                    count += 1
                if count == 1000:
                    break
            demo = ''.join(demo)
            allSymbols = len([x for x in self.text if x.lower() in alphabet])
            counter = {k: 0 for k in alphabet}
            for letter in demo:
                if letter.lower() in alphabet:
                    counter[letter.lower()] += 1
            self.allCount = sum(counter[x] for x in alphabet)
            probabilities = {x: (counter[x] / self.allCount) for x in alphabet}
            entropy = 0
            for x in alphabet:
                if probabilities[x] != 0:
                    entropy += -1 * probabilities[x] * math.log2(probabilities[x])
            entropyAprx = entropy * 1000 * (allSymbols / 1000)
            self.labelAprxBook.setText(self.labelAprxBook.text() + "\n" + str(round(entropyAprx, 3)))
            setup_table(self.tableWidget_2, 3, 33, ["Буква", "Количество", "Вероятность"])
            for i, letter in enumerate(alphabet):
                self.tableWidget_2.setItem(i, 0, QtWidgets.QTableWidgetItem(f"{letter}"))
                self.tableWidget_2.setItem(i, 1, QtWidgets.QTableWidgetItem(f"{counter[letter]}"))
                self.tableWidget_2.setItem(i, 2, QtWidgets.QTableWidgetItem(f"{round(probabilities[letter], 4)}"))

            #plot_widget = PlotWidget(self.widgetLetters)
            #self.widgetLetters.layout().addWidget(plot_widget)
            #plot_widget.plot(probabilities, "Для первых 1000 символов")

            counterAll = {k: 0 for k in alphabet}
            for letter in self.text:
                if letter.lower() in alphabet:
                    counterAll[letter.lower()] += 1
            self.allCount = sum(counterAll[x] for x in alphabet)
            probabilities = {x: (counterAll[x] / self.allCount) for x in alphabet}
            entropy = 0
            for x in alphabet:
                if probabilities[x] != 0:
                    entropy += -1 * probabilities[x] * math.log2(probabilities[x])
            entropy *= allSymbols
            self.labelExactBook.setText(self.labelExactBook.text() + "\n" + str(round(entropy, 3)))
            setup_table(self.tableWidget_3, 3, 33, ["Буква", "Количество", "Вероятность"])
            for i, letter in enumerate(alphabet):
                self.tableWidget_3.setItem(i, 0, QtWidgets.QTableWidgetItem(f"{letter}"))
                self.tableWidget_3.setItem(i, 1, QtWidgets.QTableWidgetItem(f"{counterAll[letter]}"))
                self.tableWidget_3.setItem(i, 2, QtWidgets.QTableWidgetItem(f"{round(probabilities[letter], 4)}"))
            #plot_widget2 = PlotWidget(self.widgetLetters_2)
            #self.widgetLetters_2.layout().addWidget(plot_widget2)
            #plot_widget2.plot(probabilities, "Для всей книги")
            self.was_analyzed_book = True
        except Exception as e:
            error(str(e))

    def load_image(self):
        try:
            self.was_analyzed_image = False
            self.labelExactImage.setText("Оценка энтропии:")
            file, _ = QtWidgets.QFileDialog.getOpenFileName(self,
                                                            'Open File',
                                                            './',
                                                            'Images (*.jpg *.png)')
            if not file:
                return
            img = Image.open(file)
            img_bw = img.convert("L")
            self.image = img_bw

            rgb_image = img_bw.convert("RGB")
            width, height = rgb_image.size
            data = rgb_image.tobytes("raw", "RGB")
            qimage = QImage(data, width, height, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qimage)

            w = self.label_2.width()
            h = int((pixmap.height() * w) / pixmap.width())
            while h > self.label_2.height():
                w = int(w * 0.9)
                h = int((pixmap.height() * w) / pixmap.width())
            self.label_2.resize(w, h)
            self.label_2.setPixmap(pixmap)
            self.label_2.setMinimumSize(1, 1)
            self.label_2.setScaledContents(True)

            rgb_image = img.convert("RGB")
            width, height = rgb_image.size
            data = rgb_image.tobytes("raw", "RGB")
            qimage = QImage(data, width, height, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qimage)

            w = self.label_3.width()
            h = int((pixmap.height() * w) / pixmap.width())
            while h > self.label_3.height():
                w = int(w * 0.9)
                h = int((pixmap.height() * w) / pixmap.width())
            self.label_3.resize(w, h)
            self.label_3.setPixmap(pixmap)
            self.label_3.setMinimumSize(1, 1)
            self.label_3.setScaledContents(True)
            self.pixels = img_bw.getdata()

            self.analyzeImageButton.setEnabled(True)
        except Exception as e:
            error(str(e))

    def analyze_image(self):
        try:
            if self.was_analyzed_image:
                error("Вы уже анализировали изображение!")
                return
            setup_table(self.tableWidget, 2, 256, ["Пиксель", "Вероятность"])
            self.tableWidget.verticalHeader().setVisible(False)

            pixelsCount = {k: 0 for k in range(256)}
            allPixels = len(self.pixels)
            for i in self.pixels:
                pixelsCount[int(i)] += 1
            probs = {pixel: pixelsCount[pixel] / allPixels for pixel in pixelsCount}
            entropy = 0
            for x in probs.keys():
                if probs[x] != 0:
                    entropy += -1 * probs[x] * math.log2(probs[x])
            entropy *= allPixels
            for i, p in enumerate(probs):
                self.tableWidget.setItem(i, 0, QtWidgets.QTableWidgetItem(f"{i}"))
                self.tableWidget.setItem(i, 1, QtWidgets.QTableWidgetItem(f"{round(probs[p], 5)}"))
            self.labelExactImage.setText(self.labelExactImage.text() + "\n" + str(round(entropy, 5)))
            self.was_analyzed_image = True
        except Exception as e:
            error(str(e))


app = QtWidgets.QApplication(sys.argv)

window = MainWindow()
window.show()
app.exec()
