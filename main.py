import math
import sys

from PIL import Image

import matplotlib.pyplot as plt
from PyQt6 import QtWidgets
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QVBoxLayout
from matplotlib import ticker
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from main_window import Ui_MainWindow

alphabet = 'абвгдеёжзийклмнопрстуфхцчшщьыъэюя'


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

        plt.title(title)
        plt.grid(axis='y')

        self.draw()


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.widgetLetters.setLayout(QVBoxLayout())
        self.widgetPixels.setLayout(QVBoxLayout())
        self.widgetLetters_2.setLayout(QVBoxLayout())

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
        file, _ = QtWidgets.QFileDialog.getOpenFileName(self,
                                                        'Open File',
                                                        './',
                                                        'Text Files (*.txt)')
        if not file:
            return
        self.text = open(file, 'r').read()
        self.textBrowser.setText(self.text)
        self.analyzeBookButton.setEnabled(True)

    def process_book(self):
        demo = self.text[:1000]
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
        self.labelAprxBook.setText(self.labelAprxBook.text() + "\n" + str(round(entropy, 3)))

        plot_widget = PlotWidget(self.widgetLetters)
        self.widgetLetters.layout().addWidget(plot_widget)
        plot_widget.plot(probabilities, "Для первых 1000 символов")

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
        self.labelExactBook.setText(self.labelExactBook.text() + "\n" + str(round(entropy, 3)))
        plot_widget2 = PlotWidget(self.widgetLetters_2)
        self.widgetLetters_2.layout().addWidget(plot_widget2)
        plot_widget2.plot(probabilities, "Для всей книги")

    def load_image(self):
        file, _ = QtWidgets.QFileDialog.getOpenFileName(self,
                                                        'Open File',
                                                        './',
                                                        'Image (*.jpg)')
        if not file:
            return
        img = Image.open(file)
        img = img.convert("L")
        self.image = img
        rgb_image = img.convert("RGB")
        width, height = rgb_image.size
        data = rgb_image.tobytes("raw", "RGB")
        qimage = QImage(data, width, height, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)
        self.label_2.setPixmap(pixmap)
        self.label_2.setMinimumSize(1, 1)
        self.label_2.setScaledContents(True)
        self.pixels = img.getdata()

    def analyze_image(self):
        pixelsCount = {k: 0 for k in range(256)}
        allPixels = len(self.pixels)
        for i in self.pixels:
            pixelsCount[int(i)] += 1
        probs = {pixel: pixelsCount[pixel] / allPixels for pixel in pixelsCount}
        print(probs)
        entropy = 0
        for x in probs.keys():
            if probs[x] != 0:
                entropy += -1 * probs[x] * math.log2(probs[x])
        self.labelAprxImage.setText(self.labelAprxImage.text() + "\n" + str(round(entropy, 3)))
        plot_widget = PlotWidget(self.widgetPixels)
        self.widgetPixels.layout().addWidget(plot_widget)
        plot_widget.plot(probs, "Для всей книги")


app = QtWidgets.QApplication(sys.argv)

window = MainWindow()
window.show()
app.exec()
