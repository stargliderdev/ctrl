#!/usr/bin/env python
# -*- coding: utf-8 -*-

from random import randrange
import random

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import parameters as pa
from qlib import addHLayout

class UI(QDialog):
    def __init__(self, parent = None):
        super(UI,    self).__init__(parent)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.CustomizeWindowHint)
        self.center()
        caption = QLabel('a@' + pa.VERSION)
        caption.setAlignment(Qt.AlignHCenter)
        mainLayout = QVBoxLayout(self)
        self.l = False  # tranca
        font = QFont('courier new',22)
        font.setBold(True)
        self.inLineEdit= QLineEdit()
        self.inLineEdit.setMinimumHeight(50)
        self.inLineEdit.setFont(font)
        self.inLineEdit.grabKeyboard()
        self.inLineEdit.setStyleSheet("QLineEdit {border-radius: 6px; font-weight: bold;border-width: 2px;border-style: solid; border-color: #007FFF;}")

        self.connect(self.inLineEdit, SIGNAL ("returnPressed ()"), self.enter_click)

        entBtn = QToolButton()
        entBtn.setMinimumWidth(60)
        entBtn.setMinimumHeight(60)
        entBtn.setIcon(QIcon('enter.png'))
        entBtn.setStyleSheet("QPushButton {border-radius: 6px; font-weight: bold; background-color : #00FF00}")
        self.connect(entBtn, SIGNAL ("clicked()"), self.enter_click)

        xBtn = QToolButton()
        xBtn.setMinimumWidth(60)
        xBtn.setMinimumHeight(60)
        xBtn.setIcon(QIcon('x.png'))
        xBtn.setStyleSheet("QPushButton {border-radius: 6px; font-weight: bold; background-color : #FF0000;}")
        self.connect(xBtn, SIGNAL ("clicked()"), self.fecha)
        
        mainLayout.addWidget(caption)
        mainLayout.addLayout(self.make_cc())
        mainLayout.addWidget(self.HLine())
        mainLayout.addLayout(self.mk_keypad())
        mainLayout.addStretch()
        mainLayout.addLayout(addHLayout([self.inLineEdit,entBtn,xBtn]))
        
    def make_cc(self):
        toto = QVBoxLayout()
        self.salesButtonsGroup = QButtonGroup()
        font = QFont('courier new',10)
        font.setWeight(80)
        font.setBold(True)
        p = ()
        l = 1
        c = 0
        self.hl = ''
        for n in range(0,3):
            dum = QHBoxLayout()
            for n in range(1,11):
                r = randrange(48,58)
                bt = QLabel(chr(r))
                bt.setAlignment(Qt.AlignCenter)
                bt.setFrameShape(QFrame.Box)
                xl =  gen_hex_colour_code() + "}"
                bt.setStyleSheet("QLabel {border-radius: 6px; font-weight: 900; background-color : #" + xl)
                p += (r-48,)
                self.setBtnSizes(bt)
                self.setFont(font)
                dum.addWidget(bt)
                c +=1
            l +=1
            toto.addLayout(dum)
        self.hl = str(p[2])+str(p[13])+str(p[24])+str(p[15])+str(p[26])
        return toto

    def mk_keypad(self):
        self.salesButtonsGroup = QButtonGroup()
        font = QFont('courier new', 10)
        font.setWeight(80)
        font.setBold(True)
        p = ()
        c = 0
        dum = QHBoxLayout()
        for n in range(0, 10):
            bt = QPushButton(str(n))
            bt.setStyleSheet("QPushButton {border-radius: 6px; font-weight: bold; background-color : #007FFF}")
            self.setBtnSizes(bt)
            self.setFont(font)
            dum.addWidget(bt)
            self.salesButtonsGroup.addButton(bt, c)
            c += 1
        self.connect(self.salesButtonsGroup, SIGNAL("buttonClicked(QAbstractButton *)"), self.bt_click)
        return dum
    
    def validate(self):
        pass
    
    def bt_click(self,bt):
        a = self.salesButtonsGroup.id(bt)
        self.inLineEdit.setText(self.inLineEdit.text() + str(a))

    def fecha(self):
        self.close()

    def enter_click(self):
        if self.hl == str(self.inLineEdit.text()):
            pa.wc = -1
        else:
            pa.wc +=1
        self.close()

    def HLine(self):
        toto = QFrame()
        toto.setFrameShape(QFrame.HLine)
        toto.setFrameShadow(QFrame.Sunken)
        return toto
    
    def setBtnSizes(self, object,value=60):
        object.setMaximumHeight (value)
        object.setMinimumHeight(value)
        object.setMaximumWidth(value)
        object.setMinimumWidth(value)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

def gen_hex_colour_code():
    return ''.join([random.choice('9ABC') for x in range(6)])

if __name__ == '__main__':
    pass