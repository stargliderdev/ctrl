#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ftplib
import os
import re
import subprocess
import sys
import time
from PyQt4.QtCore import Qt, SIGNAL
from PyQt4.QtGui import QDialog, QVBoxLayout, QComboBox, QCheckBox, QTextEdit, QBrush, QColor, QPalette, QFont, \
    QPushButton, QApplication, QStyleFactory, QFileDialog, QDesktopWidget

import parameters as gl
import qlib
import stdio


class BackupToFtp(QDialog):
    def __init__(self, parent=None):
        super(BackupToFtp, self).__init__(parent)
        self.resize(600, 400)
        self.center()
        self.setWindowTitle('Envia Ficheiros p/ FTP')
        masterLayout = QVBoxLayout(self)
        self.targetCbx = QComboBox()
        self.archiveChk = QCheckBox('Arquiva')

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
        self.exitChk = QCheckBox('Sair')
        masterLayout.addWidget(self.exitChk)
        self.okBtn = QPushButton('Envia')
        self.okBtn.setMinimumHeight(60)
        self.okBtn.setMinimumWidth(400)
        cancelBtn = QPushButton('X')
        cancelBtn.setMinimumWidth(60)
        cancelBtn.setMaximumHeight(60)
        self.connect(self.okBtn, SIGNAL("clicked()"), self.ok_click)
        cancelBtn.clicked.connect(self.exit_click)
        
        masterLayout.addLayout(qlib.addHLayout([self.okBtn, True,cancelBtn]))
        stdio.get_params()
            
    def PRINT(self, text):
        try:
            self.outputPlainText.append(text.decode('utf-8'))
        except UnicodeEncodeError:
            self.outputPlainText.append('Erro de unicode')
            self.outputPlainText.append(text.encode('utf-8'))
        self.outputPlainText.repaint()    
    
    def ok_click(self):
        file_list = QFileDialog.getOpenFileNames(self, "File to send", "c:\\backup")
        att_files = []
        if file_list.isEmpty():
            pass
        else:
            for n in file_list:
                att_files.append(str(n))
                self.PRINT(str(n))
            time.sleep(1)
            self.send_ftp(att_files)
            if self.exitChk.checkState():
                self.PRINT('Saindo ...')
                time.sleep(5)
                sys.exit(0)
                
    def exit_click(self):
        self.close()

    def send_ftp(self, file_list):
        t0 = time.time()
        try:
            session = ftplib.FTP()
            session.connect(gl.malaristix[0] , 21)
            session.login(gl.malaristix[1] , gl.malaristix[2])
            session.mkd('/' + gl.saftnif +'/')
            session.cwd('/' + gl.saftnif +'/')
        except Exception as resp:
            if str(resp).find('File exists') > -1:
                session.cwd('/' + gl.saftnif + '/')
            else:
                self.PRINT('ERROR: ' + str(resp))
        self.PRINT("{:^80}".format( 'Start Sending'))
        self.PRINT(str(len(file_list)) + ' files' )
        for n in file_list:
            x_file = open(n, 'rb')
            try:
                tt0 = time.time()
                file_name =  os.path.basename(n) # n[n.rfind('/') + 1:]
                session.storbinary('STOR ' + file_name, x_file)
                tt1 = time.time()
                dum_str = os.path.basename(n)[:-7]
                self.PRINT("{:<40}".format(dum_str[:40]) + ' ' +  stdio.seconds_to_hours(tt1-tt0))
            except Exception as resp:
                self.PRINT('ERRO: ' + str(resp))
        session.close()
        t1 = time.time()
        self.PRINT(' ' * 81 + stdio.seconds_to_hours(t1 - t0))

   
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

def run_silent(command):
    try:
        toto = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        result = toto.stdout.readlines()
        p = re.compile('error')
        if p.search(str(result)):
            stdio.print2file('dump.log', result)
            return False, result
        else:
            stdio.print2file('dump.log', result)
            return True, result
    
    except Exception as err:
        print(' run silent error')
        stdio.print2file('error.log', str(err) + '\n')
        return False, str(err)



def main():
    app = QApplication(sys.argv)
    QApplication.setStyle(QStyleFactory.create('plastique'))
    form = BackupToFtp()
    form.show()
    app.exec_()
    
if __name__ == '__main__':
    pass


