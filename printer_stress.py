#!/usr/bin/python
# -*- coding: utf-8 -*-
import base64
import datetime
import thread
import threading
import time

from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QHBoxLayout, QVBoxLayout, QLabel,QPushButton,QFont,QCheckBox,QPlainTextEdit,QDialog,QButtonGroup, QSpinBox
import parameters as pa
import libpg
import prtlib
import stdio
from qlib import addHLayout


class PrinterStress(QDialog):
    def __init__(self, parent=None):
        super(PrinterStress,  self).__init__(parent)
        self.setWindowTitle('PrinterStress')
        self.resize(600, 400)
        font = QFont()
        font.setFamily("Monospace")
        font.setPointSize(12)
        font.setBold(True)
        font.setFixedPitch(True)
        self.first_run = True
        self.toto = -1
        self.get_local_printers()
        self.local_printer.append([-1,0,False])
        self.get_remote_printers()
        mainLayout = QVBoxLayout(self)
        label = QLabel('Impressoras')
        mainLayout.addWidget(label)
        self.countSpin = QSpinBox()
        self.countSpin.setMinimum(1)
        self.countSpin.setValue(30)
        self.pauseSpin = QSpinBox()
        self.pauseSpin.setMinimum(0)
        self.pauseSpin.setValue(1)
        self.linesCountSpin = QSpinBox()
        self.linesCountSpin.setMinimum(1)
        self.linesCountSpin.setValue(5)
        self.connect(self.linesCountSpin, SIGNAL("valueChanged(int)"), self.update_msg_click)
        
        mainLayout.addLayout(self.make_buttons())
        mainLayout.addLayout(addHLayout([self.countSpin,'Numero',self.pauseSpin,'Pausa enter (S)', 'Linhas', self.linesCountSpin,True]))
        
        self.mensagem = QPlainTextEdit()
        self.mensagem.setReadOnly(False)
        self.mensagem.setFont(font)
        mainLayout.addWidget(self.mensagem)
        self.sendBtn = QPushButton(u'Envia um')
        self.setSizeHeight(self.sendBtn, 50)
        self.connect(self.sendBtn, SIGNAL("clicked()"), self.send_click)

        self.startBtn = QPushButton(u'Começa')
        self.setSizeHeight(self.startBtn,50)
        self.connect(self.startBtn, SIGNAL("clicked()"), self.start_click)
        self.stopBtn = QPushButton(u'Para')
        self.setSizeHeight(self.stopBtn, 50)
        self.stopBtn.setEnabled(False)
        self.connect(self.stopBtn, SIGNAL("clicked()"), self.stop_click)

        self.closeBtn = QPushButton('Sair')
        self.setSizeHeight(self.closeBtn,50)
        self.connect(self.closeBtn, SIGNAL("clicked()"), self.closeBtn_click)
        mainLayout.addLayout(addHLayout([self.startBtn,self.sendBtn,self.stopBtn,self.closeBtn]))
        self.mensagem.setPlainText('STRESS TEST ' * self.linesCountSpin.value())
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        mainLayout.addWidget(self.output)


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
        self.local_printer = []
        self.printers_dic = {}
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
        # sql = 'SELECT id, description from printers order by id '
        sql = base64.b64decode('U0VMRUNUIGlkLCBkZXNjcmlwdGlvbiBmcm9tIHByaW50ZXJzIG9yZGVyIGJ5IGlkIA==')
        cu = libpg.query_many(sql, (1,))
        for n in cu:
            self.local_printer.append([n[0], n[1], True])
            self.printers_dic[n[1]] = n[0]

    def button_group_click(self, status_id):
        self.toto = status_id
        self.close()

    def update_msg_click(self,i):
        self.mensagem.setPlainText('STRESS TEST ' * self.linesCountSpin.value())

    def stop_click(self):
        self.t.do_run = False
        self.t.join()
        self.closeBtn.setEnabled(True)
        self.sendBtn.setEnabled(True)
        self.startBtn.setEnabled(True)
        self.stopBtn.setEnabled(False)
        self.output.appendPlainText(self.send_to_printer)
        
    def closeBtn_click(self):
        self.close()
        
    def send_click(self):
        if self.first_run:
            self.output.appendPlainText('Limpa spool')
            self.first_run = False
            xl = stdio.spool_clean()
            self.output.appendPlainText('Pedidos:' + str(xl['request_print']) + ' Contas:' + str(xl['print_spool']))
        self.toto = -1
        self.impressoras = []
        pa.msg_c += 1
        for n in self.salesButtonsGroup.buttons():
            if n.isChecked() is True:
                self.impressoras.append(self.printers_dic[unicode(n.text()).encode('utf-8')])
        request_id =  prtlib.print_report(self.mensagem.toPlainText(), self.impressoras, print_random = True)
        self.output.appendPlainText(str(request_id) + ' @ ' + datetime.datetime.now().strftime('%H:%M:%S %d.%m.%Y'))
       
    def start_click(self):
        self.closeBtn.setEnabled(False)
        self.sendBtn.setEnabled(False)
        self.startBtn.setEnabled(False)
        self.stopBtn.setEnabled(True)
        self.output.clear()
        self.output.appendPlainText('Limpa spool')
        xl = stdio.spool_clean()
        self.output.appendPlainText('Pedidos:' + str(xl['request_print']) + ' Contas:' + str(xl['print_spool']))
        self.toto = -1
        self.impressoras = []
        pa.msg_c += 1
        for n in self.salesButtonsGroup.buttons():
            if n.isChecked() is True:
                self.impressoras.append(self.printers_dic[unicode(n.text()).encode('utf-8')])
        self.t = threading.Thread(target=self.doit, args=("task",))
        self.t.start()
       
    def setSizeHeight(self, object, value):
        object.setMaximumHeight(value)
        object.setMinimumHeight(value)

    def doit(self,arg):
        self.send_to_printer = ''
        self.t = threading.currentThread()
        cnt = 0
        cnt_end = self.countSpin.value()
        while getattr(self.t, "do_run", True):
            # print ("working on ", str(cnt))
            if cnt > cnt_end:
                # print("Stopping by count.")
                break
            else:
                cnt +=1
            request_id = prtlib.print_report(self.mensagem.toPlainText(), self.impressoras, print_random=True)
            # self.output.appendPlainText(str(request_id) + ' @ ' + datetime.datetime.now().strftime('%H:%M:%S %d.%m.%Y'))
            self.send_to_printer += str(request_id) + ' @ ' + datetime.datetime.now().strftime('%H:%M:%S %d.%m.%Y') + '\n'
            time.sleep(self.pauseSpin.value())
        # print("Stopping as you wish.")
        self.closeBtn.setEnabled(True)
        self.sendBtn.setEnabled(True)
        self.startBtn.setEnabled(True)
        self.stopBtn.setEnabled(False)



if __name__ == '__main__':
    pass
