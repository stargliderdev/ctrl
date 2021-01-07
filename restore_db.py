#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import re
import subprocess
import time
import os
import parameters as gl
import stdio
import libpgadmin
import libpg
import qlib

class RestoreDialog(QDialog):
    def __init__(self,  parent = None):
        super(RestoreDialog,  self).__init__(parent)
        self.resize(600, 400)
        self.setWindowFlags(Qt.WindowStaysOnTopHint|Qt.WindowTitleHint|Qt.FramelessWindowHint)
        self.setWindowTitle('Restore DB')
        masterLayout = QVBoxLayout(self)

        self.outputPlainText = QTextEdit()
        palette = QPalette()
        brush = QBrush(QColor(0, 255, 0))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Text, brush)
        brush = QBrush(QColor(0, 0, 0))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Base, brush)
        brush = QBrush(QColor(0, 255, 0))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive, QPalette.Text, brush)
        brush = QBrush(QColor(0, 0, 0))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive, QPalette.Base, brush)
        brush = QBrush(QColor(165, 164, 164))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.Text, brush)
        brush = QBrush(QColor(244, 244, 244))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.Base, brush)
        font = QFont('courier new', 10)
        font.setWeight(80)
        font.setBold(False)
        self.outputPlainText.setPalette(palette)
        self.outputPlainText.setFont(font)
        masterLayout.addWidget(self.outputPlainText)

        self.okBtn = QPushButton('Restaurar a DB')
        self.connect(self.okBtn, SIGNAL("clicked()"), self.ok_click)
        self.cancelBtn = QPushButton('Tira-me daqui!')
        self.cancelBtn.clicked.connect(self.exit_click)
        masterLayout.addLayout(qlib.addHLayout([self.okBtn,self.cancelBtn]))
        b_data = stdio.get_backup_data(str(gl.file_name))
        self.PRINT(str(gl.file_name))
        self.PRINT('---------------------------------------------')
        self.PRINT('Data: ' + b_data['data'])
        self.PRINT('Idade: ' + b_data['old'])
        self.PRINT('NIF: ' + b_data['nif'])
        self.PRINT('host: ' + gl.pos_ini['host'])
        self.PRINT('---------------------------------------------')
        self.PRINT('PG_PATH: ' + gl.POSTGRES_PATH)
        self.PRINT('<font color="#85C3FE">Pronto para repor o Backup')
        self.flag = False
        self.repaint()

    def restore_db(self):
        t0 = time.time()
        self.flag = True
        gl.windows_env = os.environ
        self.PRINT('Mata processos...')
        self.outputPlainText.repaint()
        stdio.kill_process()
        gl.POSTGRES_PATH = libpg.get_data_dir()[1].replace('data','bin')

        self.outputPlainText.repaint()
        delete_responce = libpgadmin.drop_database_insoft()
        if not delete_responce[0]:
            self.PRINT(u'A Base de Dados não está criada!<br>' + delete_responce[1].replace('\\r\\n', '<br>'))
            self.outputPlainText.repaint()
        self.PRINT('A criar a base de dados...')
        self.outputPlainText.repaint()
   
        create_responce = libpgadmin.create_database_insoft()
        if not create_responce[0]:
            de = create_responce[1].replace('\\r\\n','<br>')
            self.PRINT('<font color="red">Ocorreu o erro #2 ao fazer o restore!<br>' + de[:de.find('host')])
            self.okBtn.setText('<font color="red">Ocorreu o erro #2')
        else:
            self.PRINT('Base de Dados criada!')
            self.outputPlainText.repaint()
            flag = False
            self.PRINT('A restaurar Base de Dados...')
            self.outputPlainText.repaint()
            foo = gl.windows_env['APPDATA'] + '\\postgresql\\pgpass.conf'
            stdio.print2file(foo,'*:' +  gl.pos_ini['port'] + ':*:root:' + gl.file1)
            toto = '"' + gl.POSTGRES_PATH + '"' + '\\pg_restore -h '+ gl.pos_ini['host'] + ' -U root -d insoft ' + str(gl.file_name)
            dump = run_silent(toto)[1]
            stdio.print2file(foo, '*:' + gl.pos_ini['port'] + ':*:root:Fn<&Z4AyU@T>V«x$$G.PBB<x-R2b[3sLk,C:LqRP;c<b;')
            RESTORE_ERROR = ' OK'
            if len(dump) > 0:
                flag = False
                # clean dump
                for n in dump:
                    if n <> '\\r\\n':
                        RESTORE_ERROR +=n #+ '<br>'
                b = RESTORE_ERROR.find('CREATE PROCEDURAL LANGUAGE')
                if b >0:
                    flag = True
                b = RESTORE_ERROR.find('unsupported version (1.13) in file header')
                if b > 0:
                    RESTORE_ERROR += 'O Postgresql tem de ser actualizada para uma 9.4.19 no minimo. \n' +\
                    'podes descarregar no CRTL.'
                    flag = False

            else:
                flag = True
            if flag:
                self.PRINT('Restore Efectuado com sucesso!')
                self.PRINT('Mensagem: <br>' + RESTORE_ERROR)
                self.outputPlainText.repaint()
                t1 = time.time()
                self.PRINT('restaurada em ' + stdio.seconds_to_hours(t1 - t0))
                self.outputPlainText.repaint()
                self.okBtn.setText('Base de dados Restaurada')
                libpg.make_default(0)
            else:
                t1 = time.time()
                self.PRINT('<font color="red">Ocorreu o erro #3 ao fazer o restore!<br>' + RESTORE_ERROR[:RESTORE_ERROR.find('host')])  # + str(dump).replace('\\r\\n','<br>')
                self.PRINT('<br>em ' + stdio.seconds_to_hours(t1 - t0))
                self.outputPlainText.repaint()
                self.okBtn.setText(u'Base de dados NÃO RESTAURADA!')
                libpg.make_default(0)
   
    def PRINT(self, text):
        try:
            self.outputPlainText.append(text.decode('utf-8'))
        except UnicodeEncodeError:
            self.outputPlainText.append('Erro de unicode')
            self.outputPlainText.append(text.encode('utf-8'))
        self.outputPlainText.repaint()
        
            
    def ok_click (self):
        if self.flag == True:
            self.close()
        else:
            self.okBtn.setEnabled(False)
            self.restore_db()
            self.okBtn.setEnabled(True)
    
    def exit_click(self):
        self.close()


def run_silent(command):
    try:
        toto = subprocess.Popen(command,shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        result = toto.stdout.readlines()
        p = re.compile('error')
        if p.search(str(result)):
            stdio.print2file('dump.log', result)
            return (False, result)
        else:
            stdio.print2file('dump.log', result)
            return (True, result)

    except Exception as err:
        print(' run silent error')
        stdio.print2file('error.log', str(err) +'\n')
        return (False, str(err))




if __name__ == '__main__':
    pass

