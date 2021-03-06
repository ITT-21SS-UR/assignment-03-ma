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
COUNTER = 3
MIN_APPEARENCE_IN_SECONDS = 5000
MAX_APPEARENCE_IN_SECONDS = 10000
DEFAULT_TEXT_COLOR = "black"
pd.set_option("display.max_rows", None, "display.max_columns", None)


# ---> Default Variables


class Test:  # Test class which ist used by the Main Class: "ButtonTestMenu"
    def __init__(self):
        # Setting the main components of the csv-table up...
        self.color_palette = pd.read_csv(url_color_csv)
        self.participant_ID = None
        self.column_names = ["ID", "Condition", "Repetition", "Color", "HEX", "Delaytime(ms)", "Pressed Key",
                             "Correct?",
                             "Timestamp(Teststart)", "Timestamp(Color)", "Timestamp(Keystroke)"]
        self.log_data = pd.DataFrame(columns=self.column_names)
        self.currentTest = self.log_data
        self.setup_dataframe()

    def setup_dataframe(self):
        # saves testsetup in "results.csv"
        global path_results
        file = Path(path_results)
        if file.is_file():
            # in case nothing will be overwritten, only added
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
        # creates test on command and fills the table
        test_palette = self.color_palette.sample(n=REPETITIONS)
        test_palette = test_palette.reset_index(drop=True)
        test_palette.index.name = self.column_names[2]
        ran_time = [None] * 10
        for i in range(0, REPETITIONS):
            ran_time[i] = random.randrange(MIN_APPEARENCE_IN_SECONDS, MAX_APPEARENCE_IN_SECONDS)
        test_palette[self.column_names[5]] = ran_time
        test_palette[self.column_names[1]] = mode
        if mode == "hard":
            test_palette[self.column_names[4]] = test_palette.sample(frac=1)[self.column_names[4]].values
        test_palette[self.column_names[2]] = test_palette.index
        self.currentTest = self.currentTest.append(test_palette, ignore_index=True)

    def save_test(self):
        # saves table to "results.csv"
        self.log_data = self.log_data.append(self.currentTest)
        self.log_data.to_csv(path_results, index=False)
        print(self.currentTest)
        self.currentTest = pd.DataFrame(columns=self.column_names)

    # getter and setter:

    def set_ID(self, id):
        self.currentTest[self.column_names[0]] = str(id)
        return

    def set_pressed_key(self, rep_status, key):
        self.currentTest.loc[rep_status, self.column_names[6]] = key
        self.currentTest.loc[rep_status, self.column_names[7]] = (
                key == self.currentTest.loc[rep_status, self.column_names[3]][0].upper())
        return

    def set_timestamp(self, rep_status, case):
        if case == 0:
            self.currentTest[self.column_names[8]] = time.time()
            return
        self.currentTest.loc[rep_status, self.column_names[case + 8]] = time.time()

    def get_color_name(self, rep_status):
        return self.currentTest.loc[rep_status, self.column_names[3]]

    def get_hex_color(self, rep_status):
        return self.currentTest.loc[rep_status, self.column_names[4]]

    def get_delay_time(self, rep_status):
        return self.currentTest.loc[rep_status, self.column_names[5]]


def rename_filepath(fpath):
    fpath = fpath.split(".")
    return fpath[0] + "~." + fpath[1]


def mapping_char(event):
    char = QKeySequence(event.nativeVirtualKey()).toString()
    if char in "??????":
        mapping = {
            "??": "??",
            "??": "??",
            "??": "??"
        }
        char = mapping.get(char)
    return char


class ButtonTestMenu(QDialog):
    """ Main class, where EVERYTHING happens
    """

    def __init__(self):
        super().__init__()
        # Setting up main control variables
        self.counter = COUNTER
        self.text_content = ""
        self.text_color = DEFAULT_TEXT_COLOR
        self.current_mode = "easy"
        self.current_repetition = 0
        self.p_id = 0
        self.test_started = False
        self.loading = False
        self.keystroke_enabled = True
        self.test_finished = False
        self.color_was_changed = False
        self.timer = QTimer()
        self.load_menu()
        self.initUI()
        self.test = Test()

    def initUI(self):
        # initialize important ui-components
        self.test_label.hide()
        self.cancel_b2.setEnabled(False)
        self.agree_b.setEnabled(False)
        self.cancel_b2.hide()
        self.setWindowTitle('reaction_game')
        self.resize(800, 600)

    def load_menu(self):
        # initialize "reaction_menu.ui" (it was planed having another ui...but that never happened...)
        uic.loadUi("reaction_menu.ui", self)
        self.agree_b.clicked.connect(self.agreed_clicked)
        self.cancel_b.clicked.connect(self.cancel_clicked)
        self.cancel_b2.clicked.connect(self.cancel_clicked)
        self.timer.timeout.connect(self.timer_timeout)
        self.input_p_id.setValidator(QIntValidator())
        self.input_p_id.textChanged[str].connect(self.text_changed)

    def start_timer(self):
        # initialize Qtimer
        if self.loading:
            self.timer.start(1000)
            self.countdown()
        self.update()

    def timer_timeout(self):
        # updating on timeouts...
        if self.loading:
            self.countdown()
            self.update()
            return

    def countdown(self):
        # setting countdown up
        if self.counter > 0:
            self.counter = self.counter - 1
            return
        self.test_started = True
        self.loading = False
        self.cancel_b2.setEnabled(True)
        self.timer.stop()
        self.test.set_timestamp(self.current_repetition, 0)
        self.test_updates()

    # handle button/key listener:

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

    def cancel_clicked(self):
        self.close()

    def keyPressEvent(self, event):
        if self.test_started:
            key = mapping_char(event)
            if not self.keystroke_enabled:
                return
            if key.isalpha():
                self.test.set_pressed_key(self.current_repetition - 1, key)
                self.test.set_timestamp(self.current_repetition - 1, 2)
                self.keystroke_enabled = False

    def update(self):
        # updates UI
        if self.loading:
            self.text_content = str(self.counter + 1)
        self.test_label.setText(self.text_content)
        self.test_label.setStyleSheet("QLabel#test_label {color: " + self.text_color + "}")
        if self.color_was_changed:
            print("color changed")
            self.test.set_timestamp(self.current_repetition, 1)
            self.color_was_changed = False

    def get_p_id(self):
        if (not self.loading) & (not self.test_started):
            self.p_id = self.input_p_id.text()
            self.test.set_ID(self.p_id)
            self.input_p_id.hide()
            return

    def text_changed(self):
        self.agree_b.setEnabled(True)

    def test_updates(self):
        # updates for communication in test class
        if self.current_repetition == 10:
            self.test.save_test()
            self.text_color = DEFAULT_TEXT_COLOR
            if self.current_mode == "easy":
                self.current_repetition = 0
                self.current_mode = "hard"
                self.test.create_test("hard")
                self.test.set_ID(self.p_id)
                self.counter = COUNTER
                self.loading = True
                self.test_started = False
                self.start_timer()
                return
            self.end_test()
            return
        self.timer.singleShot(self.test.get_delay_time(self.current_repetition), lambda: self.test_updates())
        self.keystroke_enabled = True
        self.text_content = self.test.get_color_name(self.current_repetition)
        self.text_color = self.test.get_hex_color(self.current_repetition)
        self.color_was_changed = True
        self.update()
        self.current_repetition = self.current_repetition + 1

    def end_test(self):
        self.text_content = "The End"
        self.cancel_b2.setText("Close")
        self.update()


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = ButtonTestMenu()

    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
