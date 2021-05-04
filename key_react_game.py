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
        self.currentTest = self.log_data
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
        if mode == "easy":
            test_palette[self.column_names[4]] = test_palette.sample(frac=1)[self.column_names[4]].values
        test_palette[self.column_names[2]] = test_palette.index
        self.currentTest = self.currentTest.append(test_palette, ignore_index=True)

    def save_test(self):
        self.log_data = self.log_data.append(self.currentTest)
        self.log_data.to_csv(path_results, index=False)

    def set_ID(self, id):
        self.currentTest[self.column_names[0]] = str(id)
        return

    def set_timestamp(self, rep_status, case):
        if case == 0:
            self.currentTest[self.column_names[8]] = time.time()
            return
        self.currentTest.loc[rep_status, self.column_names[case + 8]] = time.time()
        print(self.currentTest)

    def get_color_name(self, rep_status):
        return self.currentTest.loc[rep_status, self.column_names[3]]

    def get_hex_color(self, rep_status):
        return self.currentTest.loc[rep_status, self.column_names[4]]

    def get_delay_time(self, rep_status):
        return self.currentTest.loc[rep_status, self.column_names[5]]


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
        self.current_mode = "easy"
        self.current_repetition = 0
        self.p_id = 0
        self.test_started = False
        self.loading = False
        self.keystroke_enabled = True
        self.test_finished = False
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
        self.test.set_timestamp(self.current_repetition, 0)
        print("Test started:", time.time())
        self.test_updates()

    def agreed_clicked(self):
        if (not self.loading) & (not self.test_started):
            self.test.create_test(self.current_mode)
            self.get_p_id()
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
            if not self.keystroke_enabled:
                return
            if key.isalpha():
                self.test.set_timestamp(self.current_repetition, 2)
                self.keystroke_enabled = False

    def update(self):
        if self.loading:
            self.text_content = str(self.counter + 1)
        if self.test_started:
            print("let's see :D")
        self.test_label.setText(self.text_content)
        self.test_label.setStyleSheet("QLabel#test_label {color: " + self.text_color + "}")

    def get_p_id(self):
        if (not self.loading) & (not self.test_started):
            self.p_id = self.input_p_id.text()
            self.test.set_ID(self.p_id)
            self.input_p_id.hide()
            return

    def text_changed(self):
        self.agree_b.setEnabled(True)

    def test_updates(self):
        # if self.self.current_repetition == 10:
        #     if self.current_mode == "easy":
        #         self.test.save_test()
        #         self.test.create_test("hard")
        #         self.counter = 3
        #         self.countdown()
        #     else:
        #         return
        # if
        self.timer.singleShot(self.test.get_delay_time(self.current_repetition), lambda: self.test_updates())
        self.keystroke_enabled = True
        self.text_content = self.test.get_color_name(self.current_repetition)
        self.text_color = self.test.get_hex_color(self.current_repetition)
        self.current_repetition = self.current_repetition + 1
        print("Test started:", time.time())
        self.update()


def main():
    app = QtWidgets.QApplication(sys.argv)
    # variable is never used, class automatically registers itself for Qt main loop:
    win = ButtonTestMenu()

    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
