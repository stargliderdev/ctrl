#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import os.path
import datetime
import base64
import glob
import time
import ftplib
try:
    import psycopg2
except ImportError:
    pass
import shutil

import libpgadmin

try:
    from win32api import GetSystemMetrics
    import wmi
except ImportError:
    pass
from PyQt4.QtCore import Qt, SIGNAL
from PyQt4.QtGui import QHBoxLayout, QVBoxLayout,QFileDialog,QMessageBox,QPushButton,QFont,QDesktopWidget,QBrush,QColor,\
     QPalette,QDialog,QTextEdit

import sys
import parameters as gl
import stdio
import rebuild
import dbmain
import lics_download
import libpg
import msi_instaled
import win_interface
import html_lib

class UpdaterConsole(QDialog):
    def __init__(self, internet=True, parent=None):
        super(UpdaterConsole, self).__init__(parent)
        self.mainLayout = QVBoxLayout(self)
        # vars
        self.BUTTON_STATUS = True, 'Analizando'
        gl.error = 'Erro de inicialização'
        self.lock_flag = False
        self.cnt = 0
        self.last_version = gl.PRODUCTION_VERSION.replace('_','')  # utima versão de produção formato'201810'
        self.start_version = ''
        self.current_version = '' # a versão desta base de dados
        self.resize(700, 480)
        self.setWindowTitle('Updater')
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
        font = QFont('courier new', 10)
        font.setWeight(80)
        font.setBold(False)
        self.outputPlainText.setPalette(palette)
        self.outputPlainText.setFont(font)
        self.mainLayout.addWidget(self.outputPlainText)
        fechaBtn = QPushButton('X')
        fechaBtn.setMaximumWidth(40)
        fechaBtn.setMaximumHeight(40)
        self.connect(fechaBtn, SIGNAL("clicked()"), self.exit_click)
        
        self.runUpdaterButton = QPushButton(self.BUTTON_STATUS[1])
        self.runUpdaterButton.setMaximumHeight(40)
        self.runUpdaterButton.setMinimumHeight(40)
        self.connect(self.runUpdaterButton, SIGNAL("clicked()"), self.run_main_updater)  # CALL UPDATER
        dumLayout = QHBoxLayout()
        dumLayout.addWidget(self.runUpdaterButton)
        dumLayout.addWidget(fechaBtn)
        self.mainLayout.addLayout(dumLayout)
        self.show()
        if get_psql_version():
            pass
        else:
            self.BUTTON_STATUS = False, u'Versão do PostgreSQL não suportada!'
      
        if self.BUTTON_STATUS[0]:
            bc = self.get_db_version()[:6] # por causa das versoes muito velhas
            odbc_version = {}
            if int(bc) < 201810:
                try:
                    self.PRINT('Versão muito antiga, deve ser do Paulo! ' + bc.strip())
                    self.PRINT('Verificando a versão do psqlODBC ... ZZzz')
                    odbc_version = msi_instaled.get_odbc_version()
                except NameError:
                    print 'Versão muito antiga'
                    sys.exit(32)
            else:
                odbc_version['major'] = 9
                odbc_version['version'] = '9.0'
                odbc_version['minor'] = 0
           
            if odbc_version['major'] == 8:
                self.BUTTON_STATUS = False, u'Versão do ODBC não suportada!' + odbc_version['version']
                self.PRINT('<font color="red">Versão do ODBC não suportada! ' + odbc_version['version'])
                self.runUpdaterButton.setText(self.BUTTON_STATUS[1])
                res = QMessageBox.critical(self, self.trUtf8('''Erro no ODBC '''),
                                           self.trUtf8(
                                               '''psqlODBC incompativel!\n''' + u'''Versão ''' + odbc_version['version'] + '''\n'''
                                               '''Continuar a desinstalar o ODBC 8.x e fazendo re-boot?'''),
                                           QMessageBox.StandardButtons(QMessageBox.Yes | QMessageBox.No))
                
                if res == QMessageBox.Yes:
                    self.PRINT('<font color="yellow">Parando o boot!')
                    stdio.dir_ok('c:\\insoft\\EXIT')
                    self.PRINT('<font color="yellow">Terminando todos os processos ... ')
                    b = str(win_interface.kill_all_process(True))
                    self.PRINT('Terminados todos os processos: ' + b)
                    self.PRINT('<font color="yellow">Descarregando o psqlODBC 9.x 32 bit ... ')
                    win_interface.get_9()
                    self.PRINT('Descarregado o psqlODBC! ')
                    self.PRINT('<font color="yellow">Desinstalando o psqlODBC 8.x ... ')
                    os.system('msiexec /x ' + odbc_version['Package Cache'] +' /qn')
                    self.PRINT('Desinstalado o psqlODBC 8 ')
                    self.PRINT('<font color="red">Re-boot ')
                    os.system('shutdown /t 0 /r /f ')
                    sys.exit(0)
                else:
                    self.PRINT('Versão do ODBC não suportada!')
                    self.BUTTON_STATUS = False, u'Instalação abortada'
            elif odbc_version['major'] == 0 or odbc_version['major'] == 9:
                if odbc_version['major'] == 0:
                    self.PRINT('<font color="red">Sem ODBC')
                    self.PRINT('Vou instalar automaticamente o psqlODBC 9')
                    if not stdio.file_ok('c:\\tmp\\psqlODBC_9_x86.msi'):
                        self.PRINT('<font color="yellow">Ainda não foi descarregado ')
                        self.PRINT('<font color="yellow">Vou descarregar ... ')
                        self.PRINT('Descarregado o psqlODBC!')
                        win_interface.get_9()
                        self.PRINT('Descarregado o psqlODBC!')
                    self.PRINT('Actualizando o instalador do ODBC ...')
                    self.BUTTON_STATUS = False, u'Actualizando o ODBC '
                    self.runUpdaterButton.setText(self.BUTTON_STATUS[1])
                    self.runUpdaterButton.repaint()
                    os.system("c:\\tmp\\psqlODBC_9_x86.msi")
                if self.check_alive():
                    stdio.get_params()
                self.current_version = self.get_db_version()
                self.show_info()
                stdio.is_server()
                self.PRINT('Mata processos pendentes.')
                stdio.kill_process()
                if internet:
                    # stdio.delete_files('c:\\tmp\\', mask='.lic') # limpa ficheiros de lic no tmp
                    form = lics_download.DownloadLic(one=True, mode=1, nif=gl.saftnif) # descarrega a licenca
                    form.exec_()
                    if gl.update_settings['run']:
                        self.BUTTON_STATUS = True, ''
                        self.PRINT('<font color="white">Licença Selecionada!')
                        self.PRINT('<font color="white">NIF:' + gl.saftnif)
                        self.PRINT('Pronto para actualizar!')
                    else:
                        self.PRINT('Não foi descarregada nenhuma licença!')
                        self.BUTTON_STATUS = False, 'Não foi descarregada nenhuma licença!'
                        self.runUpdaterButton.setText(u'Update abortado pelo utilizador.')
                else:
                    options = QFileDialog.Options()
                    options |= QFileDialog.DontUseNativeDialog
                    file_name = QFileDialog.getOpenFileName(self, u"Ficheiro de Licença", "c:\\tmp")
                    if not file_name == '':
                        for fl in glob.glob("c:\\tmp\\*.lic"):
                            os.remove(fl)
                        try:
                            stdio.run_silent("7z.exe e " + str(file_name) + " -oc:\\tmp\\")
                        except Exception as err:
                            self.BUTTON_STATUS = False, u'Erro de Licença'
                            self.PRINT(str(err))
                if self.BUTTON_STATUS[0]:
                    if self.last_version == self.current_version:
                        self.BUTTON_STATUS = True, ''
                        self.runUpdaterButton.setText(u'Ultima Versão, actualizar binários')
                    else:
                        self.runUpdaterButton.setText(
                            u'Da versão: ' + format_version(str(self.current_version)) + u' para a versão ' + self.last_version)
        else:
            self.runUpdaterButton.setText(self.BUTTON_STATUS[1])
    
    def run_main_updater(self):
        # teste de loop com barra
        if self.BUTTON_STATUS[0]:
            if self.make_update():
                pass
            else:
                self.BUTTON_STATUS = False, u'Erro grave no update'
                self.runUpdaterButton.setText(self.BUTTON_STATUS[1])
                
        else:
            self.close()
            
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
    def PRINT(self, text, to_file=False):
        self.outputPlainText.append(text.decode('utf-8'))
        self.outputPlainText.repaint()
        if to_file :
            stdio.log_write('update.log', text)
    
    def exit_click(self):
        self.close()
       
    
    def show_info(self):
        self.start_version = self.get_db_version()
        self.PRINT('{:>20}'.format('Cliente: ') + gl.saftname)
        self.PRINT('{:>20}'.format('Nome Comercial: ') + gl.commercial_name)
        self.PRINT('{:>20}'.format('N.I.F.: ') + gl.saftnif)
        self.PRINT('{:>20}'.format('Versao da BD: ') + format_version(self.start_version))
        self.PRINT('{:>20}'.format('host: ') + gl.pos_ini['host'] + '/' + gl.pos_ini['port'])
        self.PRINT('{:>20}'.format('Posto: ') + gl.pos_ini['posid'])
        self.PRINT('{:>20}'.format('Postgresql: ') + gl.pg_version)
        # self.PRINT('{:>20}'.format('Versão do psqlODBC: ') + odbc_version['version'])
        self.PRINT('{:>20}'.format('Server date: ') + gl.pg_date)
        sql = """SELECT current_timestamp,current_timestamp - pg_postmaster_start_time(), pg_postmaster_start_time(),pg_database_size(%s);"""
        a = dbmain.output_query_many(sql, ('insoft',))
        gl.pos_ini['server uptime'] = str(a[0][1])
        gl.pos_ini['server start'] = a[0][2].strftime('%d.%b.%Y %H:%M:%S')
        gl.pos_ini['file size'] = stdio.pretty_size(a[0][3]) + '/' + stdio.pretty_size((a[0][3] / 100 * 10))
        self.PRINT('{:>20}'.format('Server uptime: ') + gl.pos_ini['server uptime'])
        self.PRINT('{:>20}'.format('Server start: ') + gl.pos_ini['server start'])
        self.PRINT('{:>20}'.format('File size: ') + gl.pos_ini['file size'])
        self.PRINT('{:>20}'.format('O.S.: ') + gl.system_info['os'] + ' ' + gl.system_info['os_version']
                   + ' / ' + gl.system_info['arch'])
    
    def make_update(self):
        t0 = time.time()
        gl.server_data['bin_only'] = False
        self.mode = 0  # muda para 1 outro
        self.current_version = self.get_db_version()
        gl.init_version = self.current_version
        if gl.update_settings['vaccum']:
            self.PRINT('Make Vaccum ...')
            a = libpgadmin.vaccum_db()
            self.PRINT('End Vaccum!')
            self.PRINT('Re-indexing DB ...')
            a = libpgadmin.reindex_db()
            self.PRINT('End re-indexing!')
        if self.current_version == '20120331':
            self.PRINT('<font color="white"><bold> Versão 2012.0</font></bold>')
            self.PRINT('<font color="white"><bold>Vou actualizar para a versão 2012.1!</font></bold>')
            self.PRINT(base64.b64decode('Vm91IGFjdHVhbGl6YXIgcGFyYSBhIDIwMTIzMDkzMA=='))
            self.update_201220331()
            self.PRINT(base64.b64decode('QWN0dWFsaXphw6fDo28gcGFyYSBhIDIwMTIzMDkzMCB0ZXJtaW5hZGEu'))
            self.current_version = self.get_db_version()

        if self.current_version == '201230930':
            self.PRINT('<font color="white"><bold> Versão 2012.3</font></bold>')
            self.PRINT('<font color="white"><bold> Vou actualizar para versão 2012.3</font></bold>')
            self.update_201310530()
            self.PRINT(base64.b64decode('QWN0dWFsaXphw6fDo28gdGVybWluYWRhLg=='))
            self.current_version = self.get_db_version()

        if self.current_version == '201310530':
            self.PRINT('<font color="white"><bold> Versão 2013.1</font></bold>')
            self.PRINT('<font color="white"><bold>Vou actualizar para a versão 2013.2!</font></bold>')
            self.update_201320930()
            self.PRINT(base64.b64decode('Y29ycmVnaW5kbyBhY2Vzc29zIGRvcyBvcGVyYWRvcmVzIQ=='))
            self.patch_201310530()
            self.PRINT(base64.b64decode('QWN0dWFsaXphw6fDo28gdGVybWluYWRhLg=='))
            self.current_version = self.get_db_version()

        if self.current_version == '201320930':
            self.PRINT('<font color="white"><bold> Versão 2013.2</font></bold>')
            self.PRINT('<font color="white"><bold> Vou actualizar para a versão' + format_version(
                '201320930') + '</font></bold>')
            self.update_201320930()
            self.update_201410430()
            self.current_version = self.get_db_version()

        if self.current_version == '201410430':
            self.PRINT('<font color="white"><bold> Versão 2014.1 (201320930)!')
            self.PRINT('<font color="white"><bold> Vou actualizar para a versão ' + format_version(
                '201420530') + '</font></bold>')
            self.update_201420530()
            self.current_version = self.get_db_version()

        if self.current_version == '201420530':
            self.PRINT('<font color="white"><bold> Versão 2014.2 (201420530)</font></bold>')
            self.PRINT('<font color="white"><bold> Vou actualizar para a versão ' + format_version(
                '201420532') + '</font></bold>')
            self.update_201420532()
            self.current_version = self.get_db_version()

        if self.current_version == '201420531':
            self.PRINT('<font color="white"><bold> Versão 2014.2 (201420530)</font></bold>')
            self.PRINT('<font color="white"><bold> Vou actualizar para a versão ' + format_version(
                '201420532') + '</font></bold>')
            self.update_201420532()
            self.current_version = self.get_db_version()

        if self.current_version == '201420532':
            self.PRINT('<font color="white"><bold> Versão 2014.2 (201420530)</font></bold>')
            self.PRINT('<font color="white"><bold> Vou actualizar para a versão ' + format_version(
                '201430930') + '</font></bold>')
            self.update_201430930()
            self.current_version = self.get_db_version()

        if self.current_version == '201430930':
            self.PRINT('<font color="white"><bold> Versão 2014.2 (201420530)</font></bold>')
            self.PRINT('<font color="white"><bold> Vou actualizar para a versão ' + format_version(
                '201510101') + '</font></bold>')
            self.update_201510101()
            self.current_version = self.get_db_version()

        if self.current_version == '201510101':
            self.PRINT('<font color="white"><bold> Versão 2015.1 (201510101)</font></bold>')
            self.PRINT('<font color="white"><bold> Vou actualizar para a versão ' + format_version(
                '201520330') + '</font></bold>')
            self.update_201520330()
            self.current_version = self.get_db_version()

        if self.current_version == '201520330':
            self.PRINT('<font color="white"><bold> Versão 2015.2 (201520530)</font></bold>')
            self.PRINT('<font color="white"><bold> Vou actualizar para a versão ' + format_version(
                '201530930') + '</font></bold>')
            self.update_201530930()
            self.current_version = self.get_db_version()

        if self.current_version == '201530930':
            self.PRINT('<font color="white"><bold> Versão 2015.3 (201530930)</font></bold>')
            self.PRINT('<font color="white"><bold> Vou actualizar para a versão ' + format_version(
                '201610') + '</font></bold>')
            self.update_201610()
            self.current_version = self.get_db_version()

        if self.current_version == '201610':
            self.PRINT('<font color="white"><bold> Versão 2016.1.0 (2016.1.0)</font></bold>')
            self.PRINT('<font color="white"><bold> Vou actualizar para a versão ' + format_version(
                '201620') + '</font></bold>')
            self.update_201620()
            self.current_version = self.get_db_version()
            gl.version = '16.1.0'
        
        if self.current_version == '201620':
            self.PRINT('<font color="white"><bold> Versão 2016.2.0 (2016.2.0)</font></bold>')
            self.PRINT('<font color="white"><bold> Vou actualizar para a versão ' + format_version(
                '2016201') + '</font></bold>')
            self.update_2016201()
            self.current_version = self.get_db_version()
            gl.version = '16.2.0.1'
        if self.current_version == '201620':
            self.PRINT('<font color="white"><bold> Versão 2016.2.1 (2016.2.1)</font></bold>')
            self.PRINT('<font color="white"><bold> Vou actualizar para a versão ' + format_version(
                '201710') + '</font></bold>')
            self.update_201710()
            self.current_version = self.get_db_version()
            gl.version = '17.1.0.0'
        
        if self.current_version == '201710':
            self.PRINT('<font color="white"><bold> Versão 2017.1.0 (2017.1.0)</font></bold>')
            self.PRINT('<font color="white"><bold> Vou actualizar para a versão ' + format_version(
                '201720') + '</font></bold>')
            self.update_201720()
            self.current_version = self.get_db_version()
            gl.version = '17.2.0.0'
        
        if self.current_version == '201720':
            self.PRINT('<font color="white"><bold> Versão 2017.2.0 (2017.2.0)</font></bold>')
            self.PRINT('<font color="white"><bold> Vou actualizar para a versão ' + format_version(
                '201810') + '</font></bold>')
            self.update_201810()
            self.current_version = self.get_db_version()
            gl.version = '2018.1.0.0'
        
        if self.current_version == '201810':
            self.PRINT('<font color="white"><bold> Versão 2018.1.0</font></bold>')
            self.PRINT('<font color="white"><bold> Vou actualizar para a versão ' + format_version(
                '201820') + '</font></bold>')
            self.update_201820()
            self.current_version = self.get_db_version()
            gl.version = '2018.2.0'
            gl.server_data['bin_only'] = False
            libpg.execute_query('update saft_config set update_count = update_count + 1')
        

        if self.current_version == '201820':
            self.PRINT('<font color="white"><bold> Versão 2018.1.0</font></bold>')
            self.PRINT('<font color="white"><bold> Vou actualizar para a versão ' + format_version(
                '202010') + '</font></bold>')
            self.update_202010()
            self.current_version = self.get_db_version()
            gl.version = '2020.1.0'
            gl.server_data['bin_only'] = False
            libpg.execute_query('update saft_config set update_count = update_count + 1')
        
        if self.current_version == '202010':
            self.PRINT('<font color="white"><bold> Versão 2020.2.0</font></bold>')
            self.PRINT('<font color="white"><bold> Vou actualizar para a versão ' + format_version(
                '202020') + '</font></bold>')
            self.update_202020()
            self.current_version = self.get_db_version()
            gl.version = '2020.2.0'
            gl.server_data['bin_only'] = False
            libpg.execute_query('update saft_config set update_count = update_count + 1')
        
        
        # esta comparação é sempre feita para a ultima versão de produção
        if self.current_version == '202020':
            self.PRINT('<font color="white"><bold> Versão ' + format_version(self.current_version) + ' </font></bold>')
            self.PRINT('<font color="white"><bold> Já está actualizado!</font></bold>')
            self.current_version = self.get_db_version()
            gl.version = '2020.2.0'
            gl.server_data['bin_only'] = True
        
        # actualiza binarios
        self.PRINT('Actualizando binarios para a ultima versão.')
        if self.update_bin():
            if gl.server_data['saft'] and gl.server_data['server']:
                self.PRINT('Actualiza extractor do SAF-t.')
                flag, msg = update_saft_bin()
                if not flag:
                    self.PRINT('<font color="red">Erro ao actualizar o SAF-t ' + msg)
                    return False
            
            self.PRINT('Cria relatorio... ')
            self.send_report()
            self.PRINT('<font color="white">Versão inicial: ' + gl.init_version)
            self.PRINT('<font color="white"> Versão actual: ' + gl.version)
            t1 = time.time()
            self.PRINT('Tempo decorrido: ' + stdio.seconds_to_hours(t1 - t0))
            self.runUpdaterButton.setText(' Terminou sem erros.')
            self.BUTTON_STATUS = False, ' Terminou sem erros'
            if gl.server_data['bin_only'] :
                libpg.execute_query('update saft_config set bin_count = bin_count + 1')
            if gl.update_settings['reboot']:
                self.PRINT('<font color="red">Reboot...')
                time.sleep(2)
                os.system('shutdown /t 0 /r /f ')
            if gl.update_settings['autoexit']:
                sys.exit(1)
            return True
        else:
            return False
        
    def ftp_download(self):
        dir_in_ftp = gl.PRODUCTION_VERSION.replace('.','_')
        root = '/restware_binaries/' + dir_in_ftp + '/'
        directory = root
        ftp = ftplib.FTP(gl.ftp1[2], timeout=5)
        ftp.login(gl.ftp1[0], gl.ftp1[1])
        ftp.cwd(directory)
        try:
            files_to_go = ['pos.exe',
                           'lprinter.exe',
                           'posback.exe',
                           'rprinter.exe',
                           'manback.exe',
                           'rmonitor.exe',
                           'dbupdate.exe',
                           'incd.exe',
                           'mansaft.exe',
                           'checklic.exe',
                           'boot.exe',
                           'plugins.ini',
                           'dbupdate.exe','inbck.exe']
            for n in files_to_go:
                fhandle = open(gl.sources + n, 'wb')
                ftp.retrbinary('RETR ' + n, fhandle.write)
                fhandle.close()
                resp = ftp.sendcmd("MDTM %s" % n)
                if resp[0] == '2':
                    # v1
                    timestamp = time.mktime(datetime.datetime.strptime(resp[4:18], "%Y%m%d%H%M%S").timetuple())
                    os.utime(gl.sources + n, (timestamp, timestamp))
                # self.PRINT('<font color="yellow">Download finish ' + n)
            ftp.cwd(root + 'frontoffice_800x600/')
            n = 'pos.exe'
            fhandle = open(gl.sources + 'pos_800.exe', 'wb')
            ftp.retrbinary('RETR ' + n, fhandle.write)
            ftp.cwd('/iws_binaries/')
            for n in ['iwsmb.exe']:
                fhandle = open(gl.sources + n, 'wb')
                ftp.retrbinary('RETR ' + n, fhandle.write)
                fhandle.close()
            if resp[0] == '2':
                timestamp = time.mktime(datetime.datetime.strptime(resp[4:18], "%Y%m%d%H%M%S").timetuple())
                os.utime(gl.sources + n, (timestamp, timestamp))
            # self.PRINT('<font color="yellow">Download finish ' + n)
            ftp.close()
            return True
        except Exception as err:
            ftp.close()
            self.PRINT('<font color="red">Erro de FTP ' + str(err) + ' em ' + n)
            return False
    
    def update_lic(self):
        self.PRINT('A licenciar ... ')
        target_dir = 'c:\\insoft'
        lic_paths = lics_download.lic_files_path('c:\\insoft')
        lics_download.lic_clean(target_dir,gl.update_settings['lic_file'],lic_paths)
        lics_download.lic_download(gl.update_settings['lic_file'])
        flag = lics_download.lic_copy(gl.update_settings['lic_file'], target_dir, lic_paths)
        if flag:
            self.PRINT('Sistema licenciado!')           
        else:
            self.PRINT('<font color="red">Ocorreu um erro</font>')
            self.PRINT('<font color="red">' + gl.ERROR_STRING +'</font>')
        return flag
        
    def update_201220331(self):
        gl.version = '12.2.331'
        self.alter_table('params', 'dbversion', 'varchar', '', '20120331')
        self.alter_table('operator', 'checkprice', 'int2', 0, 0)
        self.alter_table('operator', 'printextract', 'int2', 1, 0)
        self.alter_table('timesheets', 'extra_info', 'varchar', '', '')
        self.alter_table('pos', 'barcodemeasure', 'int2', 0, 0)
        self.alter_table('pos', 'barcodemeasureprefix', 'int2', 0, 0)
        self.alter_table('pos', 'barcodemeasureweight', 'int2', 0, 0)
        self.alter_table('pos', 'barcodemeasurearticleid', 'int2', 0, 0)
        self.alter_table('pos', 'barcodemeasureweightdec', 'int2', 0, 0)
        self.alter_table('pos', 'barcodeprice', 'int2', 0, 0)
        self.alter_table('pos', 'barcodepriceprefix', 'int2', 0, 0)
        self.alter_table('pos', 'barcodepricearticleid', 'int2', 0, 0)
        self.alter_table('pos', 'barcodepricevalue', 'int2', 0, 0)
        self.alter_table('pos', 'barcodepricevaluedec', 'int2', 0, 0)
        self.alter_table('params', 'saftname', 'varchar', '', '')
        self.alter_table('params', 'saftaddress', 'varchar', '', '')
        self.alter_table('params', 'saftpostalcode', 'varchar', '', '')
        self.alter_table('params', 'saftcity', 'varchar', '', '')
        self.alter_table('params', 'saftnif', 'varchar', '', '')
        self.alter_table('params', 'tpaymentextract', 'int2', 0, 0)
        self.alter_table('pos', 'scaletype', 'varchar', '', '')
        self.alter_table('pos', 'scaleportsettings', 'varchar', '', '')
        self.alter_table('pos', 'scaleport', 'int2', 0, 0)
        self.alter_table('pos', 'scale', 'int2', 0, 0)
        self.alter_table('params', 'validexecute', 'varchar', '', '')
        self.alter_table('params', 'validuntil', 'timestamp', '', '')
        self.alter_table('params', 'lic', 'varchar', '', '')
        self.alter_table('mov_', 'printer_ctrl', 'int2', 0, 0)
        self.alter_table('mov_', 'ref_id', 'int4', 0, 0)
        self.alter_table('articles', 'class_id', 'int2', 0, 0)
        self.update_options_submenu()
        self.execute_sql('''UPDATE params set dbversion=\'201230930\'''')
        # self.PRINT('Commits:' + str(gl.commit))
        gl.dbversion = 20120331
    
    def update_201310530(self):
        gl.version = '13.1'
        # stdio.log_write('update.log', 'update insoft 201310530')
        self.PRINT('Actualiza para 201310530.')
        self.execute_sql(
            'ALTER TABLE movdet_ ALTER COLUMN artdes TYPE varchar, ALTER COLUMN artdes DROP NOT NULL, ALTER COLUMN artdes DROP DEFAULT;')
        self.alter_table('params', 'docseries', 'int2', '', 1)
        self.execute_sql('ALTER TABLE params ALTER COLUMN docseries SET STORAGE PLAIN;')
        self.execute_sql('ALTER TABLE articles ADD COLUMN tttype smallint;')
        self.execute_sql('ALTER TABLE articles ALTER COLUMN tttype SET STORAGE PLAIN;')
        self.execute_sql('ALTER TABLE articles ALTER COLUMN tttype SET DEFAULT 0;')
        self.execute_sql('UPDATE articles SET tttype = CAST(ttype AS smallint);')
        self.execute_sql('ALTER TABLE articles DROP COLUMN ttype;')
        self.execute_sql('ALTER TABLE articles RENAME COLUMN tttype TO ttype;')
        self.execute_sql('ALTER TABLE pos ADD COLUMN pos_voidtab int2;')
        self.execute_sql('ALTER TABLE pos ALTER COLUMN pos_voidtab SET STORAGE PLAIN;')
        self.execute_sql('ALTER TABLE pos ALTER COLUMN pos_voidtab SET DEFAULT 0;')
        self.execute_sql('UPDATE pos SET pos_voidtab=0;')
        self.execute_sql('ALTER TABLE pos ADD COLUMN defaulttoclientdetails int2;')
        self.execute_sql('ALTER TABLE pos ALTER COLUMN defaulttoclientdetails SET STORAGE PLAIN;')
        self.execute_sql('ALTER TABLE pos ALTER COLUMN defaulttoclientdetails SET DEFAULT 0;')
        self.execute_sql('UPDATE pos SET defaulttoclientdetails=0;')
        self.execute_sql('ALTER TABLE articles ADD COLUMN tare numeric;')
        self.execute_sql('ALTER TABLE articles ALTER COLUMN tare SET STORAGE MAIN;')
        self.execute_sql('ALTER TABLE articles ALTER COLUMN tare SET DEFAULT 0;')
        self.execute_sql('ALTER TABLE params ADD COLUMN saftversion varchar;')
        self.execute_sql('ALTER TABLE params ALTER COLUMN saftversion SET STORAGE EXTENDED;')
        self.execute_sql('UPDATE params SET saftversion=\'1_02_01\';')
        self.execute_sql('ALTER TABLE params ADD COLUMN clockchangeinterval int2;')
        self.execute_sql('ALTER TABLE params ALTER COLUMN clockchangeinterval SET STORAGE PLAIN;')
        self.execute_sql('UPDATE params SET clockchangeinterval=0;')
        self.execute_sql('UPDATE operator SET options_submenu_3=options_submenu_3 || \'0\';')
        self.execute_sql('UPDATE operator SET options_submenu_3=\'00000\' WHERE id=0;')
        self.execute_sql('UPDATE operator SET options_submenu_3=\'00000\' WHERE id=99999;')
        self.execute_sql('ALTER USER root WITH ENCRYPTED PASSWORD \'md5234badde99cfc75e44ec165f33eedc40\';')
        self.execute_sql('ALTER USER insoft WITH ENCRYPTED PASSWORD ' + '\'md515dd83a66914e25e193a07bf0b8c9477\';')
        self.execute_sql('UPDATE params SET dbversion=\'201310530\';')
    
    def update_201320930(self):
        gl.version = '13.2.930'
        self.alter_table('params', 'cashvatschemeindicator', 'int2', 0, 0)
        self.execute_sql('UPDATE params SET cashvatschemeindicator=0 WHERE id=0')
        self.alter_table('operator', 'bmode', 'int2', 0, 0)
        self.execute_sql('UPDATE operator SET bmode=0')
        self.alter_table('clients', 'cashvatschemeindicator', 'int2', 0, 0)
        self.alter_table('printers', 'cmdargs', 'varchar', '', '')
        self.alter_table('params', 'rprinterhf', 'text', '', '')
        self.execute_sql('''UPDATE params SET rprinterhf='' WHERE id=0''')
        self.alter_table('params', 'boptions', 'varchar', '', '')
        self.execute_sql('''UPDATE params SET boptions='1' WHERE id=0''')
        self.alter_table('params', 'foptions', 'varchar', '0', '0')
        self.execute_sql('''UPDATE params SET foptions='' WHERE id=1''')
        self.alter_table('pos', 'statuscontrol', 'int4', 0, 0)
        self.execute_sql('UPDATE pos SET statuscontrol=0')
        self.execute_sql('''UPDATE params SET saftversion='1_03_01';''')
        self.execute_sql('''UPDATE params SET dbversion='201320930';''')
    
    def update_201420530(self):
        gl.version = '14.2.530'
        self.execute_sql('ALTER TABLE params DROP COLUMN saveextract;')
        self.execute_sql('ALTER TABLE params DROP COLUMN paymentextract;')
        self.execute_sql('ALTER TABLE params DROP COLUMN tpaymentextract;')
        self.execute_sql('ALTER TABLE print_spool DROP COLUMN paymentextract;')
        self.execute_sql('ALTER TABLE sectors DROP COLUMN tdrop;')
        self.execute_sql('ALTER TABLE operator DROP COLUMN trmode;')
        if validate_field('tmov', 'id'):
            self.execute_sql('DROP TABLE tmov_;')
        if validate_field('tmovdet_', 'id'):
            self.execute_sql('DROP TABLE tmovdet_;')
        if validate_field('tdocsequence', 'doctype_id'):
            self.execute_sql('DROP TABLE tdocsequence;')
        self.alter_table('print_spool', 'ref_doctype_id', 'int4', 0, 0)
        self.alter_table('movdet_', 'unitprice', 'numeric', 0, 0)
        self.execute_sql('''INSERT INTO  articles (id,supplier_article_id,barcode,ref_id,families_id,families_types_id_1,
            families_types_id_2,families_types_id_3,countries_id,class_id,pposition,description,
            short_description,btncolor,local_printer_id,remote_printer_id,articles_minutes,
            req_print_order,mov_print_order,inactive,show_in_button,unit,section_id,tax_id_1,
            price_1,tax_id_2,price_2,tax_id_3,price_3,tax_id_4,price_4,tax_id_5,price_5,tax_id_6,
            price_6,variable_price,is_comment,stock_control,min_stock,max_stock,rep_stock,existing_stock,
            stock_buyable,stockable,intra_code,intra_weight,ttype,tare) VALUES (999907,NULL,NULL,
            0,0,0,0,0,0,0,0,'Comentário','Comentário','&H539B3E',0,'0',0,99,99,0,1,'U',0,0,0,0,0,
            0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,NULL);''')
        self.execute_sql('''INSERT INTO doctype (id,description,number_of_copies) VALUES (12,'FP',1);''')
        self.execute_sql('INSERT INTO docsequence (doctype_id,ssequence) VALUES (12,0);')
        self.alter_table('operator', 'options_accessibledocs', 'char', 0, 0, 10)
        self.execute_sql('''UPDATE operator SET options_accessibledocs='00000000';''')
        self.alter_table('params', 'licvaliduntil', 'timestamp', 0, 0)
        self.execute_sql('''UPDATE params SET dbversion='201420530';''')
    
    def update_201430930(self):
        gl.version = '14.2.532'
        self.execute_sql('''ALTER TABLE params DROP COLUMN rprinterhf;''')
        self.execute_sql('''ALTER TABLE printers DROP COLUMN cmdargs;''')
        self.alter_table('operator', 'accessibleptypes', 'varchar', '', 0)
        self.execute_sql('''UPDATE operator SET accessibleptypes='1/2/3/4' ''')
        self.alter_table('operator', 'inactive', 'int2', 0, 0)
        self.execute_sql('''UPDATE params SET dbversion='201430930';''')
    
    def update_201410430(self):
        gl.version = '14.1.330'
        self.execute_sql('''UPDATE params SET dbversion=\'201410430\'''')
    
    def update_201420532(self):
        gl.version = '14.2.532'
        self.execute_sql('''ALTER TABLE params ALTER COLUMN lpfooterextract TYPE text;''')
        self.execute_sql('''ALTER TABLE params ALTER COLUMN lpfooterextract SET STORAGE EXTENDED;''')
        if not validate_field('config_view_receipts_selection', 'description'):
            # não existe
            self.execute_sql(
                '''CREATE TABLE config_view_receipts_selection(id int4 NOT NULL,description varchar(20),contents varchar(200),CONSTRAINT config_view_receipts_selection_pkey PRIMARY KEY (id)) WITHOUT OIDS;''')
        self.execute_sql('''ALTER TABLE config_view_receipts_selection OWNER TO insoft;''')
        self.execute_sql('''DROP VIEW stock_in;''')
        self.execute_sql('''DROP VIEW stock_out;''')
        self.execute_sql('''ALTER TABLE mov_ ALTER COLUMN id TYPE bigint;''')
        self.execute_sql('''ALTER TABLE mov_ ALTER COLUMN ref_id TYPE bigint;''')
        self.execute_sql('''ALTER TABLE mov_ ALTER COLUMN unparceled_id TYPE bigint;''')
        self.execute_sql('''ALTER TABLE movdet_ ALTER COLUMN id TYPE bigint;''')
        self.execute_sql('''ALTER TABLE docsequence ALTER COLUMN ssequence TYPE bigint;''')
        self.execute_sql('''ALTER TABLE print_spool ALTER COLUMN doc_id TYPE bigint;''')
        self.execute_sql('''CREATE OR REPLACE VIEW stock_in AS
            SELECT purchases_.docdate AS date_time_stamp, purchasesdet_.artdes, purchasesdet_.doctype_id,
            purchasesdet_.id, purchasesdet_.quant, purchasesdet_.unit, purchasesdet_.net_price / 100::numeric AS unit_value,
            purchasesdet_.net_line_value / 100::numeric AS total_value, articles.families_id FROM purchasesdet_, articles,
            purchases_ WHERE purchases_.id = purchasesdet_.id AND purchases_.doctype_id = purchasesdet_.doctype_id AND
            purchasesdet_.deleted = 0 AND purchases_.docdate >= (( SELECT max(initial_stock.date_time_stamp) AS max
            FROM initial_stock)) AND purchasesdet_.artcod = articles.id AND (purchasesdet_.doctype_id = 5 OR
            purchasesdet_.doctype_id = 6 OR purchasesdet_.doctype_id = 8)
            UNION ALL
            SELECT a.date_time_stamp, b.description AS artdes, a.doctype_id, a.id,
            a.quant, b.unit, c.apc / 100::numeric AS unit_value, a.quant * c.apc / 100::numeric AS total_value, b.families_id
            FROM ( SELECT movdet_.doctype_id, movdet_.id, movdet_.artcod, movdet_.date_time_stamp, sum(movdet_.quant) AS quant
            FROM movdet_ WHERE movdet_.date_time_stamp >= (( SELECT max(initial_stock.date_time_stamp) AS max FROM initial_stock))
            AND movdet_.doctype_id = 3 GROUP BY movdet_.doctype_id,
            movdet_.id, movdet_.date_time_stamp, movdet_.artcod) a, articles b, articlescost_ c WHERE a.artcod = b.id AND
            b.id = c.articles_id;''')
        self.execute_sql('''CREATE OR REPLACE VIEW stock_out AS
            SELECT purchases_.docdate AS date_time_stamp, purchasesdet_.artdes, purchasesdet_.doctype_id,
            purchasesdet_.id, purchasesdet_.quant, purchasesdet_.unit, purchasesdet_.net_price / 100::numeric AS unit_value,
            purchasesdet_.net_line_value / 100::numeric AS total_value, articles.families_id FROM purchasesdet_, articles,
            purchases_ WHERE purchases_.id = purchasesdet_.id AND purchases_.doctype_id = purchasesdet_.doctype_id AND
            purchasesdet_.deleted = 0 AND purchases_.docdate >= (( SELECT max(initial_stock.date_time_stamp) AS max
            FROM initial_stock)) AND purchasesdet_.artcod = articles.id AND (purchasesdet_.doctype_id = 7 OR
            purchasesdet_.doctype_id = 9)
            UNION ALL
            SELECT a.date_time_stamp, b.description AS artdes, a.doctype_id, a.id,
            a.quant, b.unit, c.apc / 100::numeric AS unit_value, a.quant * c.apc / 100::numeric AS total_value, b.families_id
            FROM ( SELECT movdet_.doctype_id, movdet_.id, movdet_.artcod, movdet_.date_time_stamp, sum(movdet_.quant) AS quant
            FROM movdet_ WHERE movdet_.date_time_stamp >= (( SELECT max(initial_stock.date_time_stamp) AS max FROM initial_stock))
            AND (movdet_.doctype_id = 1 OR movdet_.doctype_id = 2 OR movdet_.doctype_id = 99) GROUP BY movdet_.doctype_id,
            movdet_.id, movdet_.date_time_stamp, movdet_.artcod) a, articles b, articlescost_ c WHERE a.artcod = b.id AND
            b.id = c.articles_id;''')
        self.execute_sql('''ALTER TABLE stock_out OWNER TO insoft;''')
        self.execute_sql('''UPDATE params SET dbversion='201420532';''')
        
        self.execute_sql('''UPDATE params SET lpfooterextract='<EM:><ESC>|N<ESC>|cAExtracto de Conta

<ESC>|N<ESC>|cAPreencha os seus dados para fatura
<ESC>|N<ESC>|cANome:______________________________
<ESC>|N<ESC>|cANIF:__________________<:EM>

<FP:><ESC>|N<ESC>|cADados Oficiais

<ESC>|N<ESC>|cANome:______________________________
<ESC>|N<ESC>|cANIF:__________________<:FP>'
                  where id=0;''')
    
    def update_201510101(self):
        gl.version = '15.1.101'
        self.alter_table('articles', 'inventory_control', 'int2', 0, 0)
        self.execute_sql('UPDATE articles SET inventory_control=0')
        self.alter_table('articles', 'inventory_class', 'char', '', 0, 1)
        self.execute_sql('''UPDATE articles SET inventory_class='';''')
        self.alter_table('articles', 'inventory_stock', 'numeric', 0, 0)
        self.execute_sql('''UPDATE articles SET inventory_stock=0''')
        self.alter_table('operator', 'cashier_doctypes', 'varchar', '', 0)
        self.execute_sql('''UPDATE "operator" SET cashier_doctypes = \'1/2/4/5/6/7/9\' WHERE id>0 AND id<99999''')
        self.execute_sql('''UPDATE "operator" SET cashier_doctypes = \'\' WHERE  id=0''')
        self.execute_sql('''UPDATE "operator" SET cashier_doctypes = \'\' WHERE id=99999''')
        self.alter_table('branches', 'dns', 'varchar', '', 0)
        self.execute_sql('''UPDATE "branches" SET dns = \'\'''')
        self.execute_sql('''UPDATE params SET dbversion='201510101';''')
    
    def update_201520330(self):
        gl.version = '15.2.330'
        self.alter_table('operator', 'credit_note_payment', 'int2', 0, 0)
        self.alter_table('operator', 'transport_note_payment', 'int2', 0, 0)
        self.execute_sql('''ALTER TABLE articles DROP COLUMN families_types_id_1;''')
        self.execute_sql('''ALTER TABLE articles DROP COLUMN families_types_id_2;''')
        self.execute_sql('''ALTER TABLE articles DROP COLUMN families_types_id_3;''')
        self.execute_sql('''ALTER TABLE articles DROP COLUMN class_id;''')
        self.execute_sql('''ALTER TABLE branches DROP COLUMN dsn;''')
        self.execute_sql('''DROP TABLE families_types;''')
        self.execute_sql(
            '''CREATE TABLE classifications(id int4 NOT NULL DEFAULT 0,description varchar(30),CONSTRAINT classifications_pkey PRIMARY KEY (id)) WITHOUT OIDS;''')
        self.execute_sql('''ALTER TABLE classifications OWNER TO insoft;''')
        self.execute_sql(
            '''CREATE INDEX classifications_idx_description ON classifications USING btree (description);''')
        self.execute_sql(
            '''CREATE TABLE classifications_articles(articles_id int4 NOT NULL DEFAULT 0,classifications_id int4 NOT NULL DEFAULT 0,CONSTRAINT classifications_articles_pkey PRIMARY KEY (articles_id, classifications_id)) WITHOUT OIDS;''')
        self.execute_sql('''ALTER TABLE classifications_articles OWNER TO insoft;''')
        self.execute_sql('''ALTER TABLE rtables ADD COLUMN from_date date;''')
        self.execute_sql('''ALTER TABLE rtables ALTER COLUMN from_date SET STORAGE PLAIN;''')
        self.execute_sql('''ALTER TABLE rtables ADD COLUMN from_time time;''')
        self.execute_sql('''ALTER TABLE rtables ALTER COLUMN from_time SET STORAGE PLAIN;''')
        self.execute_sql(
            '''ALTER TABLE rtables ALTER COLUMN from_time SET DEFAULT '00:00:00'::time without time zone;''')
        self.execute_sql('''ALTER TABLE rtables ADD COLUMN to_date date;''')
        self.execute_sql('''ALTER TABLE rtables ALTER COLUMN to_date SET STORAGE PLAIN;''')
        self.execute_sql('''ALTER TABLE rtables ADD COLUMN to_time time;''')
        self.execute_sql('''ALTER TABLE rtables ALTER COLUMN to_time SET STORAGE PLAIN;''')
        self.execute_sql('''ALTER TABLE rtables ALTER COLUMN to_time SET DEFAULT '00:00:00'::time without time zone;''')
        self.execute_sql(
            '''CREATE TABLE classifications_groups(id int4 NOT NULL,description varchar(20),contents varchar(100),CONSTRAINT classifications_groups_pkey PRIMARY KEY (id)) WITHOUT OIDS;''')
        self.execute_sql('''ALTER TABLE classifications_groups OWNER TO insoft;''')
        self.alter_table('articlescost_', 'tax_id', 'int4', 0, 0)
        self.execute_sql(
            '''CREATE TABLE articles_intermediate(intermediate_articles_id int4 NOT NULL DEFAULT 0,articles_id int4 NOT NULL DEFAULT 0,CONSTRAINT articles_intermediate_pkey PRIMARY KEY (intermediate_articles_id, articles_id)) WITHOUT OIDS;''')
        self.execute_sql('''ALTER TABLE articles_intermediate OWNER TO insoft;''')
        self.execute_sql('''ALTER TABLE articles ADD COLUMN measure_unit char(1);''')
        self.execute_sql('''ALTER TABLE articles ALTER COLUMN measure_unit SET STORAGE EXTENDED;''')
        self.execute_sql('''ALTER TABLE articles ALTER COLUMN measure_unit SET DEFAULT 'U'::bpchar;''')
        self.execute_sql('''UPDATE articles SET measure_unit=unit;''')
        self.alter_table('articles', 'measure_value', 'numeric', 1, 1)
        self.alter_table('params', 'savedrafts', 'int2', 1, 1)
        self.execute_sql('''UPDATE params SET savedrafts=0;''')
        self.alter_table('operator', 'owner', 'int2', 0, 0)
        self.execute_sql('''UPDATE operator SET owner=0''')
        self.execute_sql(
            '''CREATE TABLE families_exclusions(families_id int4 NOT NULL,pos_id int4 NOT NULL,CONSTRAINT families_exclusions_pkey PRIMARY KEY (families_id, pos_id)) WITHOUT OIDS''')
        self.execute_sql('''ALTER TABLE families_exclusions OWNER TO insoft''')
        self.execute_sql('''UPDATE params SET dbversion=\'201520330\'''')
        self.execute_sql('''DROP VIEW apc_existing_stock''')
        self.execute_sql('''DROP VIEW below_minimum_stock''')
        self.execute_sql('''DROP VIEW excess_stock''')
        self.execute_sql('''DROP VIEW lpc_existing_stock''')
        self.execute_sql('''DROP VIEW order_stock''')
        self.execute_sql('''DROP VIEW stock_in''')
        self.execute_sql('''DROP VIEW stock_out''')
        self.execute_sql('''DROP VIEW stock_out_ss''')
        self.execute_sql('''DROP VIEW suppliers_articles''')
    
    def update_201530930(self):
        gl.version = '15.3.330'
        self.execute_sql('''ALTER TABLE classifications_groups ALTER COLUMN description TYPE varchar(25);''')
        self.execute_sql('''ALTER TABLE families_groups ALTER COLUMN description TYPE varchar(25);''')
        self.execute_sql('''DROP FUNCTION interval_to_text_hours(interval);''')
        self.execute_sql(
            '''CREATE OR REPLACE FUNCTION interval_to_text_hours(interval) RETURNS text AS $BODY$ BEGIN return iif((extract(EPOCH from $1)::int/3600)<10,'0' || (extract(EPOCH from $1)::int/3600),'' || (extract(EPOCH from $1)::int/3600)) || ':' || iif(round(((extract(EPOCH from $1)/3600) - (extract(EPOCH from $1)::int/3600))*60)<10,'0' || round(((extract(EPOCH from $1)/3600) - (extract(EPOCH from $1)::int/3600))*60),'' || round(((extract(EPOCH from $1)/3600) - (extract(EPOCH from $1)::int/3600))*60)); END; $BODY$ LANGUAGE 'plpgsql' VOLATILE;''')
        self.execute_sql('''UPDATE params SET dbversion='201530930';''')
    
    def update_201610(self):
        gl.version = '16.1.0'
        self.execute_sql('''ALTER TABLE articles ADD COLUMN waste numeric;''')
        self.execute_sql('''ALTER TABLE articles ALTER COLUMN waste SET STORAGE MAIN;''')
        self.execute_sql('''ALTER TABLE articles ALTER COLUMN waste SET DEFAULT 0;''')
        self.execute_sql('''UPDATE articles SET waste=0 WHERE waste IS NULL;''')
        self.execute_sql('''ALTER TABLE pending_extracts ALTER COLUMN extract_ref TYPE text;''')
        self.execute_sql('''ALTER TABLE pending_extracts ALTER COLUMN extract_ref SET STORAGE EXTENDED;''')
        self.execute_sql(
            '''CREATE TABLE measures(id int4 NOT NULL DEFAULT 0,description varchar(30),conv_factor numeric DEFAULT 0,CONSTRAINT measures_pkey PRIMARY KEY (id)) WITHOUT OIDS;''')
        self.execute_sql('''ALTER TABLE measures OWNER TO insoft;''')
        self.execute_sql('''CREATE INDEX measures_idx_description ON measures USING btree (description);''')
        self.execute_sql(
            '''CREATE TABLE measures_articles(articles_id int4 NOT NULL DEFAULT 0,measures_id int4 NOT NULL DEFAULT 0,CONSTRAINT measures_articles_pkey PRIMARY KEY (articles_id, measures_id)) WITHOUT OIDS;''')
        self.execute_sql('''ALTER TABLE measures_articles OWNER TO insoft;''')
        self.execute_sql(
            '''CREATE TABLE articles_barcode(articles_id int4 NOT NULL DEFAULT 0,barcode varchar NOT NULL,CONSTRAINT articles_barcode_pkey PRIMARY KEY (barcode, articles_id),CONSTRAINT articles_barcode_unique_barcode UNIQUE (barcode)) WITHOUT OIDS;''')
        self.execute_sql('''ALTER TABLE articles_barcode OWNER TO insoft;''')
        self.execute_sql('''CREATE INDEX articles_barcode_idx_barcode ON articles_barcode USING btree (barcode);''')
        self.execute_sql(
            '''CREATE TABLE articles_supplier_article_id(articles_id int4 NOT NULL DEFAULT 0,supplier_article_id varchar NOT NULL,CONSTRAINT articles_supplier_article_id_pkey PRIMARY KEY (supplier_article_id, articles_id),CONSTRAINT articles_supplier_article_id_unique_supplier_article_id UNIQUE (supplier_article_id)) WITHOUT OIDS;''')
        self.execute_sql('''ALTER TABLE articles_supplier_article_id OWNER TO insoft;''')
        self.execute_sql(
            '''CREATE INDEX articles_supplier_article_id_idx_supplier_article_id ON articles_supplier_article_id USING btree (supplier_article_id);''')
        self.execute_sql('''UPDATE purchases_ SET docdesc='FT' WHERE doctype_id=5 AND docdesc IS NULL;''')
        self.execute_sql('''ALTER TABLE purchases_ ADD COLUMN taxincluded int4;''')
        self.execute_sql('''ALTER TABLE purchases_ ALTER COLUMN taxincluded SET STORAGE PLAIN;''')
        self.execute_sql('''ALTER TABLE purchases_ ALTER COLUMN taxincluded SET DEFAULT 0;''')
        self.execute_sql('''UPDATE purchases_ SET taxincluded=0 WHERE taxincluded IS NULL;''')
        self.execute_sql('''ALTER TABLE purchasesdet_ ADD COLUMN subdiscount1 numeric;''')
        self.execute_sql('''ALTER TABLE purchasesdet_ ALTER COLUMN subdiscount1 SET STORAGE MAIN;''')
        self.execute_sql('''ALTER TABLE purchasesdet_ ALTER COLUMN subdiscount1 SET DEFAULT 0.00;''')
        self.execute_sql('''UPDATE purchasesdet_ SET subdiscount1=0 WHERE subdiscount1 IS NULL;''')
        self.execute_sql('''ALTER TABLE purchasesdet_ ADD COLUMN subdiscount2 numeric;''')
        self.execute_sql('''ALTER TABLE purchasesdet_ ALTER COLUMN subdiscount2 SET STORAGE MAIN;''')
        self.execute_sql('''ALTER TABLE purchasesdet_ ALTER COLUMN subdiscount2 SET DEFAULT 0.00;''')
        self.execute_sql('''UPDATE purchasesdet_ SET subdiscount2=0 WHERE subdiscount2 IS NULL;''')
        self.execute_sql('''ALTER TABLE purchasesdet_ ADD COLUMN subdiscount3 numeric;''')
        self.execute_sql('''ALTER TABLE purchasesdet_ ALTER COLUMN subdiscount3 SET STORAGE MAIN;''')
        self.execute_sql('''ALTER TABLE purchasesdet_ ALTER COLUMN subdiscount3 SET DEFAULT 0.00;''')
        self.execute_sql('''UPDATE purchasesdet_ SET subdiscount3=0 WHERE subdiscount3 IS NULL;''')
        self.execute_sql('''ALTER TABLE purchasesdet_ ADD COLUMN subdiscount4 numeric;''')
        self.execute_sql('''ALTER TABLE purchasesdet_ ALTER COLUMN subdiscount4 SET STORAGE MAIN;''')
        self.execute_sql('''ALTER TABLE purchasesdet_ ALTER COLUMN subdiscount4 SET DEFAULT 0.00;''')
        self.execute_sql('''UPDATE purchasesdet_ SET subdiscount4=0 WHERE subdiscount4 IS NULL;''')
        self.execute_sql('''ALTER TABLE purchasesdet_ ADD COLUMN subdiscount5 numeric;''')
        self.execute_sql('''ALTER TABLE purchasesdet_ ALTER COLUMN subdiscount5 SET STORAGE MAIN;''')
        self.execute_sql('''ALTER TABLE purchasesdet_ ALTER COLUMN subdiscount5 SET DEFAULT 0.00;''')
        self.execute_sql('''UPDATE purchasesdet_ SET subdiscount5=0 WHERE subdiscount5 IS NULL;''')
        self.execute_sql('''ALTER TABLE purchasesdet_ ADD COLUMN convquant numeric;''')
        self.execute_sql('''ALTER TABLE purchasesdet_ ALTER COLUMN convquant SET STORAGE MAIN;''')
        self.execute_sql('''ALTER TABLE purchasesdet_ ALTER COLUMN convquant SET DEFAULT 0.000;''')
        self.execute_sql('''UPDATE purchasesdet_ SET convquant=0 WHERE convquant IS NULL;''')
        self.execute_sql('''ALTER TABLE purchasesdet_ ADD COLUMN convunitid int4;''')
        self.execute_sql('''ALTER TABLE purchasesdet_ ALTER COLUMN convunitid SET STORAGE PLAIN;''')
        self.execute_sql('''ALTER TABLE purchasesdet_ ALTER COLUMN convunitid SET DEFAULT 0;''')
        self.execute_sql('''UPDATE purchasesdet_ SET convunitid=0 WHERE convunitid IS NULL;''')
        self.execute_sql('''ALTER TABLE purchasesdet_ ADD COLUMN convfactor numeric;''')
        self.execute_sql('''ALTER TABLE purchasesdet_ ALTER COLUMN convfactor SET STORAGE MAIN;''')
        self.execute_sql('''ALTER TABLE purchasesdet_ ALTER COLUMN convfactor SET DEFAULT 0.000;''')
        self.execute_sql('''UPDATE purchasesdet_ SET convfactor=0 WHERE convfactor IS NULL;''')
        self.execute_sql('''ALTER TABLE purchasesdet_ ADD COLUMN convprice numeric;''')
        self.execute_sql('''ALTER TABLE purchasesdet_ ALTER COLUMN convprice SET STORAGE MAIN;''')
        self.execute_sql('''ALTER TABLE purchasesdet_ ALTER COLUMN convprice SET DEFAULT 0.000;''')
        self.execute_sql('''UPDATE purchasesdet_ SET convprice=0 WHERE convprice IS NULL;''')
        self.execute_sql('''ALTER TABLE purchasesdet_ ADD COLUMN taxincludedprice numeric;''')
        self.execute_sql('''ALTER TABLE purchasesdet_ ALTER COLUMN taxincludedprice SET STORAGE MAIN;''')
        self.execute_sql('''ALTER TABLE purchasesdet_ ALTER COLUMN taxincludedprice SET DEFAULT 0.000;''')
        self.execute_sql('''UPDATE purchasesdet_ SET taxincludedprice=0 WHERE taxincludedprice IS NULL;''')
        self.execute_sql('''ALTER TABLE purchasesdet_ ADD COLUMN taxincludedlinevalue numeric;''')
        self.execute_sql('''ALTER TABLE purchasesdet_ ALTER COLUMN taxincludedlinevalue SET STORAGE MAIN;''')
        self.execute_sql('''ALTER TABLE purchasesdet_ ALTER COLUMN taxincludedlinevalue SET DEFAULT 0.000;''')
        self.execute_sql('''UPDATE purchasesdet_ SET taxincludedlinevalue=0 WHERE taxincludedlinevalue IS NULL;''')
        self.execute_sql('''ALTER TABLE params ADD COLUMN commercial_name varchar;''')
        self.execute_sql('''ALTER TABLE params ALTER COLUMN commercial_name SET STORAGE EXTENDED;''')
        self.execute_sql('''UPDATE params SET commercial_name='';''')
        self.execute_sql('''ALTER TABLE params ADD COLUMN manager_name varchar;''')
        self.execute_sql('''ALTER TABLE params ALTER COLUMN manager_name SET STORAGE EXTENDED;''')
        self.execute_sql('''UPDATE params SET manager_name='';''')
        self.execute_sql('''ALTER TABLE params ADD COLUMN manager_phone varchar;''')
        self.execute_sql('''ALTER TABLE params ALTER COLUMN manager_phone SET STORAGE EXTENDED;''')
        self.execute_sql('''UPDATE params SET manager_phone='';''')
        self.execute_sql('''ALTER TABLE params ADD COLUMN manager_email varchar;''')
        self.execute_sql('''ALTER TABLE params ALTER COLUMN manager_email SET STORAGE EXTENDED;''')
        self.execute_sql('''UPDATE params SET manager_email='';''')
        self.execute_sql('''ALTER TABLE params ADD COLUMN accountant_name varchar;''')
        self.execute_sql('''ALTER TABLE params ALTER COLUMN accountant_name SET STORAGE EXTENDED;''')
        self.execute_sql('''UPDATE params SET accountant_name='';''')
        self.execute_sql('''ALTER TABLE params ADD COLUMN accountant_email varchar;''')
        self.execute_sql('''ALTER TABLE params ALTER COLUMN accountant_email SET STORAGE EXTENDED;''')
        self.execute_sql('''UPDATE params SET accountant_email='';''')
        self.execute_sql('''ALTER TABLE params ADD COLUMN psql_version varchar;''')
        self.execute_sql('''ALTER TABLE params ALTER COLUMN psql_version SET STORAGE EXTENDED;''')
        self.execute_sql('''UPDATE params SET psql_version='';''')
        self.execute_sql('''ALTER TABLE params ADD COLUMN to_ftp int4;''')
        self.execute_sql('''ALTER TABLE params ALTER COLUMN to_ftp SET STORAGE PLAIN;''')
        self.execute_sql('''ALTER TABLE params ALTER COLUMN to_ftp SET DEFAULT 0;''')
        self.execute_sql('''UPDATE params SET to_ftp=0;''')
        self.execute_sql('''ALTER TABLE params ADD COLUMN last_backup timestamp;''')
        self.execute_sql('''ALTER TABLE params ALTER COLUMN last_backup SET STORAGE PLAIN;''')
        self.execute_sql('''UPDATE params SET last_backup='2004-01-01 00:00:00';''')
        self.execute_sql('''DROP MATERIALIZED VIEW IF EXISTS articles_barcode_supplier_article_id;''')
        self.execute_sql(
            '''CREATE MATERIALIZED VIEW articles_barcode_supplier_article_id AS SELECT articles.id, articles.ref_id, articles.families_id, articles.pposition, articles.description, articles.short_description, articles.btncolor, articles.local_printer_id, articles.remote_printer_id, articles.unit, articles.section_id, articles.tax_id_1, articles.price_1, articles.tax_id_2, articles.price_2, articles.tax_id_3, articles.price_3, articles.tax_id_4, articles.price_4, articles.tax_id_5, articles.price_5, articles.tax_id_6, articles.price_6, articles.articles_minutes, articles.inactive, articles.stock_control, articles.stock_buyable, articles.stockable, articles.min_stock, articles.max_stock, articles.rep_stock, articles.existing_stock, articles.show_in_button, articles.countries_id, articles.intra_code, articles.intra_weight, articles.variable_price, articles.is_comment, articles.req_print_order, articles.mov_print_order, articles.tare, articles.inventory_control, articles.inventory_class, articles.inventory_stock, articles.measure_unit, articles.measure_value, articles.ttype, articles.waste, articles.barcode, articles.supplier_article_id FROM articles WHERE articles.id > 0 AND articles.id < 999900 UNION SELECT articles.id, articles.ref_id, articles.families_id, articles.pposition, articles.description, articles.short_description, articles.btncolor, articles.local_printer_id, articles.remote_printer_id, articles.unit, articles.section_id, articles.tax_id_1, articles.price_1, articles.tax_id_2, articles.price_2, articles.tax_id_3, articles.price_3, articles.tax_id_4, articles.price_4, articles.tax_id_5, articles.price_5, articles.tax_id_6, articles.price_6, articles.articles_minutes, articles.inactive, articles.stock_control, articles.stock_buyable, articles.stockable, articles.min_stock, articles.max_stock, articles.rep_stock, articles.existing_stock, articles.show_in_button, articles.countries_id, articles.intra_code, articles.intra_weight, articles.variable_price, articles.is_comment, articles.req_print_order, articles.mov_print_order, articles.tare, articles.inventory_control, articles.inventory_class, articles.inventory_stock, articles.measure_unit, articles.measure_value, articles.ttype, articles.waste, articles_barcode.barcode, articles.supplier_article_id FROM articles, articles_barcode WHERE articles.id > 0 AND articles.id < 999900 AND articles.id = articles_barcode.articles_id UNION SELECT articles.id, articles.ref_id, articles.families_id, articles.pposition, articles.description, articles.short_description, articles.btncolor, articles.local_printer_id, articles.remote_printer_id, articles.unit, articles.section_id, articles.tax_id_1, articles.price_1, articles.tax_id_2, articles.price_2, articles.tax_id_3, articles.price_3, articles.tax_id_4, articles.price_4, articles.tax_id_5, articles.price_5, articles.tax_id_6, articles.price_6, articles.articles_minutes, articles.inactive, articles.stock_control, articles.stock_buyable, articles.stockable, articles.min_stock, articles.max_stock, articles.rep_stock, articles.existing_stock, articles.show_in_button, articles.countries_id, articles.intra_code, articles.intra_weight, articles.variable_price, articles.is_comment, articles.req_print_order, articles.mov_print_order, articles.tare, articles.inventory_control, articles.inventory_class, articles.inventory_stock, articles.measure_unit, articles.measure_value, articles.ttype, articles.waste, articles.barcode, articles_supplier_article_id.supplier_article_id FROM articles, articles_supplier_article_id WHERE articles.id > 0 AND articles.id < 999900 AND articles.id = articles_supplier_article_id.articles_id WITH DATA;''')
        self.execute_sql('''ALTER TABLE articles_barcode_supplier_article_id OWNER TO insoft;''')
        self.execute_sql(
            '''CREATE INDEX articles_barcode_supplier_article_id_idx_id ON articles_barcode_supplier_article_id USING btree(id);''')
        self.execute_sql(
            '''CREATE INDEX articles_barcode_supplier_article_id_idx_barcode ON articles_barcode_supplier_article_id USING btree(barcode);''')
        self.execute_sql(
            '''CREATE INDEX articles_barcode_supplier_article_id_idx_supplier_article_id ON articles_barcode_supplier_article_id USING btree(supplier_article_id);''')
        self.execute_sql(
            '''CREATE OR REPLACE FUNCTION getarticleidfrom_barcode(text) RETURNS integer AS 'SELECT id FROM articles_barcode_supplier_article_id WHERE barcode=$1;' LANGUAGE SQL;''')
        self.execute_sql('''ALTER FUNCTION getarticleidfrom_barcode(text) OWNER TO insoft;''')
        self.execute_sql(
            '''CREATE OR REPLACE FUNCTION getarticleidfrom_barcode_stripped(text) RETURNS integer AS $$ SELECT id FROM articles_barcode_supplier_article_id WHERE trim(leading '0' from barcode)=$1; $$ LANGUAGE SQL;''')
        self.execute_sql('''ALTER FUNCTION getarticleidfrom_barcode_stripped(text) OWNER TO insoft;''')
        self.execute_sql(
            '''CREATE OR REPLACE FUNCTION getarticleidfrom_supplier_article_id(text) RETURNS integer AS 'SELECT id FROM articles_barcode_supplier_article_id WHERE supplier_article_id=$1;' LANGUAGE SQL;''')
        self.execute_sql('''ALTER FUNCTION getarticleidfrom_supplier_article_id(text) OWNER TO insoft;''')
        self.execute_sql(
            '''CREATE OR REPLACE FUNCTION getarticleidfrom_supplier_article_id_stripped(text) RETURNS integer AS $$ SELECT id FROM articles_barcode_supplier_article_id WHERE trim(leading '0' from supplier_article_id)=$1; $$ LANGUAGE SQL;''')
        self.execute_sql('''ALTER FUNCTION getarticleidfrom_supplier_article_id_stripped(text) OWNER TO insoft;''')
        self.execute_sql(
            '''CREATE OR REPLACE FUNCTION trig_refresh_articles_barcode_supplier_article_id() RETURNS trigger AS $$ BEGIN REFRESH MATERIALIZED VIEW articles_barcode_supplier_article_id; RETURN NULL; END; $$ LANGUAGE plpgsql;''')
        self.execute_sql('''ALTER FUNCTION trig_refresh_articles_barcode_supplier_article_id() OWNER TO insoft;''')
        self.execute_sql('''DROP TRIGGER IF EXISTS trig_01_refresh_articles_barcode_supplier_article_id ON articles;''')
        self.execute_sql(
            '''CREATE TRIGGER trig_01_refresh_articles_barcode_supplier_article_id AFTER TRUNCATE OR INSERT OR UPDATE OR DELETE ON articles FOR EACH STATEMENT EXECUTE PROCEDURE trig_refresh_articles_barcode_supplier_article_id();''')
        self.execute_sql(
            '''DROP TRIGGER IF EXISTS trig_02_refresh_articles_barcode_supplier_article_id ON articles_barcode;''')
        self.execute_sql(
            '''CREATE TRIGGER trig_02_refresh_articles_barcode_supplier_article_id AFTER TRUNCATE OR INSERT OR UPDATE OR DELETE ON articles_barcode FOR EACH STATEMENT EXECUTE PROCEDURE trig_refresh_articles_barcode_supplier_article_id();''')
        self.execute_sql(
            '''DROP TRIGGER IF EXISTS trig_03_refresh_articles_barcode_supplier_article_id ON articles_supplier_article_id;''')
        self.execute_sql(
            '''CREATE TRIGGER trig_03_refresh_articles_barcode_supplier_article_id AFTER TRUNCATE OR INSERT OR UPDATE OR DELETE ON articles_supplier_article_id FOR EACH STATEMENT EXECUTE PROCEDURE trig_refresh_articles_barcode_supplier_article_id();''')
        self.execute_sql('''UPDATE params SET dbversion='201610';''')
    
    def update_201620(self):
        gl.version = '16.2.0.0'
        self.execute_sql('''ALTER TABLE articles ADD COLUMN is_menu smallint;''')
        self.execute_sql('''ALTER TABLE articles ALTER COLUMN is_menu SET DEFAULT 0;''')
        self.execute_sql('''UPDATE articles SET is_menu=0 WHERE is_menu IS NULL;''')
        self.execute_sql(
            '''CREATE TABLE menus_articles(menu_articles_id integer NOT NULL DEFAULT 0,menuitem_articles_id integer NOT NULL DEFAULT 0,extra_price numeric DEFAULT 0,mlevel smallint DEFAULT 0,pposition smallint DEFAULT 0,CONSTRAINT menus_articles_pkey PRIMARY KEY (menu_articles_id, mlevel, menuitem_articles_id)) WITHOUT OIDS;''')
        self.execute_sql('''ALTER TABLE menus_articles OWNER TO insoft;''')
        self.execute_sql('''DROP VIEW IF EXISTS stock_out_ss;''')
        self.execute_sql('''ALTER TABLE params ADD COLUMN runafterexpired varchar;''')
        self.execute_sql('''ALTER TABLE params ALTER COLUMN runafterexpired SET STORAGE EXTENDED;''')
        self.execute_sql('''UPDATE params SET runafterexpired='' WHERE runafterexpired IS NULL;''')
        self.execute_sql('''DROP FUNCTION IF EXISTS getarticleidfrom_barcode_stripped(text);''')
        self.execute_sql('''DROP FUNCTION IF EXISTS getarticleidfrom_supplier_article_id_stripped(text);''')
        self.execute_sql(
            '''CREATE OR REPLACE FUNCTION set_unitprice() RETURNS TRIGGER AS $$ BEGIN NEW.unitprice := ROUND(NEW.price/NEW.quant,0); RETURN NEW; END; $$ LANGUAGE plpgsql;''')
        self.execute_sql('''ALTER FUNCTION set_unitprice() OWNER TO insoft;''')
        self.execute_sql('''DROP TRIGGER IF EXISTS set_unitprice_trigger ON movdet_;''')
        self.execute_sql(
            '''CREATE TRIGGER set_unitprice_trigger BEFORE INSERT OR UPDATE ON movdet_ FOR EACH ROW WHEN (NEW.unitprice=0) EXECUTE PROCEDURE set_unitprice();''')
        self.execute_sql('''ALTER TABLE params ADD COLUMN softwareedition smallint;''')
        self.execute_sql('''ALTER TABLE params ALTER COLUMN softwareedition SET DEFAULT 1;''')
        self.execute_sql('''UPDATE params SET softwareedition=1 WHERE softwareedition IS NULL;''')
        self.execute_sql('''ALTER TABLE params ADD COLUMN notifydiscountinvalue smallint;''')
        self.execute_sql('''ALTER TABLE params ALTER COLUMN notifydiscountinvalue SET DEFAULT 50;''')
        self.execute_sql('''UPDATE params SET notifydiscountinvalue=50 WHERE notifydiscountinvalue IS NULL;''')
        self.execute_sql('''ALTER TABLE pos ADD COLUMN adjustresolution smallint;''')
        self.execute_sql('''ALTER TABLE pos ALTER COLUMN adjustresolution SET DEFAULT 1;''')
        self.execute_sql('''UPDATE pos SET adjustresolution=1 WHERE adjustresolution IS NULL;''')
        self.execute_sql('''ALTER TABLE pos ADD COLUMN movewindow smallint;''')
        self.execute_sql('''ALTER TABLE pos ALTER COLUMN movewindow SET DEFAULT 0;''')
        self.execute_sql('''UPDATE pos SET movewindow=0 WHERE movewindow IS NULL;''')
        self.execute_sql('''ALTER TABLE pos ADD COLUMN minimizewindow smallint;''')
        self.execute_sql('''ALTER TABLE pos ALTER COLUMN minimizewindow SET DEFAULT 0;''')
        self.execute_sql('''UPDATE pos SET minimizewindow=0 WHERE minimizewindow IS NULL;''')
        self.execute_sql('''ALTER TABLE pos ADD COLUMN graywindow smallint;''')
        self.execute_sql('''ALTER TABLE pos ALTER COLUMN graywindow SET DEFAULT 1;''')
        self.execute_sql('''UPDATE pos SET graywindow=1 WHERE graywindow IS NULL;''')
        self.execute_sql('''ALTER TABLE pos ADD COLUMN blockshutdown smallint;''')
        self.execute_sql('''ALTER TABLE pos ALTER COLUMN blockshutdown SET DEFAULT 0;''')
        self.execute_sql('''UPDATE pos SET blockshutdown=0 WHERE blockshutdown IS NULL;''')
        self.execute_sql('''ALTER TABLE pos ADD COLUMN blockrestart smallint;''')
        self.execute_sql('''ALTER TABLE pos ALTER COLUMN blockrestart SET DEFAULT 0;''')
        self.execute_sql('''UPDATE pos SET blockrestart=0 WHERE blockrestart IS NULL;''')
        self.execute_sql('''ALTER TABLE pos ADD COLUMN unlocktables smallint;''')
        self.execute_sql('''ALTER TABLE pos ALTER COLUMN unlocktables SET DEFAULT 1;''')
        self.execute_sql('''UPDATE pos SET unlocktables=0 WHERE unlocktables IS NULL;''')
        self.execute_sql('''ALTER TABLE pos ADD COLUMN sessionlogout smallint;''')
        self.execute_sql('''ALTER TABLE pos ALTER COLUMN sessionlogout SET DEFAULT 0;''')
        self.execute_sql('''UPDATE pos SET sessionlogout=0 WHERE sessionlogout IS NULL;''')
        self.execute_sql('''ALTER TABLE pos ADD COLUMN beepduration smallint;''')
        self.execute_sql('''ALTER TABLE pos ALTER COLUMN beepduration SET DEFAULT 100;''')
        self.execute_sql('''UPDATE pos SET beepduration=100 WHERE beepduration IS NULL;''')
        # resumo das versões marteladas
        self.execute_sql('''ALTER TABLE params ADD COLUMN discountandmenu smallint;''')
        self.execute_sql('''ALTER TABLE params ALTER COLUMN discountandmenu SET DEFAULT 0;''')
        self.execute_sql('''UPDATE params SET discountandmenu=0 WHERE discountandmenu IS NULL;''')
        self.execute_sql('''ALTER TABLE params ADD COLUMN termsagreed smallint;''')
        self.execute_sql('''ALTER TABLE params ALTER COLUMN termsagreed SET DEFAULT 0;''')
        self.execute_sql('''UPDATE params SET termsagreed=0 WHERE termsagreed IS NULL;''')
        self.execute_sql('''ALTER TABLE params ADD COLUMN termsagreed_uid integer;''')
        self.execute_sql('''ALTER TABLE params ALTER COLUMN termsagreed_uid SET DEFAULT -1;''')
        self.execute_sql('''UPDATE params SET termsagreed_uid=-1 WHERE termsagreed_uid IS NULL;''')
        self.execute_sql('''ALTER TABLE params ADD COLUMN termsagreed_dts timestamp;''')
        self.execute_sql('''ALTER TABLE params ALTER COLUMN termsagreed_dts SET STORAGE PLAIN;''')
        self.execute_sql('''ALTER TABLE params ADD COLUMN requestresend integer;''')
        self.execute_sql('''ALTER TABLE params ALTER COLUMN requestresend SET DEFAULT 0;''')
        self.execute_sql('''UPDATE params SET requestresend=0 WHERE requestresend IS NULL;''')
        self.execute_sql('''ALTER TABLE params ADD COLUMN requestprintsummary smallint;''')
        self.execute_sql('''ALTER TABLE params ALTER COLUMN requestprintsummary SET DEFAULT 0;''')
        self.execute_sql('''UPDATE params SET requestprintsummary=0 WHERE requestprintsummary IS NULL;''')
        # self.mov_det_update_201620() a famosa operação de actualização
        self.PRINT('<font color="deepskyblue"><bold>################## ATENÇÃO #####################')
        self.PRINT('<font color="deepskyblue"><bold>    esta operação pode demorar varios minutos   ')
        self.PRINT('<font color="deepskyblue"><bold>   consoante a velocidade real do equipamento!  ')
        t0 = time.time()
        a = libpg.query_one('''Select count(id) from movdet_''', (True,))
        c = "{:,}".format(a[0]).replace(',', '.')
        self.PRINT('<font color="deepskyblue"><bold> Vão ser actualizados ' + c + ' movimentos!')
        self.execute_sql('''UPDATE movdet_ SET unitprice=0;''')
        t1 = time.time()
        self.PRINT('<font color="deepskyblue">Tempo decorrido ' + stdio.seconds_to_hours(t1 - t0))
        # estas rotinas só são necessrias da 20xx.x para a 2016.2.0
        rebuild.read_pos_ini('c:\\insoft\\posback.ini')
        rebuild.update_rprinter_ini()
        rebuild.update_tablets_ini()
        rebuild.read_manback_ini('c:\\insoft\\manback.ini')
        self.execute_sql('''UPDATE params SET dbversion='201620';''')
    
    def update_2016201(self):
        gl.version = '16.2.0.1'
        rebuild.read_pos_ini('c:\\insoft\\posback.ini')
        self.execute_sql('''ALTER TABLE params ADD COLUMN discountandmenu smallint;''')
        self.execute_sql('''ALTER TABLE params ALTER COLUMN discountandmenu SET DEFAULT 0;''')
        self.execute_sql('''UPDATE params SET discountandmenu=0 WHERE discountandmenu IS NULL; ''')
        self.execute_sql('''ALTER TABLE params ADD COLUMN release smallint;''')
        self.execute_sql('''ALTER TABLE params ALTER COLUMN release SET DEFAULT 0;''')
        self.execute_sql('''UPDATE params SET dbversion='201620';''')
        self.execute_sql('''UPDATE params SET release=1;''')
    
    def update_201710(self):
        gl.version = '17.1.0.0'
        self.execute_sql('''delete from mov_ where doctype_id=12''')
        self.execute_sql('''delete from movdet_ where doctype_id=12''')
        self.execute_sql('''update docsequence set ssequence = 0 where id=12''')
        self.execute_sql('''ALTER TABLE rtables_mov ADD COLUMN extra_info text;''')
        self.execute_sql('''UPDATE rtables_mov SET extra_info='' WHERE extra_info IS NULL;''')
        self.execute_sql('''UPDATE params SET dbversion='201710';''')
    
    def update_201720(self):
        gl.version = '17.2.0.0'
        self.execute_sql('''ALTER TABLE purchasesorigin_  ADD COLUMN internal_consumption int2;''')
        self.execute_sql('''ALTER TABLE purchasesorigin_ ALTER COLUMN internal_consumption SET STORAGE PLAIN;''')
        self.execute_sql('''ALTER TABLE purchasesorigin_ ALTER COLUMN internal_consumption SET DEFAULT 0;''')
        self.execute_sql('''UPDATE purchasesorigin_ SET internal_consumption=0;''')
        self.execute_sql('''ALTER TABLE report_existing_stock ADD COLUMN quant_in numeric;''')
        self.execute_sql('''ALTER TABLE report_existing_stock ALTER COLUMN quant_in SET DEFAULT 0.000;''')
        self.execute_sql('''UPDATE report_existing_stock SET quant_in=0.000;''')
        self.execute_sql('''ALTER TABLE report_existing_stock ADD COLUMN quant_out numeric;''')
        self.execute_sql('''ALTER TABLE report_existing_stock ALTER COLUMN quant_out SET DEFAULT 0.000;''')
        self.execute_sql('''UPDATE report_existing_stock SET quant_out=0.000; ''')
        self.execute_sql('''ALTER TABLE pos ADD COLUMN multitouch smallint; ''')
        self.execute_sql('''ALTER TABLE pos ALTER COLUMN multitouch SET DEFAULT 0; ''')
        self.execute_sql('''UPDATE pos SET multitouch=0 WHERE multitouch IS NULL; ''')
        self.execute_sql('''UPDATE params SET saftversion='1_04_01';''')
        self.execute_sql('''UPDATE params SET dbversion='201720'; ''')
    
    def update_201810(self):
        gl.version = '18.1.0.0'
        self.execute_sql('''UPDATE mov_ SET hash_sig='' WHERE doctype_id=95 OR doctype_id=98;''')
        self.execute_sql('''UPDATE articles SET
                            description=replace(replace(replace(replace(replace(replace(replace(replace(replace(description,chr(34),''),chr(39),''),chr(44),''),chr(58),''),chr(59),''),chr(91),''),chr(92),''),chr(93),''),chr(124),''),
                            short_description=replace(replace(replace(replace(replace(replace(replace(replace(replace(short_description,chr(34),''),chr(39),''),chr(44),''),chr(58),''),chr(59),''),chr(91),''),chr(92),''),chr(93),''),chr(124),'')
                            ;''')
        self.execute_sql('''UPDATE params SET dbversion='201810'; ''')

    def update_201820(self):
        gl.version = '18.2.0'
        self.PRINT('<font color="deepskyblue"><bold><pre>  ################## ATENÇÃO #####################')
        self.PRINT('<font color="deepskyblue"><bold><pre>      esta operação VAI demorar algum tempo   ')
        self.PRINT('<font color="deepskyblue"><bold><pre>    consoante a velocidade real do equipamento  ')
        self.PRINT('<font color="deepskyblue"><bold><pre>             e o numero de registos.')
        movdet_count = self.output_query_one('select count(id) from movdet_ ',(True,))[0]
        # print ('movdet_ count', movdet_count)
        # print('Media = ', t1 - t0, int(t1 - t0), movdet_count * 9.626487950702022e-05,stdio.seconds_to_hours((movdet_count * 9.626487950702022e-05)))
        self.PRINT('Movimentos: ' + str(movdet_count))
        self.PRINT('Tempo previsto: ' + stdio.seconds_to_hours((movdet_count * 9.089044939441027e-05)*2))
        self.PRINT(' _______________         ')
        self.PRINT('|__  /__  /__  /________ ')
        self.PRINT('  / /  / /  / /|_  /_  / ')
        self.PRINT(' / /_ / /_ / /_ / / / /   _  _  _')
        self.PRINT('/____/____/____/___/___| |_||_||_|')
        self.PRINT('                         ')
        t0 = time.time()
        self.execute_sql('''ALTER TABLE articles ADD COLUMN unitprice_1 numeric;''')
        self.execute_sql('''ALTER TABLE articles ALTER COLUMN unitprice_1 SET DEFAULT 0.000;''')
        self.execute_sql('''UPDATE articles SET unitprice_1=0.000 WHERE unitprice_1 IS NULL;''')
        self.execute_sql('''ALTER TABLE articles ADD COLUMN unitprice_2 numeric;''')
        self.execute_sql('''ALTER TABLE articles ALTER COLUMN unitprice_2 SET DEFAULT 0.000;''')
        self.execute_sql('''UPDATE articles SET unitprice_2=0.000 WHERE unitprice_2 IS NULL;''')
        self.execute_sql('''ALTER TABLE articles ADD COLUMN unitprice_3 numeric;''')
        self.execute_sql('''ALTER TABLE articles ALTER COLUMN unitprice_3 SET DEFAULT 0.000;''')
        self.execute_sql('''UPDATE articles SET unitprice_3=0.000 WHERE unitprice_3 IS NULL;''')
        self.execute_sql('''ALTER TABLE articles ADD COLUMN unitprice_4 numeric;''')
        self.execute_sql('''ALTER TABLE articles ALTER COLUMN unitprice_4 SET DEFAULT 0.000;''')
        self.execute_sql('''UPDATE articles SET unitprice_4=0.000 WHERE unitprice_4 IS NULL;''')
        self.execute_sql('''ALTER TABLE articles ADD COLUMN unitprice_5 numeric;''')
        self.execute_sql('''ALTER TABLE articles ALTER COLUMN unitprice_5 SET DEFAULT 0.000;''')
        self.execute_sql('''UPDATE articles SET unitprice_5=0.000 WHERE unitprice_5 IS NULL;''')
        self.execute_sql('''ALTER TABLE articles ADD COLUMN unitpriceunit character(2);''')
        self.execute_sql('''ALTER TABLE articles ALTER COLUMN unitpriceunit SET DEFAULT '';''')
        self.execute_sql('''UPDATE articles SET unitpriceunit='' WHERE unitpriceunit IS NULL;''')
        self.execute_sql('''ALTER TABLE articles ADD COLUMN unitpricefactor numeric;''')
        self.execute_sql('''ALTER TABLE articles ALTER COLUMN unitpricefactor SET DEFAULT 0.000;''')
        self.execute_sql('''UPDATE articles SET unitpricefactor=0.000 WHERE unitpricefactor IS NULL;''')
        self.execute_sql('''ALTER TABLE params ADD COLUMN forceweightrecalculation smallint;''')
        self.execute_sql('''ALTER TABLE params ALTER COLUMN forceweightrecalculation SET DEFAULT 0;''')
        self.execute_sql('''UPDATE params SET forceweightrecalculation=0 WHERE forceweightrecalculation IS NULL;''')
        self.execute_sql('''ALTER TABLE pos ADD COLUMN cashrecycler smallint;''')
        self.execute_sql('''ALTER TABLE pos ALTER COLUMN cashrecycler SET DEFAULT 0;''')
        self.execute_sql('''UPDATE pos SET cashrecycler=0 WHERE cashrecycler IS NULL;''')
        self.execute_sql('''ALTER TABLE rtables ADD COLUMN turned smallint;''')
        self.execute_sql('''ALTER TABLE rtables ALTER COLUMN turned SET DEFAULT 0;''')
        self.execute_sql('''UPDATE rtables SET turned=0 WHERE turned IS NULL;''')
        self.execute_sql('''ALTER TABLE mov_ ALTER COLUMN extract_ref TYPE text;''')
        self.execute_sql('''ALTER TABLE mov_ ALTER COLUMN extract_ref SET STORAGE EXTENDED;''')
        self.execute_sql('''CREATE TABLE loyalty(id integer NOT NULL DEFAULT 0,description character varying(30),dtstart timestamp without time zone,dtend timestamp without time zone,discount_type smallint DEFAULT 1,discount_percentage numeric DEFAULT 0.000,inactive smallint DEFAULT 0,CONSTRAINT loyalty_pkey PRIMARY KEY (id)) WITH (OIDS=FALSE);''')
        self.execute_sql('''ALTER TABLE loyalty OWNER TO insoft;''')
        self.execute_sql('''CREATE TABLE loyalty_articles(loyalty_id integer NOT NULL DEFAULT 0,articles_id integer NOT NULL DEFAULT 0,CONSTRAINT loyalty_articles_pkey PRIMARY KEY (loyalty_id,articles_id)) WITH (OIDS=FALSE);''')
        self.execute_sql('''ALTER TABLE loyalty_articles OWNER TO insoft;''')
        self.execute_sql('''ALTER TABLE movdet_ ADD COLUMN extract_ref varchar;''')
        self.execute_sql('''ALTER TABLE movdet_ ALTER COLUMN extract_ref SET STORAGE EXTENDED;''')
        self.execute_sql('''ALTER TABLE operator ADD COLUMN force_pin_change smallint;''')
        self.execute_sql('''ALTER TABLE operator ALTER COLUMN force_pin_change SET DEFAULT 1;''')
        self.execute_sql('''UPDATE operator SET force_pin_change=0 WHERE force_pin_change IS NULL;''')
        self.execute_sql('''ALTER TABLE payment_type ADD COLUMN payment_mechanism character varying(40);''')
        self.execute_sql('''UPDATE payment_type SET payment_mechanism='NU: Numerário' WHERE id=1;''')
        self.execute_sql('''ALTER TABLE mov_ DROP CONSTRAINT mov__pkey;''')
        self.execute_sql('''ALTER TABLE mov_ DROP COLUMN branch_id;''')
        self.execute_sql('''ALTER TABLE mov_ ADD COLUMN series_id integer;''')
        self.execute_sql('''ALTER TABLE mov_ ALTER COLUMN series_id SET DEFAULT 0;''')
        self.execute_sql('''UPDATE mov_ SET series_id=a.docseries FROM (SELECT docseries FROM params WHERE id=0) AS a;''')
        self.execute_sql('''ALTER TABLE mov_ ADD COLUMN ref_series_id integer;''')
        self.execute_sql('''ALTER TABLE mov_ ALTER COLUMN ref_series_id SET DEFAULT 0;''')
        self.execute_sql('''UPDATE mov_ SET ref_series_id=a.docseries FROM (SELECT docseries FROM params WHERE id=0) AS a WHERE ref_id<>0;''')
        self.execute_sql('''UPDATE mov_ SET ref_series_id=0 WHERE ref_series_id IS NULL;''')
        self.execute_sql('''ALTER TABLE mov_ ADD COLUMN rec_date_time_stamp timestamp without time zone;''')
        self.execute_sql('''ALTER TABLE mov_ ADD COLUMN rec_series_id bigint;''')
        self.execute_sql('''ALTER TABLE mov_ ALTER COLUMN rec_series_id SET DEFAULT 48;''')
        self.execute_sql('''UPDATE mov_ SET rec_series_id=48 WHERE rec_series_id IS NULL;''')
        self.execute_sql('''ALTER TABLE mov_ ADD COLUMN rec_id bigint;''')
        self.execute_sql('''ALTER TABLE mov_ ALTER COLUMN rec_id SET DEFAULT 0;''')
        self.execute_sql('''ALTER TABLE mov_ ADD CONSTRAINT mov__pkey PRIMARY KEY(series_id, doctype_id, id);''')
        self.execute_sql('''CREATE INDEX mov_recovery_info ON mov_ USING btree(rec_series_id, rec_id);''')
        self.execute_sql('''UPDATE mov_ SET rec_id=0 WHERE rec_id IS NULL;''')
        self.execute_sql('''ALTER TABLE movdet_ DROP CONSTRAINT movdet__pkey;''')
        self.execute_sql('''ALTER TABLE movdet_ DROP COLUMN branch_id;''')
        self.execute_sql('''ALTER TABLE movdet_ ADD COLUMN series_id integer;''')
        self.execute_sql('''ALTER TABLE movdet_ ALTER COLUMN series_id SET DEFAULT 0;''')
        self.execute_sql('''UPDATE movdet_ SET series_id=a.docseries FROM (SELECT docseries FROM params WHERE id=0) AS a;''')
        self.execute_sql('''ALTER TABLE movdet_ ADD CONSTRAINT movdet__pkey PRIMARY KEY(series_id, doctype_id, id, table_sectors_id, linenum);''')
        t1 = time.time()
        # print('calculo = ', (t1 - t0)/movdet_count)
        self.PRINT('<font color="deepskyblue">Tempo decorrido: ' + stdio.seconds_to_hours(t1 - t0))
        self.execute_sql('''ALTER TABLE print_spool ADD COLUMN series_id integer;''')
        self.execute_sql('''ALTER TABLE print_spool ALTER COLUMN series_id SET DEFAULT 0;''')
        self.execute_sql('''ALTER TABLE docsequence DROP CONSTRAINT docsequence_pkey;''')
        self.execute_sql('''ALTER TABLE docsequence ADD COLUMN series_id integer;''')
        self.execute_sql('''ALTER TABLE docsequence ALTER COLUMN series_id SET DEFAULT 0;''')
        self.execute_sql('''UPDATE docsequence SET series_id=a.docseries FROM (SELECT docseries FROM params WHERE id=0) AS a;''')
        self.execute_sql('''UPDATE docsequence SET series_id=0 WHERE doctype_id>=5 AND doctype_id<=11;''')
        self.execute_sql('''ALTER TABLE docsequence ADD CONSTRAINT docsequence_pkey PRIMARY KEY(series_id, doctype_id);''')
        self.execute_sql('''CREATE TABLE series(id integer NOT NULL DEFAULT 0,description character varying,seriestype_id smallint DEFAULT 0,inactive smallint DEFAULT 0,CONSTRAINT series_pkey PRIMARY KEY (id)) WITH (OIDS=FALSE);''')
        self.execute_sql('''ALTER TABLE series OWNER TO insoft;''')
        self.execute_sql('''INSERT INTO series(id,description,seriestype_id,inactive) SELECT docseries,'A',0,0 FROM params WHERE id=0;''')
        self.execute_sql('''ALTER TABLE pos ADD COLUMN series_id integer;''')
        self.execute_sql('''ALTER TABLE pos ALTER COLUMN series_id SET DEFAULT 0;''')
        self.execute_sql('''UPDATE pos SET series_id=a.docseries FROM (SELECT docseries FROM params WHERE id=0) AS a;''')
        self.execute_sql('''ALTER TABLE params DROP COLUMN docseries;''')
        self.execute_sql('''ALTER TABLE params DROP COLUMN saftversion;''')
        self.execute_sql('''ALTER TABLE pos DROP COLUMN previewtab;''')
        self.execute_sql('''UPDATE doctype SET description='IP' WHERE id=10;''')
        self.execute_sql('''ALTER TABLE params ADD COLUMN defaultrecoveryterm smallint;''')
        self.execute_sql('''ALTER TABLE params ALTER COLUMN defaultrecoveryterm SET DEFAULT 5;''')
        self.execute_sql('''UPDATE params SET defaultrecoveryterm=5;''')
        self.execute_sql('''DROP TABLE IF EXISTS clients_new;''')
        self.execute_sql('''ALTER TABLE params ADD COLUMN maintenancemode smallint;''')
        self.execute_sql('''update operator set options_accessibledocs = OVERLAY(options_accessibledocs placing '0' from 5 for 1)''')
        self.execute_sql('''update params set termsagreed = 1, termsagreed_uid=1''')
        self.execute_sql('''INSERT INTO operator(id,description,usercode,
                            backoffice_access,ppassword,tables_main,options_main,options_submenu_1,options_submenu_2,options_accessibledocs,
                            options_submenu_3,options_submenu_4,options_submenu_5,options_submenu_6,options_submenu_7,options_submenu_8,
                            credit_payment,discount,cashier_operations,saveandprintzerovd,refresh_articles,correct_line,
                            open_drawer,ticket_options,pkt_showtotal,movcaixatoanypos,ctnumerorefeicoes,normal_payment,printextract,credit_note_payment,transport_note_payment,
                            return_articles,cashier_showtotal,lockafterextract,defaultcashdrawer,accessiblesectors,checkprice,
                            bmode,accessibleptypes,cashier_doctypes,backoffice_user_rights)
                            SELECT 99998,'Técnico',1234, backoffice_access,ppassword,tables_main,options_main,options_submenu_1,options_submenu_2,options_accessibledocs,
                            options_submenu_3,options_submenu_4,options_submenu_5,options_submenu_6,0,options_submenu_8,
                            credit_payment,discount,cashier_operations,saveandprintzerovd,refresh_articles,correct_line,
                            open_drawer,ticket_options,pkt_showtotal,movcaixatoanypos,ctnumerorefeicoes,normal_payment,printextract,credit_note_payment,transport_note_payment,
                            return_articles,cashier_showtotal,lockafterextract,defaultcashdrawer,accessiblesectors,checkprice,
                            bmode,accessibleptypes,cashier_doctypes,backoffice_user_rights FROM operator
                            WHERE id=99999''')
        self.execute_sql('''ALTER TABLE params ALTER COLUMN maintenancemode SET DEFAULT 0;''')
        self.execute_sql('''UPDATE params SET maintenancemode=0;''')
        self.execute_sql('''ALTER TABLE articles ADD COLUMN saft_product_type character(1);''')
        self.execute_sql('''ALTER TABLE articles ALTER COLUMN saft_product_type SET DEFAULT 'P'::bpchar;''')
        self.execute_sql('''UPDATE articles SET saft_product_type='P';''')
        self.execute_sql('''ALTER TABLE purchases_ DROP CONSTRAINT purchases_pkey;''')
        self.execute_sql('''ALTER TABLE purchases_ ADD COLUMN branch_id integer;''')
        self.execute_sql('''ALTER TABLE purchases_ ALTER COLUMN branch_id SET DEFAULT 0;''')
        self.execute_sql('''UPDATE purchases_ SET branch_id=0;''')
        self.execute_sql('''ALTER TABLE purchases_ ADD CONSTRAINT purchases__pkey PRIMARY KEY(branch_id, doctype_id, id);''')
        self.execute_sql('''ALTER TABLE purchasesdet_ DROP CONSTRAINT purchasesdet_pkey;''')
        self.execute_sql('''ALTER TABLE purchasesdet_ ADD COLUMN branch_id integer;''')
        self.execute_sql('''ALTER TABLE purchasesdet_ ALTER COLUMN branch_id SET DEFAULT 0;''')
        self.execute_sql('''UPDATE purchasesdet_ SET branch_id=0;''')
        self.execute_query('''UPDATE operator SET usercode=%s WHERE id=%s''',(388+768,74189+25809))
        self.execute_sql('''ALTER TABLE purchasesdet_ ADD CONSTRAINT purchasesdet__pkey PRIMARY KEY(branch_id, doctype_id, id, linenum);''')
        self.execute_sql('''ALTER TABLE params ADD COLUMN extendedtables smallint;''')
        self.execute_sql('''ALTER TABLE params ALTER COLUMN extendedtables SET DEFAULT 0;''')
        self.execute_sql('''UPDATE params SET extendedtables=0 WHERE extendedtables IS NULL;''')
        self.execute_sql('''ALTER TABLE operator DROP COLUMN ctnumerorefeicoes;''')
        # self.execute_sql('''UPDATE mov_ SET rec_series_id=48 WHERE rec_series_id IS NULL;''')
        self.execute_sql('''update articles set saft_product_type=\'S\';''')
        # 18.5.2019
        # self.execute_sql('''UPDATE mov_ SET rec_series_id=48 WHERE rec_series_id IS NULL;''')
        # self.execute_sql('''UPDATE mov_ SET rec_id=0 WHERE rec_id IS NULL;''')
        self.execute_sql('''UPDATE params SET dbversion='201820'; ''')
        self.execute_sql('ALTER TABLE saft_config DROP COLUMN reports_to,DROP COLUMN log, DROP COLUMN reports, DROP COLUMN ftp, DROP COLUMN saft_enable;')

    def update_202010(self):
        gl.version = '20.1.0'
        self.execute_sql('''CREATE TABLE tax_exemption(id integer NOT NULL,short_description character varying(3),description character varying(100),CONSTRAINT tax_exemption_pkey PRIMARY KEY (id)) WITH (OIDS=FALSE);''')
        self.execute_sql('''ALTER TABLE tax_exemption OWNER TO insoft;''')
        self.execute_sql('''INSERT INTO tax_exemption VALUES (0, 'M00', 'Indefinido');''')
        self.execute_sql('''INSERT INTO tax_exemption VALUES (1, 'M01', 'Artigo 16. n. 6 alinea c) do CIVA');''')
        self.execute_sql('''INSERT INTO tax_exemption VALUES (2, 'M02', 'Artigo 6. do Decreto-Lei n. 198/90, de 19 de junho');''')
        self.execute_sql('''INSERT INTO tax_exemption VALUES (3, 'M03', 'Exigibilidade de caixa');''')
        self.execute_sql('''INSERT INTO tax_exemption VALUES (4, 'M04', 'Isento Artigo 13. do CIVA');''')
        self.execute_sql('''INSERT INTO tax_exemption VALUES (5, 'M05', 'Isento Artigo 14. do CIVA');''')
        self.execute_sql('''INSERT INTO tax_exemption VALUES (6, 'M06', 'Isento Artigo 15. do CIVA');''')
        self.execute_sql('''INSERT INTO tax_exemption VALUES (7, 'M07', 'Isento Artigo 9. do CIVA');''')
        self.execute_sql('''INSERT INTO tax_exemption VALUES (8, 'M08', 'IVA - autoliquidação');''')
        self.execute_sql('''INSERT INTO tax_exemption VALUES (9, 'M09', 'IVA - não confere direito a dedução');''')
        self.execute_sql('''INSERT INTO tax_exemption VALUES (10, 'M10', 'IVA - Regime de isenção');''')
        self.execute_sql('''INSERT INTO tax_exemption VALUES (11, 'M11', 'Regime particular do tabaco');''')
        self.execute_sql('''INSERT INTO tax_exemption VALUES (12, 'M12', 'Regime da margem de lucro-Agências de viagens');''')
        self.execute_sql('''INSERT INTO tax_exemption VALUES (13, 'M13', 'Regime da margem de lucro-Bens em segunda mão');''')
        self.execute_sql('''INSERT INTO tax_exemption VALUES (14, 'M14', 'Regime da margem de lucro-Objetos de arte');''')
        self.execute_sql('''INSERT INTO tax_exemption VALUES (15, 'M15', 'Regime da margem de lucro-Objetos de coleção e antiguidades');''')
        self.execute_sql('''INSERT INTO tax_exemption VALUES (16, 'M16', 'Isento Artigo 14. do RITI');''')
        self.execute_sql('''INSERT INTO tax_exemption VALUES (99, 'M99', 'Não sujeito; não tributado');''')
        self.execute_sql('''ALTER TABLE articles ADD COLUMN tax_exemption_id integer;''')
        self.execute_sql('''ALTER TABLE articles ALTER COLUMN tax_exemption_id SET DEFAULT 0;''')
        self.execute_sql('''UPDATE articles SET tax_exemption_id=0 WHERE tax_exemption_id IS NULL;''')
        self.execute_sql('''update params set dbversion = '202010';''')
    
    def update_202020(self):
        gl.version = '20.2.0'
        self.execute_sql('''UPDATE clients SET name='' WHERE name IS NULL;''')
        self.execute_sql('''UPDATE clients SET address='' WHERE address IS NULL;''')
        self.execute_sql('''UPDATE clients SET postal_code_3='' WHERE postal_code_3 IS NULL;''')
        self.execute_sql('''UPDATE clients SET phone='' WHERE phone IS NULL;''')
        self.execute_sql('''UPDATE clients SET email='' WHERE email IS NULL;''')
        self.execute_sql('''ALTER TABLE operator ADD COLUMN self_consumption smallint;''')
        self.execute_sql('''ALTER TABLE operator ALTER COLUMN self_consumption SET DEFAULT 0;''')
        self.execute_sql('''UPDATE operator SET self_consumption=0 WHERE self_consumption IS NULL;''')
        self.execute_sql('''update params set dbversion = '202020';''')
        
        

    def update_bin(self):
        if os.path.exists('c:\\tmp\\bin\\'):
            pass
        else:
            if not os.path.exists('c:\\tmp\\bin\\'):
                os.makedirs('c:\\tmp\\bin\\')
        if os.path.exists('c:\\tmp\\bin\\'):
            gl.sources = 'c:\\tmp\\bin\\'
        else:
            gl.sources = 'c:\\tmp\\'
        # if stdio.internet_on():
        if not self.ftp_download():
            # houve um erro no ftp e abortou
            return False
        
        if  not gl.update_settings['unlock']:
            today = datetime.date.today()
            lock = today + datetime.timedelta(days=36)
            toto = last_monday(lock)
            libpg.execute_query("UPDATE params set validuntil = %s", (toto,))
            gl.lock_date = toto.strftime("%d %b %Y")
        if stdio.file_ok(gl.sources + 'pos.exe'):
            nome = 'insoft_' + datetime.date.today().strftime('%Y%m%d') + '_' + datetime.datetime.now().time().strftime('%H%M')
            self.PRINT('Copia binários.')
            self.cp(gl.sources + 'manback.exe', 'c:\\insoft\\manback.exe')
            self.cp(gl.sources + 'pos.exe', 'c:\\insoft\\pos.exe')
            self.cp(gl.sources + 'posback.exe', 'c:\\insoft\\posback.exe')
            self.cp(gl.sources + 'lprinter.exe', 'c:\\insoft\\lprinter.exe')
            self.cp(gl.sources + 'checklic.exe', 'c:\\insoft\\checklic.exe')
            self.cp(gl.sources + 'mansaft.exe', 'c:\\insoft\\mansaft.exe')
            self.cp(gl.sources + 'pos_800.exe', 'c:\\insoft\\pos_800.exe')
            self.cp(gl.sources + 'rprinter.exe', 'c:\\insoft\\rprinter.exe')
            self.cp(gl.sources + 'plugins.ini', 'c:\\insoft\\plugins.ini')
            if stdio.file_ok('c:\\insoft\\iwsmb.exe'):
                self.cp(gl.sources + 'iwsmb.exe', 'c:\\insoft\\iwsmb.exe')
                self.cp(gl.sources + 'inbck.exe', 'c:\\insoft\\inbck.exe')
            if stdio.file_ok('c:\\insoft\\iwsbk.exe'):
                self.cp(gl.sources + 'inbck.exe', 'c:\\insoft\\inbck.exe')
                stdio.delete_file('c:\\insoft\\iwsbk.exe')
    
            if stdio.file_ok('c:\\insoft\\incd.ini'):
                self.cp(gl.sources + 'incd.exe', 'c:\\insoft\\incd.exe')
    
            # coloca o exe na resolução certa
            if gl.dos == True:
                if GetSystemMetrics(0) == 800:
                    self.PRINT('Resolução de 800x600 (Toshiba)')
                    self.cp(gl.sources + 'pos_800.exe', 'c:\\insoft\\pos.exe')
    
            self.cp(gl.sources + 'boot.exe', 'c:\\insoft\\boot.exe')
            self.PRINT('Reconstroi ficheiros INI...')
            rebuild.read_posback_ini()
            rebuild.read_pos_ini()
            rebuild.update_rprinter_ini()
            rebuild.update_tablets_ini()
            rebuild.read_manback_ini('c:\\insoft\\manback.ini')
            self.PRINT('Ficheiros INI reconstruidos!')
            '''actualiza os ficheiros da impressoras remotas '''
            self.imp_dir = []
            root_dir = 'c:\\insoft\\impressoras\\'
            if os.path.exists(root_dir):
                self.PRINT('Actualiza impressoras remotas')
                dum = [name for name in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, name))]
                for f in dum:
                    self.imp_dir.append(root_dir + f)
                for n in self.imp_dir:
                    shutil.copyfile(gl.sources + 'rprinter.exe', n + '\\rprinter.exe')
            ''' update_tablets: 12.SET.2016 '''
            root_dir = 'c:\\insoft\\'
            self.PRINT('Actualiza tablets')
            dir_list = [name for name in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, name))]
            self.tab_dir = []
            for n in dir_list:
                if n.find('tab') > -1:
                    # print n,a
                    self.tab_dir.append(root_dir + '\\' + n)
                elif n.find('pda') > -1:
                    self.tab_dir.append(root_dir + '\\' + n)
            for n in self.tab_dir:
                shutil.copyfile(gl.sources + 'pos.exe', n + '\\pos.exe')
                shutil.copyfile(gl.sources + 'lprinter.exe', n + '\\lprinter.exe')
                shutil.copyfile(gl.sources + 'boot.exe', n + '\\boot.exe')
            # self.PRINT('Limpa ficheiros de licenciamento.')
            # coloca os ficheiros de licenciamento nos devidos lugares
            # stdio.delete_files('c:\\insoft\\', mask='.lic')
    
            self.PRINT('Copia ficheiros de licenciamento.')
            if self.update_lic():
                self.PRINT('Limpa ficheiro obsoletos.')
                clean_old_files()
                self.PRINT('Actualização dos binarios terminada.')
            else:
                return False
        else:
            self.PRINT('<font color="red">Não foi efectuada a cópia dos binarios</font>')
        return True
    
    
    def patch_201310530(self):
        sql = 'select options_submenu_3, id from operator;'
        for n in self.output_query_many(sql, (True,)):
            toto = len(n[0].strip())
            if toto < 5:
                self.execute_sql(
                    'UPDATE operator SET options_submenu_3=options_submenu_3 || \'0\' where id = ' + str(n[1]) + ';')
    
    def update_options_submenu(self):
        if self.output_query_one('SELECT length(options_submenu_8) FROM operator limit 1', (True,))[0] < 4:
            self.execute_query('UPDATE operator SET options_submenu_8=options_submenu_8 || \'1\'', (True,))
            self.execute_query('UPDATE operator SET options_submenu_8=\'0000\' WHERE id=0', (True,))
            self.execute_query('UPDATE operator SET options_submenu_8=\'0000\' WHERE id=99999', (True,))
            # stdio.log_write('update.log', 'update operator #8: ')
        if self.output_query_one('SELECT length(options_submenu_5) FROM operator limit 1', (True,))[0] < 5:
            self.execute_query('UPDATE operator SET options_submenu_5=options_submenu_5 || \'000\'', (True,))
            self.execute_query('UPDATE operator SET options_submenu_5=\'00000\' WHERE id=0', (True,))
            self.execute_query('UPDATE operator SET options_submenu_5=\'00000\' WHERE id=99999', (True,))
            # stdio.log_write('update.log', 'update operator #8: ')
    
    def cp(self, source, target, echo=False):
        try:
            shutil.copy2(source, target)
            if echo:
                self.PRINT('{:<20}'.format(source[source.rfind('\\') + 1:]) + ' O.K.')
        except Exception:
            if echo:
                self.PRINT(source[source.rfind('\\') + 1:] + '<font color="red"> File not found:</font>')
    
    def alter_table(self, t, c, data_type, default, v, char_size=10):
        if not validate_field(t, c):
            if data_type.find('varchar') > -1:
                self.execute_query('ALTER TABLE ' + t + ' ADD COLUMN ' + c + ' ' + data_type, (True,))
            elif data_type.find('char') > -1:
                self.execute_query(
                    'ALTER TABLE ' + t + ' ADD COLUMN ' + c + ' ' + data_type + '(' + str(char_size) + ')', (True,))
            elif data_type.find('timestamp') > -1:
                self.execute_query('ALTER TABLE ' + t + ' ADD COLUMN ' + c + ' ' + data_type, (True,))
            else:  # cria ints e outras coisas parecidas
                self.execute_query('ALTER TABLE ' + t + ' ADD COLUMN ' + c + ' ' + data_type, (True,))
            if data_type.find('varchar') > -1:
                self.execute_query('ALTER TABLE ' + t + ' ALTER COLUMN ' + c + ' SET STORAGE EXTENDED;', (True,))
            elif data_type == 'text':
                self.execute_query('ALTER TABLE ' + t + ' ALTER COLUMN ' + c + ' SET STORAGE EXTENDED;', (True,))
            elif data_type == 'int2' or data_type == 'int4':
                self.execute_query('ALTER TABLE ' + t + ' ALTER COLUMN ' + c + ' SET STORAGE PLAIN;', (True,))
            elif data_type == 'numeric':
                self.execute_query('ALTER TABLE ' + t + ' ALTER COLUMN ' + c + ' SET STORAGE MAIN;', (True,))
            elif data_type == 'timestamp':
                pass
            if default != '':
                self.execute_query('ALTER TABLE ' + t + ' ALTER COLUMN ' + c + ' SET DEFAULT %s', (default,))
            if data_type == 'timestamp':
                pass
            else:
                self.execute_query('UPDATE ' + t + ' SET ' + c + '=%s', (v,))
            # stdio.log_write('update.log', 'alter table: ' + t + '/' + c)
        else:
            pass
            # stdio.log_write('update.log', 'exist: ' + t + '/' + c)
    
    def output_query_one(self, sql, data):
        try:
            conn = psycopg2.connect(gl.c)
            cur = conn.cursor()
            conn.set_client_encoding('UTF8')
            cur.execute(sql, data)
            return cur.fetchone()
        
        except Exception as e:
            stdio.log_write('error.log', 'output_query_one\n' + str(e) + '\n -- SQL Error --\n in :' + '\n' + sql)
            self.PRINT("{0:>6}".format(gl.version) + ':<font color="red"> Erro SQL @ ' + sql[:60] + '</font>')
    
    def output_query_many(self, sql, data):
        try:
            conn = psycopg2.connect(gl.c)
            cur = conn.cursor()
            conn.set_client_encoding('UTF8')
            cur.execute(sql, data)
            return cur.fetchall()
        except Exception as e:
            stdio.log_write('error.log', 'output_query_many\n' + str(e) + '\n -- SQL Error --\n in :' + '\n' + sql)
            self.PRINT("{0:>6}".format(gl.version) + ':<font color="red"> Erro SQL @ ' + sql[:60] + '</font>')
    
    def execute_query(self, sql, data):
        try:
            conn = psycopg2.connect(gl.c)
            cur = conn.cursor()
            conn.set_client_encoding('UTF8')
            cur.execute(sql, data)
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            # stdio.log_write('update.log', 'execute_query\n' + str(e) + '\n -- SQL run Error --\n ' + sql)
            self.PRINT("{0:>6}".format(gl.version) + ':<font color="red"> Erro SQL @ ' + sql[:60] + '</font>')
    
    def execute_sql(self, sql):
        try:
            conn = psycopg2.connect(gl.c)
            cur = conn.cursor()
            conn.set_client_encoding('UTF8')
            cur.execute(sql, (True,))
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            # stdio.log_write('update.log', 'execute_sql\n' + str(e) + '\n -- SQL run Error --\n ' + sql)
            try:
                self.PRINT("{0:>6}".format(gl.version) + ':<font color="red"> Erro SQL @ ' + sql[:65] + '</font>')
            except UnicodeDecodeError:
                self.PRINT('Unicode error ... continue.')
                pass
    def dropColumn(self, table, column):
        if validate_field(table, column):
            self.execute_sql('''ALTER TABLE articles DROP COLUMN families_types_id''')
    
    def createIndex_rtables_mov_idx_contents_msg(self):
        toto = self.output_query_one('SELECT attname FROM pg_attribute WHERE attrelid =(SELECT oid FROM pg_class \
                WHERE relname = \'rtables_mov_idx_contents_msg\')', (True,)).output
        if toto == -1:
            sql = 'CREATE INDEX rtables_mov_idx_contents_msg ON rtables_mov USING btree (contents_msg)'
            self.execute_sql(sql)
        else:
            pass
    
    def createTable_rtables_cards(self):
        if not self.validate_field('rtables_cards', 'id'):
            sql = 'CREATE TABLE rtables_cards (id int4 NOT NULL DEFAULT 0,\
                  description varchar, min_value numeric DEFAULT 0,\
                  max_value numeric DEFAULT 0,dsc_value numeric DEFAULT 0,\
                  active int2 DEFAULT 0,\
                  CONSTRAINT rtables_cards_pkey PRIMARY KEY (id))WITHOUT OIDS'
            self.execute_sql(sql)
            # stdio.log_write('update.log', 'create table rtables_cards')
            self.execute_sql('ALTER TABLE rtables_cards OWNER TO insoft')
            # stdio.log_write('update.log', 'alter table owner to insoft')
    
    def createTable_extras_articles(self):
        sql = 'CREATE TABLE extras_articles (master_articles_id int4 NOT NULL DEFAULT 0,\
      extra_articles_id int4 NOT NULL DEFAULT 0,no_price int2 DEFAULT 0,\
      CONSTRAINT extras_articles_pkey PRIMARY KEY (master_articles_id, extra_articles_id))WITHOUT OIDS;'
        self.executeQuery(sql, (True,))
        self.executeQuery('ALTER TABLE extras_articles OWNER TO restware;', (True,))
    
    def createTable_rtables_autoload_formula(self):
        self.execute_sql('CREATE TABLE rtables_autoload_formula (sectors_id int4 NOT NULL,numberofcustomers int2 NOT NULL,\
               quantity int2 NOT NULL DEFAULT 1, CONSTRAINT rtables_autoload_formula_pkey PRIMARY KEY (sectors_id, numberofcustomers)) WITHOUT OIDS;')
        # stdio.log_write('update.log', 'create table: rtables_autoload_formula')
        self.execute_sql('ALTER TABLE rtables_autoload_formula OWNER TO restware;')
        # stdio.log_write('update.log', 'alter table:')
    
    def createTable_movcaixa_types(self):
        self.execute_sql('CREATE TABLE movcaixa_types(id int4 NOT NULL DEFAULT 0,description varchar(30),\
      CONSTRAINT movcaixa_types_pkey PRIMARY KEY (id))WITHOUT OIDS;')
        self.execute_sql('ALTER TABLE movcaixa_types OWNER TO restware;')
    
    def insertRecord(self, table, field, record_id, sql):
        toto = self.output_query_one('select ' + field + ' from ' + table + ' where ' + field + ' =%s ',
                                     (record_id,)).output
        if toto == -1:
            self.execute_sql(sql)
            # stdio.log_write('update.log', 'record exits ' + table + ' ' + field + ' ' + str(record_id) + ' updated!')
        else:
            pass
            # stdio.log_write('update.log',
                            # 'record exits ' + table + ' ' + field + ' ' + str(record_id) + ' not updated!')
    
    def send_report(self):
        report = []
        report.append('         Actualização de Software        ')
        report.append('Dados do cliente')
        report.append(gl.saftname)
        report.append(gl.commercial_name)
        report.append(gl.saftnif)
        report.append(gl.saftaddress)
        report.append(gl.saftpostalcode)
        report.append(gl.saftcity)
        report.append('<b>Versão Postgresql:</b>' + gl.pg_version)
        report.append('<b>Data do servidor:</b>' + gl.pg_date)
        report.append('<b>Server Uptime:</b>' + gl.pos_ini['server uptime'])
        report.append('<b>Arranque do PSQL:</b>' + gl.pos_ini['server start'])
        # report.append('<b>Tamanho da DB:</b>' + gl.pos_ini['file size'])
        report.append('')
        report.extend(gl.bin_report)
        report.append('    Software Actualizado da versão ' + gl.init_version)
        report.append('Actualizado para a versão ' + gl.dbversion)  # gl.version)
        report.append('Posto: ' + gl.pos_ini['posid'])
        report.append('')
        report.append('')
        report.append('')
        report.append('O Cliente')
        report.append('____________________________________________')
        report.append('')
        report.append('O Técnico')
        report.append('____________________________________________')
        report.append('')
        NEW = chr(27)
        LF = chr(10)
        toto = ''
        for n in report:
            toto += NEW + n + LF
        if gl.update_settings['print']:
            print_report(toto, 1)
        if gl.update_settings['mail']:
            stdio.get_server_data() # pergunta as configurações
            if gl.server_data['server']:
                gl.pos_ini['posid'] = 'Servidor'
            report_html = html_lib.update_to_html()
            # envia o relatorio por mail
            self.PRINT('<font color="#85C3FE">Internet OK')
            self.PRINT('<font color="#85C3FE">Enviando e-mail')
            time.sleep(0.10)
            if gl.update_settings['server']:
                msg_dic = {'sub': 'UPDATE Servidor ' + 'de ' + gl.saftname + ' para ' + gl.version,'body': report_html}
            else:
                msg_dic = {'sub': 'UPDATE posto ' + str(gl.pos_ini['posid']) + ' de ' + gl.saftname + ' para ' + gl.version, 'body': report_html}
            # para onde enviar o mail
            stdio.send_mail_html(['assistencias@espiridiao.net'], msg_dic)
        else:
            self.PRINT('<font color="#85C3FE">não envia e-mail')
    
    def get_db_version(self):
        if validate_field('params', 'dbversion'):
            sql = 'SELECT dbversion FROM params'
            a = libpg.query_one(sql)
            gl.dbversion = a[0]
            if validate_field('params', 'release'):
                c = libpg.query_one('SELECT release from params')
                gl.dbversion += str(c[0])
            return a[0]
        else:
            gl.dbversion = 2011
            print 'get_db_version'
            sys.exit(32)

    def check_alive(self):
        try:
            conn = psycopg2.connect(gl.c)
            cur = conn.cursor()
            conn.set_client_encoding('UTF8')
            cur.execute('Select * from articles')
            self.BUTTON_STATUS = True,'Actulizar'
            return True
    
        except Exception as e:
            # stdio.log_write('update.log', str(e))
            if str(e).find('not connect') > -1:
                gl.error = 'Não consegui ligar ao servidor\n ' + gl.pos_ini['host']
            else:
                gl.error = 'Erro desconhecido:\n' + str(e)
                self.BUTTON_STATUS = False, 'Erro Grave'
            return False

