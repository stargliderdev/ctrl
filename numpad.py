#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

from PyQt4.QtCore import SIGNAL, Qt
from PyQt4.QtGui import QDialog, QVBoxLayout, QLineEdit, QPushButton, QIcon, QFont, QHBoxLayout, QDesktopWidget, \
    QApplication, QButtonGroup
from qlib import addHLayout


class NumPad(QDialog):
    def __init__(self, parent=None):
        super(NumPad, self).__init__(parent)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.CustomizeWindowHint)
        self.center()
        mainLayout = QVBoxLayout(self)
        self.l = False  # tranca
        self.inLineEdit = QLineEdit()
        self.inLineEdit.setEchoMode(2)
        self.inLineEdit.grabKeyboard()
        
        self.connect(self.inLineEdit, SIGNAL("returnPressed ()"), self.enter_click)
        
        entBtn = QPushButton()
        entBtn.setMinimumHeight(60)
        entBtn.setIcon(QIcon('enter.png'))
        entBtn.setStyleSheet("QPushButton {border-radius: 6px; font-weight: bold; background-color : #00FF00}")
        self.connect(entBtn, SIGNAL("clicked()"), self.enter_click)
        
        xBtn = QPushButton()
        xBtn.setMinimumHeight(60)
        xBtn.setIcon(QIcon('x.png'))
        xBtn.setStyleSheet("QPushButton {border-radius: 6px; font-weight: bold; background-color : #FF0000;}")
        self.connect(xBtn, SIGNAL("clicked()"), self.exit_click)
        
        mainLayout.addWidget(self.inLineEdit)
        mainLayout.addLayout(self.mk_keypad())
        mainLayout.addLayout(addHLayout([entBtn, xBtn]))
        mainLayout.addStretch()
    
   
    def mk_keypad(self):
        toto = QVBoxLayout()
        self.salesButtonsGroup = QButtonGroup()
        font = QFont('courier new', 10)
        font.setWeight(80)
        font.setBold(True)
        c = 1
        
        for n in range(0, 3):
            dum = QHBoxLayout()
            for f in range(0,3):
                bt = QPushButton(str(c))
                bt.setStyleSheet("QPushButton {border-radius: 6px; font-weight: bold; background-color : #007FFF}")
                self.setBtnSizes(bt)
                self.setFont(font)
                dum.addWidget(bt)
                self.salesButtonsGroup.addButton(bt, c)
                c += 1
            dum.addStretch()
            toto.addLayout(dum)
        bt = QPushButton('0')
        bt.setStyleSheet("QPushButton {border-radius: 6px; font-weight: bold; background-color : #007FFF}")
        bt.setMinimumHeight(60)
        bt.setMaximumHeight(60)
        self.setFont(font)
        self.salesButtonsGroup.addButton(bt)
        toto.addWidget(bt)
        self.connect(self.salesButtonsGroup, SIGNAL("buttonClicked(QAbstractButton *)"), self.bt_click)
        return toto
    
    
    def bt_click(self, bt):
        a = self.salesButtonsGroup.id(bt)
        self.inLineEdit.setText(self.inLineEdit.text() + str(a))
    
    def exit_click(self):
        self.ret = ''
        self.close()
    
    def enter_click(self):
        self.ret = self.inLineEdit.text()
        self.close()
    
    def setBtnSizes(self, object, value=60):
        object.setMaximumHeight(value)
        object.setMinimumHeight(value)
        object.setMaximumWidth(value)
        object.setMinimumWidth(value)
    
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


if __name__ == '__main__':
    pass