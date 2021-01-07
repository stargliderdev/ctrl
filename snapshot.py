#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt4.QtGui import QVBoxLayout, QPalette, QBrush, QColor, QFont, QDialog, QDesktopWidget, QTextEdit, QPushButton
from PyQt4.QtCore import *
import subprocess
import glob
import os
import re
import shutil
import calendar
from datetime import date
import datetime
from dateutil.relativedelta import relativedelta

import stdio
import parameters as gl

class ConsoleClass(QDialog):
    def __init__(self, parent=None):
        super(ConsoleClass,  self).__init__(parent)
        self.mainLayout = QVBoxLayout(self)
        # self.mainLayout.setContentsMargins(0,0,0,0)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.resize(600, 400)
        self.center()

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

        font = QFont('courier new',10)
        font.setWeight(80)
        font.setBold(False)

        self.outputPlainText.setPalette(palette)
        self.outputPlainText.setFont(font)
        self.mainLayout.addWidget(self.outputPlainText)
        self.run_like_hell = QPushButton(u'Começar')
        self.connect(self.run_like_hell, SIGNAL("clicked()"), self.run)
        self.mainLayout.addWidget(self.run_like_hell)
        self.PRINT(u'Faz snapshot 1.0')


    def run(self):
        self.run_like_hell.setDisabled(True)
        try:
            self.PRINT('Faz um backup da base de dados.')
            a = run_silent('c:/insoft/manback.exe')
            if a[0] == False:
                self.PRINT(' Error:\n' + a[1])
                raise Exception("Erro")
            file_paths = glob.glob('c:\\backup\\*.backup')
            sorted_files = stdio.sort_files_by_last_modified(file_paths)
            backup_file = sorted_files[-1][0]
            self.PRINT('Copia c:\insoft para c:\\tmp\insoft')
            if os.path.exists('c:\\tmp\\insoft'):
                shutil.rmtree('c:\\tmp\\insoft')
            shutil.copytree('c:\\insoft', 'c:\\tmp\\insoft')
            self.PRINT('Limpa c:\\tmp\\insoft')
            clean_files()
            self.PRINT('Copia o ultimo backup para c:\\tmp\\insoft')
            shutil.copy2(backup_file, 'c:\\tmp\\insoft' +'/'+backup_file[backup_file.rfind('\\')+1:])
            self.PRINT('Cria c:\\tmp\\insoft\\SAF-t')
            self.mk_dir(['c:\\tmp\\insoft\\SAF-t'])
            self.PRINT('Gera SAF-t dos ultimos 3 meses para c:\\tmp\\insoft\\SAF-t')
            self.make_saft_files()
            self.PRINT('Cria zip de TUDO em c:\\tmp.')
            self.compress_insoft()
            self.PRINT('Terminou sem erros!\n')
        except Exception as err:
            self.PRINT('-------------------------')
            self.PRINT('     Ocorreu um erro     ')
            self.PRINT(str(err))
            self.PRINT('-------------------------')
        self.PRINT('ESC to exit!')


    def make_saft_files(self):
        hl = last_n_months(4)
        for n in range(0, len(hl)):
            # print hl[n][0].strftime('%Y-%m-%d'),hl[n][1].strftime('%Y-%m-%d')
            b = gera_saft(hl[n][0], hl[n][1])
            self.PRINT('SAF-t: ' + hl[n][0].strftime('%Y-%m-%d') + ' to ' + hl[n][1].strftime('%Y-%m-%d') + b[1] )

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def PRINT(self, t):
        self.outputPlainText.append((t).decode('utf-8'))
        self.outputPlainText.repaint()

    def exit_click(self):
        self.close()

    def set_btn_height(self, object,value=60):
        object.setMaximumHeight (value)
        object.setMinimumHeight(value)

    def mk_dir(self, d_list):
        for n in d_list:
            if not os.path.exists(n):
                os.makedirs(n)
            else:
                self.PRINT(n + ' OK')

    def compress_insoft(self):
        # 7z.exe a - t7z NewArchivePath PathOfFolderToArchive
        file_name = gl.saftnif + '-' + '_' + gl.saftname.replace(' ','') + '_' + datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S') + '.zip'
        self.PRINT(file_name)
        run_silent("7z.exe a -tzip " + "c:\\tmp\\" + file_name + " c:\\tmp\\insoft\\")