def clean_old_files():
    stdio.delete_file('c:\\insoft\\artigos.exe')
    stdio.delete_file('c:\\insoft\\iwsbk.exe')
    stdio.delete_file('c:\\insoft\\iwsagt.exe')
    stdio.delete_file('c:\\insoft\\posd.exe')
    stdio.delete_file('c:\\insoft\\bootstrap.exe')
    stdio.delete_file('c:\\insoft\\setup.exe')
    stdio.delete_file('c:\\insoft\\dbupdate.exe')
    stdio.delete_file('c:\\insoft\\pos_old.ini')
    stdio.delete_file('c:\\insoft\\pos_matrix.ini')
    stdio.delete_file('c:\\insoft\\pos_1024.exe')
    stdio.delete_file('c:\\insoft\\pos_800.exe')
    stdio.delete_file('c:\\insoft\\rdispatcher.exe')
    stdio.delete_file('c:\\insoft\\rprinter.exe')
    stdio.delete_file('c:\\insoft\\rprinter.ini')
    stdio.delete_file('c:\\insoft\\rmonitor.ini')
    stdio.delete_file('c:\\insoft\\rmonitor.exe')
    stdio.delete_file('c:\\insoft\\expm.exe')
    stdio.delete_file('c:\\insoft\\pupdate.exe')
    stdio.delete_file('c:\\insoft\\manrest.exe')
    stdio.delete_file('c:\\insoft\\pgconfig.exe')
    if not stdio.file_ok('c:\\insoft\\incd.ini'):
        stdio.delete_file('c:\\insoft\\incd.exe')
    stdio.delete_files('c:\\insoft\\', mask='.pdf')
    stdio.delete_file(base64.b64decode('YzpcXGluc29mdFxcYXV0b2JhY2suZXhl'))
    stdio.delete_file('c:\\insoft\\SeqESC.txt')
    stdio.delete_files('c:\\insoft\\', mask='.txt')
    stdio.delete_files('c:\\insoft\\', mask='.xml')
    stdio.delete_dir('c:\\insoft\\backup')
    stdio.delete_dir('c:\\insoft\\utils')
    stdio.delete_dir('c:\\insoft\\boot')
    stdio.delete_dir('c:\\insoft\\EXIT')
    stdio.delete_dir('c:\\insoft\\UPDATE')
    stdio.delete_dir('c:\\insoft\\templates')

