#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt4.QtGui import QDialog, QLabel, QCheckBox, QVBoxLayout, QLineEdit, QTabWidget, QPushButton, \
    QWidget, QToolButton, QDateEdit, QTextEdit, QMessageBox, QCalendarWidget, QDesktopWidget, QTableWidget, QComboBox, \
    QApplication
import sys
import datetime
from qlib import addHLayout, addVLayout


class DateInput(QDialog):
    def __init__(self, title, parent=None):
        super(DateInput, self).__init__(parent)
        self.ret = False, ''
        self.setWindowTitle(title)
        masterLayout = QVBoxLayout(self)
        self.startDateQCalendarWidget = QCalendarWidget()
        self.startDateQCalendarWidget.setVerticalHeaderFormat(0)
        self.startDateQCalendarWidget.selectionChanged.connect(self.start_changed)
        
        self.endDateQCalendarWidget = QCalendarWidget()
        self.endDateQCalendarWidget.setVerticalHeaderFormat(0)
        self.endDateQCalendarWidget.selectionChanged.connect(self.start_changed)
        masterLayout.addLayout(addHLayout([self.startDateQCalendarWidget, self.endDateQCalendarWidget]))
        okBtn = QPushButton('Valida')
        okBtn.clicked.connect(self.save_click)
        cancelBtn = QPushButton('Cancela')
        cancelBtn.clicked.connect(self.cancel_btn_click)
        masterLayout.addLayout(addHLayout([okBtn, cancelBtn]))
    
    def start_changed(self):
        self.endDateQCalendarWidget.setMinimumDate(self.startDateQCalendarWidget.selectedDate())
        self.startDateQCalendarWidget.setMaximumDate(self.endDateQCalendarWidget.selectedDate())
    
    def cancel_btn_click(self):
        self.ret = False, ''
        self.close()
    
    def save_click(self):
        self.ret = True, self.startDateQCalendarWidget.selectedDate().toPyDate(), \
                   self.endDateQCalendarWidget.selectedDate().toPyDate()
        self.close()
    
    def lifetime_click(self):
        self.ret = (True, datetime.datetime(2050, 0o1, 0o1))
        self.close()


def main():
    app = QApplication(sys.argv)
    form = DateInput('Teste')
    form.show()
    app.exec_()
    print(form.ret)


if __name__ == '__main__':
    main()