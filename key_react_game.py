#!/usr/bin/python3
# -*- coding: utf-8 -*-


import sys
from PyQt5 import QtGui, QtWidgets, QtCore, uic
from PyQt5.QtGui import QKeySequence, QIntValidator
from PyQt5.QtWidgets import QDialog, QStackedWidget, QWidget
from PyQt5.QtCore import QTimer, QDateTime
import random
import time
import pandas as pd
from pathlib import Path

url_color_csv = "color_palette.csv"
path_results = "results.csv"
REPETITIONS = 10
pd.set_option("display.max_rows", None, "display.max_columns", None)


class Test:
    def __init__(self):
        self.color_palette = pd.read_csv(url_color_csv)
        self.participant_ID = None
        self.column_names = ["ID", "Condition", "Repetition", "Color", "HEX", "Delaytime(ms)", "Pressed Key",
                             "Correct?",
                             "Timestamp(Teststart)", "Timestamp(Color)", "Timestamp(Keystroke)"]
        self.log_data = pd.DataFrame(columns=self.column_names)
        self.setup_dataframe()
        print("Howdey")
        print(self.log_data)

    def setup_dataframe(self):
        global path_results
        file = Path(path_results)
        if file.is_file():
            check_db = pd.read_csv(path_results)
            data_top = list(check_db)
            if data_top == self.column_names:
                self.log_data = check_db
                return
            path_results = rename_filepath(path_results)
            self.setup_dataframe()
            return
        self.log_data.to_csv(path_results, index=False)

    def create_test(self, mode):
        test_palette = self.color_palette.sample(n=REPETITIONS)
        test_palette = test_palette.reset_index(drop=True)
        test_palette.index.name = self.column_names[2]
        ran_time = [None] * 10
        for i in range(0, REPETITIONS):
            ran_time[i] = random.randrange(5, 100) * 100
            print("here", ran_time[i])
        print("Random", random.randrange(5, 100))
        test_palette[self.column_names[5]] = ran_time
        test_palette[self.column_names[1]] = mode
        print(test_palette)
        if mode == "easy":
            test_palette[self.column_names[4]] = test_palette.sample(frac=1)[self.column_names[4]].values
            print(test_palette)


def generate_table():
    return


def rename_filepath(fpath):
    fpath = fpath.split(".")
    return fpath[0] + "~." + fpath[1]


def mapping_char(event):
    char = QKeySequence(event.nativeVirtualKey()).toString()
    if char in "ÀÞº":
        mapping = {
            "À": "Ö",
            "Þ": "Ä",
            "º": "Ü"
        }
        char = mapping.get(char)
    return char


class ButtonTestMenu(QDialog):
    """ Counts how often the 'space' key is pressed and displays the count.

    Every time the 'space' key is pressed, a visual indicator is toggled, too.
    """

    def __init__(self):
        super().__init__()
        self.counter = 3
        self.text_content = ""
        self.text_color = "black"

        self.p_id = 0
        self.test_started = False
        self.loading = False
        self.timer = QTimer()
        self.load_menu()
        self.initUI()
        self.test = Test()

    def initUI(self):
        self.test_label.hide()
        self.cancel_b2.setEnabled(False)
        self.agree_b.setEnabled(False)
        self.cancel_b2.hide()
        self.setWindowTitle('reaction_game')
        self.resize(800, 600)
        print("here")

    def load_menu(self):
        uic.loadUi("reaction_menu.ui", self)
        self.agree_b.clicked.connect(self.agreed_clicked)
        self.cancel_b.clicked.connect(self.cancel_clicked)
        self.cancel_b2.clicked.connect(self.cancel_clicked)
        self.timer.timeout.connect(self.timer_timeout)
        self.input_p_id.setValidator(QIntValidator())
        self.input_p_id.textChanged[str].connect(self.text_changed)

    def start_timer(self):
        if self.loading:
            self.timer.start(1000)
            self.countdown()
        self.update()

    def timer_timeout(self):
        if self.loading:
            self.countdown()
            self.update()
            return

    def countdown(self):
        if self.counter > 0:
            self.counter = self.counter - 1
            return
        self.test_started = True
        self.loading = False
        self.cancel_b2.setEnabled(True)
        self.timer.stop()
        print("Test started:", time.time())

    def agreed_clicked(self):
        if (not self.loading) & (not self.test_started):
            self.get_p_id()
            self.test.create_test("easy")
            self.agree_b.hide()
            self.cancel_b.hide()
            self.cancel_b2.show()
            self.text_browser.hide()
            self.test_label.show()
            self.loading = True
            self.start_timer()
            print("click")

    def cancel_clicked(self):
        self.close()

    def keyPressEvent(self, event):
        if self.test_started:
            key = mapping_char(event)
            if key.isalpha():
                print("'", key, "' clicked at:", time.time())

    def update(self):
        if self.loading:
            self.text_content = str(self.counter + 1)
        if self.test_started:
            self.text_content = "Start"
        self.test_label.setText(self.text_content)
        self.test_label.setStyleSheet("QLabel#test_label {color: " + self.text_color + "}")

    def get_p_id(self):
        if (not self.loading) & (not self.test_started):
            self.p_id = self.input_p_id.text()
            print(self.p_id)
            self.input_p_id.hide()
            return

    def text_changed(self):
        self.agree_b.setEnabled(True)

    # def initUI0(self):
    #     # set the text property of the widget we are inheriting
    #     self.text = "Please press 'space' repeatedly."
    #     self.setGeometry(300, 300, 280, 170)
    #     self.setWindowTitle('ClickRecorder')
    #     # widget should accept focus by click and tab key
    #     self.setFocusPolicy(QtCore.Qt.StrongFocus)
    #     self.show()
    #
    # def keyPressEvent(self, ev):
    #     if ev.key() == QtCore.Qt.Key_Space:
    #         self.counter += 1
    #         self.update()

    # @staticmethod
    # def filter_char(char):
    #     sym = ["/", "*", "-", "+", ","]
    #     if char.isnumeric():
    #         return False
    #     if char in sym:
    #         return False
    #     return True
    #
    # def paintEvent(self, event):
    #     qp = QtGui.QPainter()
    #     qp.begin(self)
    #     self.drawText(event, qp)
    #     self.drawRect(event, qp)
    #     qp.end()
    #
    # def drawText(self, event, qp):
    #     qp.setPen(QtGui.QColor(168, 34, 3))
    #     qp.setFont(QtGui.QFont('Decorative', 32))
    #     if self.counter > 0:
    #         self.text = str(self.counter)
    #     qp.drawText(event.rect(), QtCore.Qt.AlignCenter, self.text)
    #
    # def drawRect(self, event, qp):
    #     if (self.counter % 2) == 0:
    #         rect = QtCore.QRect(10, 10, 80, 80)
    #         qp.setBrush(QtGui.QColor(34, 34, 200))
    #     else:
    #         rect = QtCore.QRect(100, 10, 80, 80)
    #         qp.setBrush(QtGui.QColor(200, 34, 34))
    #     qp.drawRoundedRect(rect, 10.0, 10.0)


def main():
    app = QtWidgets.QApplication(sys.argv)
    # variable is never used, class automatically registers itself for Qt main loop:
    win = ButtonTestMenu()

    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