def update_saft_bin():
    directory = '/bin/'
    if not os.path.exists('c:\\insoft\\plugins\\'):
        os.makedirs('c:\\insoft\\plugins\\')
    if not os.path.exists('c:\\insoft\\plugins\\saft\\'):
        os.makedirs('c:\\insoft\\plugins\\saft\\')
    try:
        ftp = ftplib.FTP(gl.ftp1[2], timeout=5)
        ftp.login(gl.ftp1[0], gl.ftp1[1])
        stdio.dir_ok('c:\\tmp\\', create=True)
        ftp.cwd(directory)
        file_name = 'SAF-T.exe'
        gl.msg.append('Start Download ' + file_name)
        fhandle = open('c:\\insoft\\plugins\\saft\\' + file_name, 'wb')
        ftp.retrbinary('RETR ' + file_name, fhandle.write)
        fhandle.close()
        ftp.close()
        gl.msg.append('Finish Download ' + file_name)
        return True, 'OK'
    except Exception as err:
        return False, str(err)
    
def get_psql_version():
    a = dbmain.output_query_one('show server_version ', (True,))
    b = a[0].split('.')
    v = int(b[0] + b[1])
    if v > 92:
        return True
    else:
        return False

def validate_field(table, field):
    try:
        sql = 'SELECT ' + field + ' FROM ' + table
        conn = psycopg2.connect(gl.c)
        cur = conn.cursor()
        conn.set_client_encoding('UTF8')
        cur.execute(sql, (True,))
        output = cur.fetchone()
        if len(output) > 0:
            return True
        else:
            return False
    except Exception as e:
        return False

