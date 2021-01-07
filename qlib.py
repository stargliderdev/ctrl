#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QWidget, QHBoxLayout,QVBoxLayout, QCheckBox,QTextEdit, QLineEdit,QLabel, QSpinBox,QDateEdit,\
    QFrame, QComboBox,QPlainTextEdit,QPushButton, QIcon

def checkBoxGrid(label=''):
    w = QWidget()
    l = QHBoxLayout(w)
    l.setContentsMargins(0,0,0,0)
    l.addStretch()
    c = QCheckBox(label)
    l.addWidget(c)
    l.addStretch()
    return w

def addHLayout(listobj1,lw=80, label_align=Qt.AlignVCenter|Qt.AlignRight):
    dumLayout = QHBoxLayout()
    for n in listobj1:
        if (type(n)==str) or (type(n) == str):
            toto = QLabel(n)
            toto.setMinimumWidth(lw)
            toto.setMaximumWidth(lw)
            toto.setAlignment(label_align)
            dumLayout.addWidget(toto)
        elif type(n) == bool:
            dumLayout.addStretch()
        else:
            dumLayout.addWidget(n)
    return dumLayout

def read_field(obj,field,dic):
    a = type(obj)
    toto = dic[field]
    if toto is None:
        pass
    elif a == QCheckBox:
        obj.setChecked(toto)
    elif a == QLineEdit:
        if type(toto) == int :
            obj.setText(str(toto))
        else:
            obj.setText(toto.decode('utf-8').strip())
    elif a == QTextEdit:
        obj.setPlainText(toto.decode('utf-8'))
    elif a == QPlainTextEdit:
        obj.setPlainText(toto.decode('utf-8'))
    elif a == QSpinBox:
        obj.setValue(toto)
    elif a == QComboBox:
        obj.setEditable(True)
        obj.setEditText(toto.decode('utf-8'))
    elif a == QDateEdit:
        obj.setDate(toto)

def write_field(obj, dic = {}):
    a = type(obj)
    if a == QLineEdit:
        if obj.text().toInt()[1] == False:
            toto = str(obj.text())
        else:
            toto = obj.text().toInt()[0]
        return toto
    elif a == QDateEdit:
        return obj.date().toPyDate()
    elif a == QCheckBox:
        return obj.isChecked()
    elif a == QPlainTextEdit or a == QTextEdit:
        return str(obj.toPlainText())
    elif a == QSpinBox:
        return obj.value()
    elif a == QComboBox:
        if dic == {}:
            return str(obj.currentText()).encode('utf-8')
        else:
            return dic[str(obj.currentText()).encode('utf-8')]

def make_button(label,icon='',w=300,h=50):
    pb = QPushButton(label)
    pb.setStyleSheet("QPushButton { text-align: left;padding-left:30px; }")
    pb.setIcon(QIcon(icon))
    pb.setMaximumWidth(w)
    pb.setMinimumWidth(w)
    pb.setMinimumHeight(h)
    return pb

def addVLayout(listobj1):
    dumLayout = QVBoxLayout()
    for n in listobj1:
        if (type(n)==str) or (type(n) == str):
            dumLayout.addWidget(QLabel(n))
        elif type(n) == bool:
            dumLayout.addStretch()
        else:
            dumLayout.addWidget(n)
    return dumLayout

def HLine():
    toto = QFrame()
    toto.setFrameShape(QFrame.HLine)
    toto.setFrameShadow(QFrame.Sunken)
    return toto