def clean_files():
    delete_file('c:\\tmp\\insoft\\artigos.exe', True)
    delete_file('c:\\tmp\\insoft\\boot.exe', True)
    delete_file('c:\\tmp\\insoft\\dbupdate.exe', True)
    delete_file('c:\\tmp\\insoft\\pos_1024.exe', True)
    delete_file('c:\\tmp\\insoft\\pos_800.exe', True)
    delete_file('c:\\tmp\\insoft\\SeqESC.txt', True)
    delete_file('c:\\tmp\\insoft\\plugins.ini', True)
    delete_file('c:\\insoft\\pos_old.ini', True)
    delete_files('c:\\tmp\\insoft\\', mask='.txt')
    delete_files('c:\\tmp\\insoft\\', mask='.pdf')
    delete_files('c:\\tmp\\insoft\\', mask='.xml')
    delete_files('c:\\tmp\\insoft\\', mask='.log')
    delete_files('c:\\tmp\\insoft\\', mask='.zip')
    delete_files('c:\\tmp\\insoft\\', mask='.7z')
    delete_dir('c:\\tmp\\insoft\\backup')
    delete_dir('c:\\tmp\\insoft\\utils')
    delete_dir('c:\\tmp\\insoft\\boot')
    delete_dir('c:\\tmp\\insoft\\impressoras')
    delete_dir('c:\\tmp\\insoft\\plugins')
    delete_dir('c:\\tmp\\insoft\\print_spool')
    delete_dir('c:\\tmp\\insoft\\templates')
    delete_dir('c:\\tmp\\insoft\\pda1')
    delete_dir('c:\\tmp\\insoft\\pda2')
    delete_dir('c:\\tmp\\insoft\\pda3')
    delete_dir('c:\\tmp\\insoft\\pda4')
    delete_dir('c:\\tmp\\insoft\\pda5')
    delete_dir('c:\\tmp\\insoft\\tab1')
    delete_dir('c:\\tmp\\insoft\\tab2')
    delete_dir('c:\\tmp\\insoft\\tab3')





def gera_saft(start, end):
    delete_file('c:\\insoft\\success.log')
    delete_file('c:\\insoft\\error.log')
    saft_str = 'localhost#5432#insoft#c:\\insoft\\posback.lic#' + start.strftime('%Y%m%d') +'#' +\
               end.strftime('%Y%m%d') + '#' + 'c:\\tmp\\insoft\\SAF-t'
    msg = []
    # gera o saft
    os.system('c:\\insoft\\mansaft.exe' + ' ' + saft_str)
    if file_ok('c:\\insoft\\error.log'):
        msg.append('Error generating SAF-T file.')
        os.system('c:\\insoft\\checklic.exe' + ' ' + 'c:\\insoft\posback.lic')
        if file_ok('c:\\insoft\\success.log'):
           msg.append('Licence error.')
        else:
           msg.append('No posback.lic.txt file found.')
        return (False, str(msg))
    else:
        return (True, 'OK!')


def last_n_months(a):
    bc = []
    for c in range(0, a):
        a = date.today() - relativedelta(months=c)
        # print a
        if a.month == date.today().month:
            bc.append((datetime.datetime(a.year, a.month, 1), date.today()))
        else:
            last_day = calendar.monthrange(a.year, a.month)
            bc.append(((datetime.datetime(a.year, a.month, 1), date(a.year, a.month, last_day[1]))))
    return bc


def delete_dir(p):
    try:
        shutil.rmtree(p)
    except Exception:
        pass

def file_ok(file):
    if os.path.exists(file):
        return True
    else:
        return False

def delete_files(path, mask='.txt'):
    import os
    for hl in os.listdir(path):
        if hl.endswith(mask):
            os.remove(path + '\\' + hl)


def delete_file(path,echo = False):
    if os.path.isfile(path):
        if echo:
            os.remove(path)


def run_silent(command):
    try:
        toto = subprocess.Popen(command,shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        result = toto.stdout.readlines()
        p = re.compile('error')
        if p.search(str(result)):
            return (False, result)
        else:
            return (True, result)
    except Exception as err:
        return (False, str(err))

if __name__ == '__main__':
    pass