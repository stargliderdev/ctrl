#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
from PyQt4.QtCore import SIGNAL, Qt
from PyQt4.QtGui import QPushButton,QTextEdit,QCalendarWidget,QLabel,QVBoxLayout,QDialog, QDesktopWidget
import parameters as gl
import libpg
from qlib import addHLayout

class LicBlock(QDialog):
    def __init__(self, parent = None):
        super(LicBlock, self).__init__(parent)
        self.setWindowFlags(Qt.CustomizeWindowHint)
        self.center()
        self.ret_dic = {'flag': False}
        self.msg_dic = {}
        mainLayout = QVBoxLayout(self)
        self.caption = QLabel('')
        label3 = QLabel('Mensagem (opcional)')
        self.caption.setMinimumHeight(40)
        self.msg_add = QTextEdit()
        self.msg_add.setMaximumHeight(120)
        self.caption.setAlignment(Qt.AlignHCenter)
        mainLayout.addWidget(self.caption)
        self.diaCalendar = QCalendarWidget()
        self.diaCalendar.setVerticalHeaderFormat(0)
        mainLayout.addLayout(addHLayout([True, self.diaCalendar, True]))
        mainLayout.addWidget(label3)
        mainLayout.addWidget(self.msg_add)
        self.ok_btn = QPushButton('O.K.')
        self.set_height(self.ok_btn,60)
        self.connect(self.ok_btn, SIGNAL("clicked()"), self.ok_click)
        self.cancel_btn = QPushButton('Cancela')
        self.set_height(self.cancel_btn,60)
        self.connect(self.cancel_btn, SIGNAL("clicked()"), self.cancel_click)
        mainLayout.addLayout(addHLayout([self.ok_btn,self.cancel_btn]))
        self.no_block = QPushButton('Desbloqueia')
        self.set_height(self.no_block)
        self.connect(self.no_block, SIGNAL("clicked()"), self.no_block_click)
        mainLayout.addWidget(self.no_block)
        cu = libpg.query_one('SELECT validuntil from params', (True,))[0]
        if cu is None :
            self.caption.setText('''<font size="6" color="blue">Sem Limite</font size>''')
        else:
            self.caption.setText('<font size="6" color="red">' + cu.strftime("%d %b %Y") + '</font size>')
    
    def ok_click(self):
        hl = self.diaCalendar.selectedDate().toPyDate()
        self.close_form(hl, hl.strftime("%d %b %Y"))
    
    def no_block_click(self):
        hl = datetime.datetime(2050,01,01,0,0,0)
        self.close_form(hl, 'Sem Bloqueio')
    
    def close_form(self, hl, lock_msg):
        body  = '''<!DOCTYPE html><html lang="pt_pt"><head><meta charset="utf-8"></head><pre>'''
        body += unicode(self.msg_add.toPlainText()).replace('\n', '<br>')
        body += gl.saft_config_dict['commercial_name'].decode('utf-8') + '<br>'
        body += gl.saft_config_dict['saftname'].decode('utf-8') + '<br>'
        body += gl.saft_config_dict['saftnif'] + '<br>'
        body += gl.saft_config_dict['saftaddress'].decode('utf-8') + '<br>'
        body += gl.saft_config_dict['saftpostalcode'].decode('utf-8') + '<br>'
        body += gl.saft_config_dict['saftcity'].decode('utf-8') + '<br>'
        body += gl.saft_config_dict['dbversion']+  '<br>'
        body += 'Count:' + str(libpg.query_one('select lock_count+1 from saft_config')[0]) + '<br>'
        body += gl.CURRENT_USER + ' @' + datetime.datetime.now().strftime(' %m.%b.%Y %H:%M')
        body += '</html>'
        self.ret_dic['flag'] = True
        libpg.execute_query("UPDATE params SET validuntil = %s", (hl,))
        if hl == datetime.datetime(2050,01,01,0,0,0):
            libpg.execute_query('UPDATE saft_config SET lock_count = 0')
        else:
            libpg.execute_query('UPDATE saft_config SET lock_count = lock_count + 1')
        if hl.year != 2050:
            self.msg_dic = {'sub': 'BLOQUEIO [' + str(gl.saft_config_dict['commercial_name']) + '] [' + lock_msg +'] [' + gl.CURRENT_USER + ']', 'body': body}
        else:
            self.msg_dic = {'sub': 'DESBLOQUEIADO [' + str(gl.saft_config_dict['commercial_name']) + '] [' + gl.CURRENT_USER + ']', 'body': body}
        self.close()

    def cancel_click(self):
        self.close()

    def set_height(self, obj, y=60):
        obj.setMinimumHeight(y)
        obj.setMaximumHeight(y)
        
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())    
        
if __name__ == '__main__':
    pass