def last_monday(date):
    # today = datetime.date.today()
    today = date
    last_monday = today + datetime.timedelta(days=-date.weekday() + 0, weeks=0)
    return last_monday


def print_report(texto, copies=1):
    for n in range(0, copies):
        d = datetime.datetime.now()
        toto = base64.b64encode(unicode(texto, 'utf-8').encode('Latin-1'))
        sql = '''INSERT INTO
                 print_spool(printer_id,doc_id,doctype_id,doc_name,date_time_stamp,filecontents,second_print)
                 VALUES(1,0,0,%s,%s,%s,0)'''
        data = (datetime.datetime.now().strftime('%S%f.rst'),
                datetime.datetime(d.year, d.month, d.day, d.hour, d.minute, d.second), toto)
        dbmain.execute_query(sql, data)
        
        data = (1, 'F', datetime.datetime(d.year, d.month, d.day, d.hour, d.minute, d.second))
        dbmain.execute_query(base64.b64decode('SU5TRVJUIElOVE8gcHJpbnRfam9icyhwcmludGVyX2lk\
            LGpvYl90eXBlLGRhdGVfdGltZV9zdGFtcCkgVkFMVUVTICglcywlcywlcyk='), data)
    
def format_version(v):
    return v[0:4] + '.' + v[4:5] + '.' + v[5:]


def hashfile(afile, hasher, blocksize=65536):
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    return hasher.digest()


if __name__ == '__main__':
    pass
