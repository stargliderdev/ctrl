#!/usr/bin/python
# -*- coding: utf-8 -*-
import base64

from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QHBoxLayout, QVBoxLayout, QLabel,QPushButton,QFont,QCheckBox,QPlainTextEdit,QDialog,QButtonGroup
try:
    from unidecode import unidecode
except ImportError:
    pass
import parameters as pa
import libpg
import prtlib
from qlib import addHLayout


class BroadCast(QDialog):
    def __init__(self,what='',where=True, parent=None):
        super(BroadCast,  self).__init__(parent)
        self.setWindowTitle('Broadcast')
        font = QFont()
        font.setFamily("Monospace")
        font.setPointSize(12)
        font.setBold(True)
        font.setFixedPitch(True)
        self.toto = -1
        self.local_printer = []
        self.printers_dic = {}
        if where :
            self.get_local_printers()
            self.local_printer.append([-1,0,False])
            self.get_remote_printers()
        else:
            self.printers_dic['Posto 1'] = 1
            self.local_printer.append([1, 'Posto 1', True])
        mainLayout = QVBoxLayout(self)
        label = QLabel(base64.b64decode('SW1wcmVzc29yYXM='))
        mainLayout.addWidget(label)
        mainLayout.addLayout(self.make_buttons())
        
        self.mensagem = QPlainTextEdit()
        self.mensagem.setFont(font)
        mainLayout.addWidget(self.mensagem)
        self.closeBtn = QPushButton(base64.b64decode('RmVjaGFy'))
        self.setSizeHeight(self.closeBtn,60)
        self.connect(self.closeBtn, SIGNAL("clicked()"), self.closeBtn_click)
        self.sendBtn = QPushButton(base64.b64decode('RW52aWE=')) #QPushButton('Envia')
        self.setSizeHeight(self.sendBtn,60)
        self.connect(self.sendBtn, SIGNAL("clicked()"), self.send_click)
        self.send_and_closeBtn =  QPushButton('Envia \n e Fecha')
        self.setSizeHeight(self.send_and_closeBtn,60)
        self.connect(self.send_and_closeBtn, SIGNAL("clicked()"), self.send_and_close_click)

        mainLayout.addLayout(addHLayout([self.send_and_closeBtn,self.sendBtn,self.closeBtn]))
        if what <> '':
            self.mensagem.setPlainText(what)


    def make_buttons(self):
        self.salesButtonsGroup = QButtonGroup()
        self.salesButtonsGroup.setExclusive(False)
        dumLayout = QHBoxLayout()
        totoLayout = QVBoxLayout()
        for n in self.local_printer:
            if n[0] == -1 :
                dumLayout.addStretch()
                totoLayout.addLayout(dumLayout)
                dumLayout = QHBoxLayout()
            else:
                btn = QCheckBox((n[1]).decode('utf-8'))
                #self.setSizes(btn, 60) 
                if not n[2]:
                    btn.setEnabled(False)
                else:
                    btn.setCheckable(True)
                    btn.setChecked(True)
                self.salesButtonsGroup.addButton(btn, int(n[0]))
                dumLayout.addWidget(btn)
        dumLayout.addStretch()
        totoLayout.addLayout(dumLayout)
        return totoLayout

    def get_local_printers(self):
        sql = 'SELECT id, cashdrawer1opencode from pos order by id '
        cu = libpg.query_many(sql, (1,))
        posto = 1
        for n in cu:
            if n[1] == '' or n[1] is None:
                flag = False
            else:
                flag = True
                self.printers_dic['Posto ' + str(posto)] = posto
            self.local_printer.append([posto, 'Posto ' + str(posto), flag])
            posto += 1

    def get_remote_printers(self):
        sql = base64.b64decode('U0VMRUNUIGlkLCBkZXNjcmlwdGlvbiBmcm9tIHByaW50ZXJzIG9yZGVyIGJ5IGlkIA==')
        cu = libpg.query_many(sql, (1,))
        for n in cu:
            self.local_printer.append([n[0], n[1], True])
            self.printers_dic[n[1]] = n[0]

    def button_group_click(self, status_id):
        self.toto = status_id
        self.close()

    def closeBtn_click(self):
        self.close()

    def send_and_close_click(self):
        self.send_click()
        self.close()

    def send_click(self):
        self.toto = -1
        impressoras = []
        pa.msg_c += 1
        for n in self.salesButtonsGroup.buttons():
            if n.isChecked() is True:
                impressoras.append(self.printers_dic[unicode(n.text()).encode('utf-8')])
        prtlib.print_report(self.mensagem.toPlainText(), impressoras)
        
    def setSizeHeight(self, object, value):
        object.setMaximumHeight(value)
        object.setMinimumHeight(value)

    def parseField(self, field_name):
        # v2
        dum = self.item_data[field_name]
        if type(dum) == int:
            return str(dum)
        elif dum is None:
            return ''
        else:
            return dum.decode('utf-8')


if __name__ == '__main__':
    pass
