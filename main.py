#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import datetime
import base64
import shutil
import glob
import ftplib
import re
import subprocess
import time
import calendar
from random import randrange
from PyQt4.QtCore import Qt, SIGNAL, QSize
from PyQt4.QtGui import QMainWindow, QWidget, QIcon, QHBoxLayout, QTreeWidget,QTreeWidgetItem,QVBoxLayout, QLabel,\
    QFileDialog,QMessageBox,QTableWidget,QPushButton,QComboBox,QFont,QLineEdit,QPixmap,QInputDialog,QCommandLinkButton,\
    QErrorMessage,QToolButton,QTextEdit,QCheckBox,QStandardItemModel,QApplication,QStyleFactory,QDesktopWidget

import client_browser
import doc_browser
import ftp_lic
import lics_download
import numpad
import printer_config
import printer_stress
import rebuild
import smtpmail
import to_ftp

try:
    from win32api import GetSystemMetrics
    import wmi
    import ctypes.wintypes
    import certifi.core
except ImportError:
    pass
import broadcast
import libpg
import parameters as gl
import licblock
import stdio
import get_printers
import libpgadmin
import dbbrowser
import restore_db
import ex_grid
import libsaft
import printer_spool
import updater
import ui
import psql_check
import report_viewer
import win_interface
from qlib import make_button


class MainWindow(QMainWindow):
    def __init__(self,  parent = None):
        super(MainWindow,  self).__init__(parent)
        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)
        if gl.dos:
            if GetSystemMetrics(0) == 800:
                self.showMaximized()
            else:
                self.resize(800, 600)
        else:
            self.resize(800, 600)
        self.center()
        self.setWindowIcon(QIcon('appimg.png'))
        self.statusBarMain = self.statusBar()
        gl.wc = 0
        gl.msg_c = 0
        self.IS_ALIVE = False
        self.att_files = []
        self.setWindowTitle('C.T.R.L.')
        if stdio.file_ok('tech.exe.log'): os.remove('tech.exe.log')       
        if self.te_click():
            self.mainLayout = QHBoxLayout(self.centralwidget)
            flag = stdio.check_ini()
            if flag:
                libpg.make_default(0)
                self.IS_ALIVE = psql_check.check_alive()
                if self.IS_ALIVE:
                    psql_check.init_table()
                    psql_check.get_saft_data()
                else:
                    bc = '''<!DOCTYPE html><html lang="pt_pt"><head><meta charset="utf-8">
                                  </head><img src="./upss.png" <br><br><font size="5" face="verdana" color="red"><strong>
                                      Sem servidor!</font></html>'''
                    form = report_viewer.BrowserView('Mensagem de erro', bc)
                    form.exec_()
            else:
                bc = '''<!DOCTYPE html><html lang="pt_pt"><head><meta charset="utf-8">
                              </head><img src="./upss.png" <br><br><font size="5" face="verdana" color="red"><strong>
                                  Sem pos.ini ou posback.ini!</font></html>'''
                form = report_viewer.BrowserView('Mensagem de erro', bc)
                form.exec_()
            self.make_user_layout()
        else:
            sys.exit(100)
        self.statusBarMain.showMessage('OK')
    
    def te_click(self):
        if gl.SUPER:
            gl.wc = -1
        else:
            form = ui.UI()
            form.exec_()
        if gl.wc == -1:
            return True
        else:
            return False
    
    def make_user_layout(self):
        pointListBox = QTreeWidget()
        pointListBox.setMinimumWidth(250)
        pointListBox.setMaximumWidth(250)
        pointListBox.setHeaderHidden(True)
        root = QTreeWidgetItem(pointListBox, ["Insoft Centre [" + gl.VERSION + "]"])
        Update = QTreeWidgetItem(root, ["Actualiza"])
        Update.setIcon(0,QIcon('update.png'))
        Lic = QTreeWidgetItem(root, [u"Licenças"])
        Lic.setIcon(0,QIcon('key.png'))
        Download = QTreeWidgetItem(root, ["Downloads"])
        Download.setIcon(0,QIcon('download.png'))
        Binaries = QTreeWidgetItem(root, ["Executaveis"])
        Binaries.setIcon(0,QIcon('binary.png'))
        Saft = QTreeWidgetItem(root, ["SAF-t"])
        Saft.setIcon(0,QIcon('saft.png'))
        Backups = QTreeWidgetItem(root, ["Backup & Restore"])
        Backups.setIcon(0,QIcon('backup-green.png'))
        Email = QTreeWidgetItem(root, ["E-mail"])
        Email.setIcon(0,QIcon('email.png'))
        Printers = QTreeWidgetItem(root, ["Impressoras"])
        Printers.setIcon(0,QIcon('printers.png'))
        PostgreSQL = QTreeWidgetItem(root, ["PostgreSQL"])
        PostgreSQL.setIcon(0,QIcon('psql.png'))
        Switch = QTreeWidgetItem(root, ["Switches"])
        Switch.setIcon(0,QIcon('switch.png'))
        Drivers = QTreeWidgetItem(root, ["Drivers"])
        Drivers.setIcon(0,QIcon('drivers.png'))
        Info = QTreeWidgetItem(root, ["Info"])
        Info.setIcon(0,QIcon('all_info.png'))
        Backoffice = QTreeWidgetItem(root,['BO'])
        Backoffice.setIcon(0, QIcon('backoffice.png'))
        
        Settings = QTreeWidgetItem(root, [u"Configuração"])
        Settings.setIcon(0, QIcon('config.png'))
        
        windows_cp = QTreeWidgetItem(root, ["Atalhos"])
        windows_cp.setIcon(0,QIcon('win10.png'))
        
        system_cp = QTreeWidgetItem(root, ["Sistema"])
        system_cp.setIcon(0, QIcon('bee.png'))
        pointListBox.itemClicked.connect(self.grid_click)
        
        self.mainLayout.addWidget(pointListBox)
        self.outputLayout = QVBoxLayout()
        self.garb = QLabel('')
        self.garb.setMinimumWidth(550)
        self.garb.setMaximumWidth(550)
        self.garb.setPixmap(QPixmap('galaxian.png'))
        self.garb.setAlignment(Qt.AlignCenter)
        pointListBox.setStyleSheet("background-color: white;background-image: url(./image.png); "
                                   "background-repeat: no-repeat; background-attachment: fixed;background-position: center; ")
        
        self.outputLayout.addWidget(self.garb)
        self.mainLayout.addLayout(self.outputLayout)
        pointListBox.setIconSize(QSize(32, 32))
        pointListBox.expandToDepth(0)
    
    
    def grid_click(self, a, b):
        i = a.text(b)[:3]
        if i =='Imp':
            self.make_printers(i)
        elif i =='Lic':
            self.make_licence(i)
        elif i == 'Swi':
            self.make_switches(i)
        elif i == 'Bac':
            self.make_backup(i)
        elif i == 'Pos':
            self.make_postgres_tools(i)
        elif i == 'Dow':
            self.make_downloads(i)
        elif i == 'Exe':
            self.binaries_download(i)
        elif i == 'Con':
            self.make_config(i)
        elif i == 'SAF':
            self.make_saft(i)
        elif i == 'Inf':
            self.make_info(i)
        elif i == 'BO':
            self.make_backoffice()
        elif i == 'Act':
            self.update_click(i)
        elif i == 'Dri':
            self.download_drivers(i)
        elif i == 'Ata':
            self.windows_cpanel(i)
        elif i == 'Sis':
            self.sistem_panel(i)
        elif i == 'E-m':
            self.send_email(i)
    
    def make_printers(self, tx):
        self.clear_layout()
        self.garb.setText(tx)
        self.outputLayout.addWidget(self.garb)
    
        limpa_spoolBtn = make_button('Limpa Spool','bin.png')
        self.connect(limpa_spoolBtn, SIGNAL("clicked()"), self.clean_spool)
        self.outputLayout.addWidget(limpa_spoolBtn)
    
        testPrinterBtn = make_button('Teste de Impressoras','test_printers.png')
        self.connect(testPrinterBtn, SIGNAL("clicked()"), self.printer_test_click)
        self.outputLayout.addWidget(testPrinterBtn)
        brodcast_btn = make_button('Mensagem pelas Impressoras',"messages_printer.png")
        self.connect(brodcast_btn, SIGNAL("clicked()"), self.brodcast_click)
        self.outputLayout.addWidget(brodcast_btn)
    
        view_spool_btn = make_button('Ver Spool','spool.png')
        self.connect(view_spool_btn, SIGNAL("clicked()"), self.spool_view)
        self.outputLayout.addWidget(view_spool_btn)
        printerStressBtn = make_button('Stress Teste',"stress.png")
        self.connect(printerStressBtn, SIGNAL("clicked()"), self.stress_test_click)
        self.outputLayout.addWidget(printerStressBtn)
        qcrCodeBtn = make_button('Configura QR code',"qr_code.png")
        self.connect(qcrCodeBtn, SIGNAL("clicked()"), self.qrcode_config_click)
        self.outputLayout.addWidget(qcrCodeBtn)
    
    
        self.outputLayout.addStretch()
    
    def clear_layout(self):
        for i in reversed(list(range(self.outputLayout.count()))):
            if self.outputLayout.itemAt(i).widget() is None:
                pass
            else:
                self.outputLayout.itemAt(i).widget().deleteLater()
        self.outputLayout = QVBoxLayout()
        self.garb = QLabel()
        self.garb.setMinimumWidth(550)
        self.garb.setMaximumWidth(550)
        self.mainLayout.addLayout(self.outputLayout)
        self.mainLayout.addStretch()
    
    def show_msg_click(self):
        pass
    
    def make_licence(self, tx):
        self.clear_layout()
        self.garb.setText(tx)
        self.outputLayout.addWidget(self.garb)
        validaBtn = make_button(u"Valida",'money.png')
        self.connect(validaBtn, SIGNAL("clicked()"), self.software_lock)
        self.outputLayout.addWidget(validaBtn)
        view_licBtn = make_button(u"Ver licenças",'lic_view.png')
        self.connect(view_licBtn, SIGNAL("clicked()"), self.view_lic_click)
        self.outputLayout.addWidget(view_licBtn)
        
        down_licBtn = make_button(u"Download de UMA licença",'lic_down1.png')
        self.connect(down_licBtn, SIGNAL("clicked()"), self.lic_download1)
        self.outputLayout.addWidget(down_licBtn)
        replacUnlockLicBtn = make_button(u'Substitui Licenças e Destranca', 'unlock_lic.png')
        self.connect(replacUnlockLicBtn, SIGNAL("clicked()"), self.replace_lic_files_unlock)
        self.outputLayout.addWidget(replacUnlockLicBtn)
        replaceLicBtn = make_button(u'Substitui Licenças', 'replace_lic.png')
        self.connect(replaceLicBtn, SIGNAL("clicked()"), self.replace_lic_files)
        self.outputLayout.addWidget(replaceLicBtn)
        unlock_btn = make_button('Unlock','unlock_db.png')
        self.connect(unlock_btn, SIGNAL("clicked()"), self.unlock_click)
        self.outputLayout.addWidget(unlock_btn)
        showOneBtn = make_button(u"Espreitar licença.",'owl.png')
        self.connect(showOneBtn, SIGNAL("clicked()"), self.show_one_lic)
        self.outputLayout.addWidget(showOneBtn)
        self.outputLayout.addStretch()
    
    def show_one_lic(self):
        dir_target = QFileDialog.getExistingDirectory(self, 'Escolhe a Pasta', 'c:\\insoft\\')
        if dir_target.isEmpty():
            pass
        else:
            if stdio.file_ok(dir_target + '\\checklic.exe'):
                dir_target = str(dir_target)
                fl = glob.glob(dir_target + '\\*.lic')
                lics_txt = ''
                for n in fl:
                    if stdio.run_silent(dir_target + '\\checklic.exe ' + n.replace('\\', os.sep)):
                        a = stdio.config_to_text(n + '.txt')[1]
                        lics_txt += '{:^80}'.format(n)
                        lics_txt += '-' * 80
                        lics_txt += a
                form = report_viewer.PlainText(u'Licenças', lics_txt)
                form.exec_()
            else:
                void = QMessageBox.warning(None, self.trUtf8("Erro"),
                                           self.trUtf8('Não foi encontrado o checklic.exe'))
    
    
    
    def make_switches(self, tx):
        self.clear_layout()
        # self.garb.setText(tx)
        self.outputLayout.addWidget(self.garb)
        forceNifInputBtn = make_button('Altera NIF','nif.png')
        self.connect(forceNifInputBtn, SIGNAL("clicked()"), self.force_nif_change)
        self.outputLayout.addWidget(forceNifInputBtn)
        
        kill_all = make_button('Mata TODOS os processos do Restware','kill_all.png')
        self.connect(kill_all, SIGNAL("clicked()"), self.kill_all_iws_click)
        self.outputLayout.addWidget(kill_all)
        biocapture = make_button('Activa Biometria','bio_enable.png')
        self.connect(biocapture, SIGNAL("clicked()"), self.biocapture_switch)
        self.outputLayout.addWidget(biocapture)
        safArticleTypeBtn = make_button(u'Preenche Classificação Fiscal', 'fill_tax.png')
        self.connect(safArticleTypeBtn, SIGNAL("clicked()"), self.saft_article_type_fix)
        self.outputLayout.addWidget(safArticleTypeBtn)
        self.outputLayout.addStretch()
    
    
    def windows_cpanel(self, tx):
        self.clear_layout()
        self.garb.setText(tx)
        self.outputLayout.addWidget(self.garb)
        
        call_services = make_button(u'Serviços','backup.png')
        self.outputLayout.addWidget(call_services)
        self.connect(call_services, SIGNAL("clicked()"), self.call_services_click)
        call_taskmgr = make_button(u'Gestor de Tarefas','taskmgr.png')
        self.outputLayout.addWidget(call_taskmgr)
        self.connect(call_taskmgr, SIGNAL("clicked()"), self.call_taskmgr_click)
        call_taskschd = make_button(u'Tarefas Agendadas','taskschd.png')
        self.outputLayout.addWidget(call_taskschd)
        self.connect(call_taskschd, SIGNAL("clicked()"), self.call_taskschd_click)
        call_cpanel = make_button(u'Painel de Controlo','cpanel.png')
        self.outputLayout.addWidget(call_cpanel)
        self.connect(call_cpanel, SIGNAL("clicked()"), self.call_cpanel_click)
        self.outputLayout.addStretch()
    
    def sistem_panel(self, tx):
        self.clear_layout()
        self.garb.setText(tx)
        self.outputLayout.addWidget(self.garb)
        
        mark_boot_update = make_button(u'Em actualização','update_boot.png')
        self.connect(mark_boot_update, SIGNAL("clicked()"), self.mark_boot_on_update)
        self.outputLayout.addWidget(mark_boot_update)
        mark_exit_exit = make_button(u'Sair do Boot','exit_boot.png')
        self.connect(mark_exit_exit, SIGNAL("clicked()"), self.mark_boot_exit)
        self.outputLayout.addWidget(mark_exit_exit)
        wipe_dir = make_button('Wipe Out','wipe.png')
        self.connect(wipe_dir, SIGNAL("clicked()"), self.wipe_click)
        self.outputLayout.addWidget(wipe_dir)
        boot_kill = make_button(u'Matar o Boot','kill_boot.png')
        self.connect(boot_kill, SIGNAL("clicked()"), self.boot_kill_click)
        self.outputLayout.addWidget(boot_kill)
        win_restart = make_button(u'Reiniciar o Windows','windows_restart.png')
        self.connect(win_restart, SIGNAL("clicked()"), self.windows_restart_click)
        self.outputLayout.addWidget(win_restart)
        ctrl_close = make_button(u'Fechar o ctrl','exit.png')
        self.connect(ctrl_close, SIGNAL("clicked()"), self.ctrl_close_click)
        self.outputLayout.addWidget(ctrl_close)
        self.outputLayout.addStretch()
    
    def mark_boot_exit(self):
        stdio.delete_dir('c:\\insoft\\UPDATE')
        stdio.dir_ok('c:\\insoft\\EXIT')
    
    def mark_boot_on_update(self):
        stdio.delete_dir('c:\\insoft\\EXIT')
        stdio.dir_ok('c:\\insoft\\UPDATE')
    
    def boot_kill_click(self):
        win_interface.kill_boot()
    
    def ctrl_close_click(self):
        self.close()
    
    def windows_restart_click(self):
        os.system('shutdown /t 0 /r /f ')
    
    def call_services_click(self):
        run_silent('services.msc')
    
    
    def call_taskmgr_click(self):
        run_silent('taskmgr')
    
    def call_cpanel_click(self):
        run_silent('control panel')
    
    def call_taskschd_click(self):
        run_silent('taskschd.msc')
    
    def make_backup(self, tx):
        self.clear_layout()
        self.garb.setText(tx)
        self.outputLayout.addWidget(self.garb)
        
        restore_btn = make_button('Restore','restore.png')
        self.connect(restore_btn, SIGNAL("clicked()"), self.restore_backup_click)
        self.outputLayout.addWidget(restore_btn)

        backupTestBtn = make_button('Faz Backup','test_backup.png')
        self.connect(backupTestBtn, SIGNAL("clicked()"), self.backup_test_click)
        self.outputLayout.addWidget(backupTestBtn)

        lastBackupBtn = make_button('Ultimo Backup','backup_last.png')
        self.connect(lastBackupBtn, SIGNAL("clicked()"), self.backup_last)
        self.outputLayout.addWidget(lastBackupBtn)
        backup_arqBtn = make_button('Envia Backup para o FTP','db2arch.png')
        self.connect(backup_arqBtn, SIGNAL("clicked()"), self.backup_archive_click)
        self.outputLayout.addWidget(backup_arqBtn)
        back_c = make_button('Backup para Infornash','backup.png')
        self.connect(back_c, SIGNAL("clicked()"), self.backup_c_click)
        self.outputLayout.addWidget(back_c)
        isnapshot_Btn = make_button('Backup completo do Insoft','snapshot.png')
        self.connect(isnapshot_Btn, SIGNAL("clicked()"), self.snapshot_bins)
        self.outputLayout.addWidget(isnapshot_Btn)
        self.outputLayout.addStretch()
    
    
    def make_postgres_tools(self, tx):
        self.clear_layout()
        self.garb.setText(tx)
        self.outputLayout.addWidget(self.garb)
        
        self.stopBtn = make_button(u'Para o serviço do Postgres',"stop.png")
        self.connect(self.stopBtn, SIGNAL("clicked()"), self.stop_psql_click)
        self.outputLayout.addWidget(self.stopBtn)
        if not gl.server_status:
            self.stopBtn.setText('Servidor parado!')
        
        sqlBtn = make_button('SQL',"sql.png")
        self.connect(sqlBtn, SIGNAL("clicked()"), self.sql_browser_click)
        self.outputLayout.addWidget(sqlBtn)
        
        vacum_btn = make_button('Vaccum','cow.png')
        self.connect(vacum_btn, SIGNAL("clicked()"), self.vaccum_click)
        self.outputLayout.addWidget(vacum_btn)
        makeDbBtn = make_button('Cria Base de Dados','build.png')
        self.connect(makeDbBtn, SIGNAL("clicked()"), self.create_database)
        self.outputLayout.addWidget(makeDbBtn)
        deleteClientsBtn = make_button('Limpa Clientes','customer.png')
        self.connect(deleteClientsBtn, SIGNAL("clicked()"), self.delete_clients)
        self.outputLayout.addWidget(deleteClientsBtn)
        
        self.outputLayout.addStretch()
    
    def stop_psql_click(self):
        res = QMessageBox.question(self, self.trUtf8("Parar Servidor"),
                                   self.trUtf8("""Parar o servidor LOCAL do Postgres?"""),
                                   QMessageBox.StandardButtons(QMessageBox.Yes|QMessageBox.No))
        if res == QMessageBox.Yes:
            xe = 'NET STOP postgresql-' + gl.server_version
            # print 'para o servidor'
            stdio.run_silent(xe)
            time.sleep(1)
            self.stopBtn.setText('Servidor parado!')
            gl.server_status = False # servidor parado
        else:
            xe = 'NET START postgresql-' + gl.server_version
            stdio.run_silent(xe)
            time.sleep(1)
            self.stopBtn.setText('Servidor a funcionar!')
            gl.server_status = True # servidor no ar
    
    def create_database(self):
        flag = True
        libpg.make_default(2)
        r = libpgadmin.make_users_9()
        if not r[0]:
            flag = False
            void = QMessageBox.information(None,
                                           self.trUtf8(""" Error """),
                                           self.trUtf8(r[1]),
                                           QMessageBox.StandardButtons(
                                               QMessageBox.Ok),
                                           QMessageBox.Ok) == QMessageBox.Ok
        else:
            c = libpgadmin.create_database_insoft()
            if not c[0]:
                flag = False
                void = QMessageBox.information(None,
                                               self.trUtf8(""" Error """),
                                               self.trUtf8(c[1]),
                                               QMessageBox.StandardButtons(QMessageBox.Ok),QMessageBox.Ok) == QMessageBox.Ok
            else:
                libpg.make_default(0)
                p = libpgadmin.change_user_psql()
                if not p[0]:
                    flag = False
                    void = QMessageBox.information(None,
                                                   self.trUtf8(""" Error """),
                                                   self.trUtf8(p[1]),
                                                   QMessageBox.StandardButtons(
                                                       QMessageBox.Ok),
                                                   QMessageBox.Ok) == QMessageBox.Ok
        if flag:
            void = QMessageBox.information(None,
                                           self.trUtf8(""" Info """),
                                           self.trUtf8('Base de dados criada com sucesso!'),
                                           QMessageBox.StandardButtons(
                                               QMessageBox.Ok),QMessageBox.Ok) == QMessageBox.Ok
    
    def delete_clients(self):
        res = QMessageBox.question(self, self.trUtf8("Limpa Clientes"),
                                   self.trUtf8("""Limpa a tabela de Clientes"""),
                                   QMessageBox.StandardButtons(QMessageBox.Yes|QMessageBox.No))
        if res == QMessageBox.Yes:
            libpg.execute_query('delete from clients')
            libpg.execute_query('ALTER SEQUENCE clients_id_seq RESTART WITH 1;')
    
    def make_downloads(self, tx):
        dataset = app_list_downloads()
        if dataset[0]:
            dataset = dataset[1]
            gl.msg = []
            self.clear_layout()
            self.garb.setText(tx)
            self.outputLayout.addWidget(self.garb)
            self.repaint()
            self.grid_downloads = QTableWidget()
            self.outputLayout.addWidget(self.grid_downloads)
            
            self.grid_downloads.setSelectionBehavior(QTableWidget.SelectRows)
            self.grid_downloads.setSelectionMode(QTableWidget.SingleSelection)
            self.grid_downloads.setEditTriggers(QTableWidget.NoEditTriggers)
            self.grid_downloads.verticalHeader().setDefaultSectionSize(20)
            self.grid_downloads.setAlternatingRowColors (True)
            self.grid_downloads.verticalHeader().setVisible(False)
            self.grid_downloads.resizeColumnsToContents()
            self.grid_downloads.setStyleSheet("alternate-background-color: #CAE00D;")
            ex_grid.ex_grid__ctrl_update (self.grid_downloads, {0:['Programa', 's', 0], 1:['Download', 'xb', -1],2:['file', 's', 1]}, dataset)
            self.grid_downloads.setColumnWidth(0, 220)
            self.grid_downloads.hideColumn(2)
            downloadBtn = QPushButton('Descarrega')
            self.outputLayout.addWidget(downloadBtn)
            self.connect(downloadBtn, SIGNAL("clicked()"), self.download_tools_click)
        else:
            QMessageBox.critical(None, self.trUtf8("Erro de FTP"),
                                 self.trUtf8(dataset[1]))
    
    def download_tools_click(self):
        a = []
        if not os.path.exists('c:\\tmp\\'):
            os.makedirs('c:\\tmp\\')
        for linha in range(0, self.grid_downloads.rowCount()):
            if self.grid_downloads.item(linha, 1) is not None:
                pass
            else:
                if self.grid_downloads.cellWidget(linha, 1).layout().itemAt(1).widget().isChecked(): #  .isChecked(): # foi escolhido
                    a.append((linha,str(self.grid_downloads.item(linha,2).text())))
        self.app_downloads(a)

    def download_drivers(self,tx):
        self.clear_layout()
        self.garb.setText('Download Drivers')
        self.outputLayout.addWidget(self.garb)
        self.driverTypeCBox = QComboBox()
        self.driverTypeCBox.addItems(['Nenhum', 'Impressoras', 'Touch', 'P.O.S.', u'Biométricos'])
        self.connect(self.driverTypeCBox, SIGNAL("currentIndexChanged(int)"), self.drivers_refresh)
        self.outputLayout.addWidget(self.driverTypeCBox)
        self.driverDownloadGrid = QTableWidget()
        self.driverDownloadGrid.setSelectionBehavior(QTableWidget.SelectRows)
        self.driverDownloadGrid.setSelectionMode(QTableWidget.SingleSelection)
        self.driverDownloadGrid.setEditTriggers(QTableWidget.NoEditTriggers)
        self.driverDownloadGrid.verticalHeader().setDefaultSectionSize(20)
        self.driverDownloadGrid.setAlternatingRowColors(True)
        self.driverDownloadGrid.verticalHeader().setVisible(False)
        self.driverDownloadGrid.resizeColumnsToContents()
        self.driverDownloadGrid.setRowCount(0)
        self.driverDownloadGrid.setStyleSheet("alternate-background-color: #ffe6ff;")
        self.outputLayout.addWidget(self.driverDownloadGrid)
        driverDowBtn = QPushButton('Descarrega')
        self.connect(driverDowBtn, SIGNAL("clicked()"), self.download_drivers_click)
        self.outputLayout.addWidget(driverDowBtn)
        
    def drivers_refresh(self):
        if self.driverTypeCBox.currentIndex() == 0:
            self.driverDownloadGrid.clear()
            self.driverDownloadGrid.setRowCount(0)
            # dataset = bin_list('/drivers/')
        else:
            filter = gl.driver_dict[unicode(self.driverTypeCBox.currentText())]
            dataset = ftp_lic.driver_list(filter)
            if dataset[0]:
                dataset = dataset[1]
                ex_grid.ex_grid__ctrl_update (self.driverDownloadGrid, {0:['Driver', 's', 0], 1:['Download', 'xb', -1], 2:['file', 's', 1]}, dataset)
                self.driverDownloadGrid.setColumnWidth(0, 400)
                self.driverDownloadGrid.setColumnWidth(1, 100)
                self.driverDownloadGrid.setColumnWidth(2,0)
            else:
                QMessageBox.critical(None, self.trUtf8("Erro de FTP"), self.trUtf8(dataset[1]))

    def download_drivers_click(self):
        ftp_error = ''
        stdio.dir_ok('c://tmp')
        driver_dowload_list = []
        c = ''
        for linha in range(0, self.driverDownloadGrid.rowCount()):
            if self.driverDownloadGrid.item(linha, 1) is not None:
                pass
            else:
                if self.driverDownloadGrid.cellWidget(linha, 1).layout().itemAt(1).widget().isChecked():
                    driver_dowload_list.append((linha, str(self.driverDownloadGrid.item(linha, 2).text())))
        """start the download"""
        t0 = time.time()
        try:
            # Establish the connection
            ftp = ftplib.FTP(gl.ftp1[2], timeout=5)
            ftp.login(gl.ftp1[0], gl.ftp1[1])
            # Change to the proper directory
            ftp.cwd('/drivers/')
            for n in driver_dowload_list:
                file_name = n[1]
                self.statusBarMain.showMessage('Start Download ' + file_name)
                gl.msg.append('Start Download ' + file_name)
                fhandle = open('c:\\tmp\\' + file_name, 'wb')
                ftp.retrbinary('RETR ' + file_name, fhandle.write)
                fhandle.close()
                resp = ftp.sendcmd("MDTM %s" % file_name)
                self.statusBarMain.showMessage('Finish Download ' + file_name)
                gl.msg.append('Finish Download ' + file_name)
                self.driverDownloadGrid.cellWidget(n[0], 1).layout().itemAt(1).widget().setChecked(False)
            ftp.quit()
            t1 = time.time()
            self.statusBarMain.showMessage('Tempo decorrido: ' + stdio.seconds_to_hours(t1 - t0))
        except Exception as err:
            ftp_error = str(err)
        
        if ftp_error == '':
            pass
        else:
            QMessageBox.critical(None, self.trUtf8("Erro de FTP"), self.trUtf8(ftp_error))
    
   
    def binaries_download(self, tx):
        self.clear_layout()
        self.garb.setText(tx)
        self.outputLayout.addWidget(self.garb)
        self.version_cb = QComboBox()
        self.version_cb.addItems(['iws','2020.2.0','2020.1.0','2018.2.0','2018.1.0.0'])
        self.connect(self.version_cb, SIGNAL("currentIndexChanged(int)"), self.binaries_refresh)
        self.outputLayout.addWidget(self.version_cb)
        self.bin_download = QTableWidget()
        self.bin_download.setSelectionBehavior(QTableWidget.SelectRows)
        self.bin_download.setSelectionMode(QTableWidget.SingleSelection)
        self.bin_download.setEditTriggers(QTableWidget.NoEditTriggers)
        self.bin_download.verticalHeader().setDefaultSectionSize(20)
        self.bin_download.setAlternatingRowColors (True)
        self.bin_download.verticalHeader().setVisible(False)
        self.bin_download.resizeColumnsToContents()
        self.bin_download.setRowCount(0)
        self.bin_download.setStyleSheet("alternate-background-color: #ccfff2;")
        self.outputLayout.addWidget(self.bin_download)
        dwonl_Btn = QPushButton('Descarrega')
        self.outputLayout.addWidget(dwonl_Btn)
        self.connect(dwonl_Btn, SIGNAL("clicked()"), self.download_binaries_click)
        replace_btn = QPushButton('Substitui')
        self.outputLayout.addWidget(replace_btn)
        self.connect(replace_btn, SIGNAL("clicked()"), self.replace_binaries_click)
        sha256Btn = QPushButton('Verifica SHA256')
        self.outputLayout.addWidget(sha256Btn)
        self.connect(sha256Btn, SIGNAL("clicked()"), self.sha256_click)
    
    def download_binaries_click(self):
        try:
            shutil.rmtree('c://tmp//bin')
        except Exception as e:
            print('download binaries', str(e))
        stdio.dir_ok('c://tmp//bin')
        self.bin_dwn = []
        c = ''
        for linha in range(0, self.bin_download.rowCount()):
            if self.bin_download.item(linha, 1) is not None:
                pass
            else:
                if self.bin_download.cellWidget(linha, 1).layout().itemAt(1).widget().isChecked():
                    self.bin_dwn.append((linha,str(self.bin_download.item(linha,0).text())))
        if self.version_cb.currentIndex() == 0:
            c = '/iws_binaries/'
        else:
            c = '/restware_binaries/' + str(self.version_cb.currentText()).replace('.','_') + '/'
        
        xl = self.bin_select_download(self.bin_dwn, c)
        if xl[0]:
            pass
        else:
            QMessageBox.critical(None, self.trUtf8("Erro de FTP"), self.trUtf8(xl[1]))
    
    def bin_select_download(self, dw_list, p_dir):
        t0 = time.time()
        try:
            # Establish the connection
            ftp = ftplib.FTP(gl.ftp1[2], timeout=5)
            ftp.login(gl.ftp1[0], gl.ftp1[1])
            # Change to the proper directory
            ftp.cwd(p_dir)
            for n in dw_list:
                file_name = n[1]
                self.statusBarMain.showMessage('Start Download ' + file_name)
                gl.msg.append('Start Download ' + file_name)
                fhandle = open('c:\\tmp\\bin\\' + file_name, 'wb')
                ftp.retrbinary('RETR ' + file_name, fhandle.write)
                fhandle.close()
                resp=ftp.sendcmd("MDTM %s" % file_name)
                self.statusBarMain.showMessage('Finish Download ' + file_name)
                gl.msg.append('Finish Download ' + file_name)
                self.bin_download.cellWidget(n[0], 1).layout().itemAt(1).widget().setChecked(False)
            ftp.quit()
            t1 = time.time()
            self.statusBarMain.showMessage('Tempo decorrido: ' + stdio.seconds_to_hours(t1-t0))
        except Exception as err:
            return False, str(err)
        return True, 'OK'
    
    def binaries_refresh(self):
        if self.version_cb.currentIndex() == 0:
            dataset = bin_list('/iws_binaries/')
        else:
            dataset = bin_list('/restware_binaries/' + str(self.version_cb.currentText()).replace('.','_') + '/')
        if dataset[0]:
            dataset = dataset[1]
            ex_grid.ex_grid__ctrl_update (self.bin_download, {0:['Programa', 's', 0], 1:['Download', 'xb', -1],2:['Size', 'i', 1] }, dataset)
            self.bin_download.setColumnWidth(0, 130)
            self.bin_download.setColumnWidth(2, 60)
        else:
            QMessageBox.critical(None, self.trUtf8("Erro de FTP"),
                                 self.trUtf8(dataset[1]))
    
    def replace_binaries_click(self):
        self.download_binaries_click()
        stdio.dir_ok('c:\\insoft\\', create=True)
        for a in self.bin_dwn:
            try:
                shutil.copy2('c:\\tmp\\bin\\' + a[1], 'c:\\insoft\\' + a[1])
            except Exception as e:
                pass
    
    def sha256_click(self):
        self.download_binaries_click()
        xe = []
        for a in self.bin_dwn:
            try:
                hl = stdio.get_sha256('c:\\tmp\\bin\\' + a[1], 16)
                bc = stdio.get_sha256('c:\\insoft\\' + a[1], 16)
                if bc == hl:
                    xe.append((a[1],hl,' OK') )
                else:
                    xe.append((a[1],hl,bc,' ERROR'))
            except Exception as e:
                xe.append((a[1],'00000000000', 'FILE NOT FOUND'))
        bc = 'Resultados da Análise sha256\n' + xe
        form = report_viewer.PlainText(u'Resultados da Análise sha256', bc)
        form.exec_()
    
    
    def make_config(self, tx):
        font = QFont('courier new',10)
        font.setWeight(80)
        font.setBold(False)
        self.tab1 = QWidget()
        self.clear_layout()
        self.garb.setText(tx)
        self.outputLayout.addWidget(self.garb)
        self.portEdit = QLineEdit()
        self.portEdit.setMaximumWidth(40)
        self.portEdit.setText(gl.pos_ini['port'])
        self.outputLayout.addWidget(self.portEdit)
        self.ipEdit = QLineEdit()
        self.ipEdit.setMaximumWidth(300)
        self.ipEdit.setText(gl.pos_ini['host'])
        self.outputLayout.addWidget(self.ipEdit)
        self.time_out = QLineEdit()
        self.time_out.setMaximumWidth(100)
        self.time_out.setText('3')
        self.outputLayout.addWidget(self.time_out)
        testBtn = make_button('Testa')
        self.connect(testBtn, SIGNAL("clicked()"), self.test_connection_click)
        self.outputLayout.addWidget(testBtn)
        self.outputLayout.addStretch()
    
    def update_click(self, tx):
        self.clear_layout()
        self.garb.setPixmap(QPixmap('update.png'))
        self.outputLayout.addWidget(self.garb)
        update_internet = make_button('Com Internet','with_internet.png')
        self.connect(update_internet, SIGNAL("clicked()"), self.internet_update_click)
        self.outputLayout.addWidget(update_internet)
        self.outputLayout.addWidget(update_internet)
        laptopBtn = make_button(u'Atualiza/Instala portátil','laptop.png')
        self.connect(laptopBtn, SIGNAL("clicked()"), self.update_laptop)
        self.outputLayout.addWidget(laptopBtn)
        backupTestBtn = make_button('Faz Backup','test_backup.png')
        self.connect(backupTestBtn, SIGNAL("clicked()"), self.backup_test_click)
        self.outputLayout.addWidget(backupTestBtn)
        oldLaptopBtn = make_button(u'Atualiza portátil 2018.2','laptop.png')
        self.connect(oldLaptopBtn, SIGNAL("clicked()"), self.update_laptop_2018)
        self.outputLayout.addWidget(oldLaptopBtn)
        self.outputLayout.addStretch()
    
    def replace_lic_files_unlock(self):
        flag = True
        form = lics_download.DownloadLic(one=True, mode=1)
        form.exec_()
        if gl.update_settings['run']:
            target_dir = 'c:\\insoft'
            lic_paths = lics_download.lic_files_path('c:\\insoft')
            lics_download.lic_clean('c:\\insoft',gl.update_settings['lic_file'], lic_paths)
            lics_download.lic_download(gl.update_settings['lic_file'])
            flag = lics_download.lic_copy(gl.update_settings['lic_file'], target_dir, lic_paths)
            libpg.execute_query("update params set lic=Null, saftnif='',saftname='', saftcity= '', saftaddress = '', saftpostalcode='', commercial_name='' ", (True,))
            flag = True

            if flag:
                void = QMessageBox.information(None,
                                               self.trUtf8(""" Info """),
                                               self.trUtf8('Lics substituidas e destrancada a bd'),
                                               QMessageBox.StandardButtons(QMessageBox.Ok), QMessageBox.Ok) == QMessageBox.Ok
            else:
                void = QMessageBox.information(None,
                                               self.trUtf8(""" Error """),
                                               self.trUtf8(u'Ocorreu um erro GRAVE\n'),
                                               QMessageBox.StandardButtons(QMessageBox.Ok),QMessageBox.Ok) == QMessageBox.Ok

    def replace_lic_files(self):
        flag = True
        form = lics_download.DownloadLic(one=True, mode=1)
        form.exec_()
        if gl.update_settings['run']:
            lic_paths = lics_download.lic_files_path('c:\\insoft')
            lics_download.lic_clean('c:\\insoft',gl.update_settings['lic_file'],lic_paths)
            lics_download.lic_download(gl.update_settings['lic_file'])
            flag = lics_download.lic_copy(gl.update_settings['lic_file'], 'c:\\insoft', lic_paths)
            flag = True
            if flag:
                void = QMessageBox.information(None,
                                               self.trUtf8(""" Info """),
                                               self.trUtf8('Lics substituidas'),
                                               QMessageBox.StandardButtons(QMessageBox.Ok), QMessageBox.Ok) == QMessageBox.Ok
            else:
                void = QMessageBox.information(None,
                                               self.trUtf8(""" Error """),
                                               self.trUtf8(u'Ocorreu um erro GRAVE\n'),
                                               QMessageBox.StandardButtons(QMessageBox.Ok),QMessageBox.Ok) == QMessageBox.Ok
    
    def update_laptop(self):
        server_dir = '/restware_binaries/' + gl.PRODUCTION_VERSION.replace('.', '_') + '/'
        self.update_laptop_all(server_dir)
        
    def update_laptop_2018(self):
        server_dir = '/restware_binaries/2018_2_0/'
        self.update_laptop_all(server_dir)

    def update_laptop_all(self, server_dir):
        flag = 255
        message = ''
        dir_target = QFileDialog.getExistingDirectory(self, 'Escolhe a Pasta', 'c:\\insoft\\')
        dir_target = str(dir_target)
        if dir_target == '':
            flag = 2
        else:
            void = self.laptop_download(['posback.exe', 'checklic.exe'], server_dir, dir_target)
            x, nif = lics_download.get_lic_nif(dir_target)
            form = lics_download.DownloadLic(one=True, mode=1, nif=nif)
            form.exec_()
            if gl.update_settings['run']:
                lic_paths = lics_download.lic_files_path(dir_target, recursive=False)
                lics_download.lic_clean(dir_target, gl.update_settings['lic_file'], lic_paths)
                lics_download.lic_download(gl.update_settings['lic_file'])
                flag = lics_download.lic_copy(gl.update_settings['lic_file'], dir_target, lic_paths)
                if flag:
                    resp, nif = lics_download.get_lic_nif(dir_target)  # + 'insoft.lic')
                    if not stdio.file_ok(str(dir_target) + '\\posback.ini'):
                        rest, ok = QInputDialog.getText(self, self.tr("DDNS input"), self.tr(u"DDNS"), QLineEdit.Normal)
                        if ok:
                            gl.pos_ini['host'] = str(rest)
                            rebuild.build_posback_ini(str(dir_target) + '\\posback.ini', str(rest))
                            message = 'NIF:' + str(nif) + '\nPASTA: ' + dir_target + '\nLIC: ' + gl.update_settings[
                                'lic_file'] + '\nDDNS: ' + str(rest)
                            flag = 1
                        else:
                            message = 'Abortado ao entrar DDNS'
                            flag = 255
                
                    else:
                        message = 'NIF:' + str(nif) + '\nPASTA: ' + dir_target + '\nLIC: ' + gl.update_settings['lic_file']
                        flag = 1
                else:
                    message = 'Erro '
                    flag = 255
            else:
                flag = 2
    
        if flag == 255:
            void = QMessageBox.information(None, self.trUtf8(""" Error """), message,
                                           QMessageBox.StandardButtons(QMessageBox.Ok),
                                           QMessageBox.Ok) == QMessageBox.Ok
        elif flag == 2:
            pass
        elif flag == 1:
            void = QMessageBox.information(None, self.trUtf8(""" Info """), message,
                                           QMessageBox.StandardButtons(QMessageBox.Ok),
                                           QMessageBox.Ok) == QMessageBox.Ok

    def laptop_download(self, files_to, server_dir, target_dir):
        try:
            # Establish the connection
            ftp = ftplib.FTP(gl.ftp1[2], timeout=5)
            ftp.login(gl.ftp1[0], gl.ftp1[1])
            # Change to the proper directory
            ftp.cwd(server_dir)
            for file_name in files_to:
                self.statusBarMain.showMessage('Start Download ' + file_name)
                fhandle = open(target_dir + '\\' + file_name, 'wb')
                ftp.retrbinary('RETR ' + file_name, fhandle.write)
                fhandle.close()
                resp = ftp.sendcmd("MDTM %s" % file_name)
                self.statusBarMain.showMessage('Finish Download ' + file_name)
            ftp.quit()
        except Exception as err:
            return False, str(err)
        return True, 'OK'
    
    
    def internet_update_click(self):
        a = psql_check.psql_listen()
        if not a[0]:
            errorMessage = QErrorMessage(self)
            errorMessage.showMessage(a[1])
        else:
            form = updater.UpdaterConsole()
            form.exec_()
    
    def update_no_internet_click(self):
        form = updater.UpdaterConsole(internet=False)
        form.exec_()
        
    def show_posini(self):
        hl = stdio.read_config_file('c:\\insoft\\pos.ini')
        form = report_viewer.TableView('POS.INI', hl)
        form.exec_()
    
    def show_posbackini(self):
        hl = stdio.read_config_file('c:\\insoft\\posback.ini')
        form = report_viewer.TableView('POSBACK.INI', hl)
        form.exec_()
    
    def show_manbakini(self):
        hl = stdio.read_config_file('c:\\insoft\\manback.ini')
        form = report_viewer.TableView('MANBACK.INI', hl)
        form.exec_()
    
    def send_email(self,tx):
        self.clear_layout()
        self.garb.setPixmap(QPixmap('email.png'))
        self.outputLayout.addWidget(self.garb)
        l2 = QLabel(u'Endereços de mail separados por virgulas')
        self.outputLayout.addWidget(l2)
        self.mail_dest = QLineEdit()
        self.outputLayout.addWidget(self.mail_dest)
        l4 = QLabel(u'Ficheiros a enviar')
        self.outputLayout.addWidget(l4)
        self.fileToSend = QLineEdit()
        self.fileToSend.setReadOnly(True)
        self.outputLayout.addWidget(self.fileToSend)
        addAttachmentsBtn = QToolButton()
        addAttachmentsBtn.setIcon(QIcon('attach.png'))
        self.connect(addAttachmentsBtn, SIGNAL("clicked()"), self.attach_add_click)
        self.outputLayout.addWidget(addAttachmentsBtn)
        self.msgCannedCb = QComboBox()
        self.msgCannedCb.setEditable(True)
        self.msgCannedCb.addItems(['',u'Mapa de IVA',u'Relatório de Vendas', u'Facturas em PDF',
                                   u'Ficheiros de Backup',u'Conta Corrente'])
        self.connect(self.msgCannedCb, SIGNAL("editTextChanged(QString)"), self.canned_msg_change)
        
        self.outputLayout.addWidget(self.msgCannedCb)
        self.previewLabel = QLabel()
        self.outputLayout.addWidget(self.previewLabel)
        l3 = QLabel('Mensagem')
        self.outputLayout.addWidget(l3)
        self.body_msg = QTextEdit()
        self.outputLayout.addWidget(self.body_msg)
        self.euzinhoCheck = QCheckBox('Euzinho')
        self.euzinhoCheck.setCheckState(0)
        self.connect(self.euzinhoCheck,SIGNAL("stateChanged(int)"), self.euzinho_change_state)
        self.outputLayout.addWidget(self.euzinhoCheck)
        self.outputLayout.addStretch()
        
        emailSend = QCommandLinkButton('Envia')
        emailSend.setIcon(QIcon('email_send.png'))
        self.connect(emailSend, SIGNAL("clicked()"), self.send_mail_click)
        self.outputLayout.addWidget(emailSend)
        psql_check.get_saft_data()
        if gl.saft_config_dict['saft_to'] is None:
            self.mail_dest.setText('')
        else:
            self.mail_dest.setText(gl.saft_config_dict['saft_to'])
        if self.euzinhoCheck.isChecked():
            self.previewLabel.setText('')
        else:
            self.previewLabel.setText(' NIF: ' + gl.saft_config_dict['saftnif'] + ' ' + gl.saft_config_dict['saftname'].decode('utf-8'))

    def euzinho_change_state(self, a):
        if a == 0 and self.IS_ALIVE:
            psql_check.get_saft_data()
        if a == 2:
            gl.saft_config_dict = {'saftname': 'Espiridiao', 'saftaddress': 'Alvor', 'saftpostalcode': '0000-000',
                                   'saftcity': 'Alvor',
                                   'saftnif': '507534050','commercial_name':'Sistema'}
        self.canned_msg_change(self.msgCannedCb.currentText())

    
    def short_msg_text_changed(self):
        self.msgRef.setText(self.ref_string + self.body_msg.toPlainText())
    
    def attach_add_click(self):
        file_list = QFileDialog.getOpenFileNames(self, 'Open file','c:\\tmp\\' )
        self.att_files = []
        a = ''
        if file_list.isEmpty():
            # vazio
            pass
        else:
            for n in file_list:
                self.att_files.append(str(n))
                c = os.path.basename(str(n))
                a = a + ';' + c
            self.fileToSend.setText(a)
    
    def canned_msg_change(self,txt):
        if self.euzinhoCheck.isChecked():
            a = txt
        else:
            a = txt + ' NIF: ' + gl.saft_config_dict['saftnif'] + ' ' + gl.saft_config_dict['saftname'].decode('utf-8')
        self.previewLabel.setText(a)
    
    def send_mail_click(self):
        if self.mail_dest.text() == '':
            void = QMessageBox.information(self, self.trUtf8("Erro"), self.trUtf8("""Envio para onde!"""), QMessageBox.StandardButtons(QMessageBox.Ok))
        else:
            if self.msgCannedCb.currentIndex() >0:
                headers = smtpmail.make_email_headers(unicode(self.previewLabel.text()).encode('utf-8'), unicode(self.fileToSend.text()).encode('utf-8'), self.body_msg.toPlainText())
                a = smtpmail.send_saft_smtp(str(self.mail_dest.text()), self.att_files, headers)
                if a:
                    void = QMessageBox.information(self, self.trUtf8("Mensagem"), self.trUtf8("""Mail enviado com sucesso!"""), QMessageBox.StandardButtons(QMessageBox.Ok))
                else:
                    void = QMessageBox.information(self, self.trUtf8("Erro"), self.trUtf8("""Erro ao enviar o mail!"""), QMessageBox.StandardButtons(QMessageBox.Ok))
            else:
                void = QMessageBox.information(self, self.trUtf8("Erro"), self.trUtf8("""Falta o assunto!"""),
                                               QMessageBox.StandardButtons(QMessageBox.Ok))
    
    def make_saft(self, tx):
        self.clear_layout()
        self.outputLayout.addWidget(self.garb)
        self.saft_periodCB = QComboBox()
        self.saft_periodCB.addItems(['Mensal','Anual','Entre Datas'])
        self.saft_periodCB.setMaximumWidth(100)
        self.connect(self.saft_periodCB, SIGNAL("currentIndexChanged(int)"), self.saft_periodCB_change)
        self.outputLayout.addWidget(self.saft_periodCB)
        
        self.saft_yearCBox = QComboBox()
        self.saft_yearCBox.addItems(gl.saft_years_list)
        self.saft_yearCBox.setMaximumWidth(100)
        self.outputLayout.addWidget(self.saft_yearCBox)
        self.saft_month = QComboBox()
        self.saft_month.addItems(gl.meses)
        self.saft_month.setMaximumWidth(100)
        self.outputLayout.addWidget(self.saft_month)
        
        l3 = QLabel(u'Numeros dos meses em batch,separados , ou ; ou espaço')
        self.outputLayout.addWidget(l3)
        self.saf_batch = QLineEdit()
        self.outputLayout.addWidget(self.saf_batch)
        l2 = QLabel(u'Endereços de mail separados por ;')
        self.outputLayout.addWidget(l2)
        self.saft_mail_dest = QLineEdit()
        self.outputLayout.addWidget(self.saft_mail_dest)
        l4 = QLabel('Nome comercial')
        self.outputLayout.addWidget(l4)
        self.unit_name = QLineEdit()
        self.outputLayout.addWidget(self.unit_name)
        put_mails_btn = QToolButton()
        put_mails_btn.setIcon(QIcon('save.png'))
        self.connect(put_mails_btn, SIGNAL("clicked()"), self.save_mails_add)
        self.outputLayout.addWidget(put_mails_btn)
        
        l3 = QLabel('Mensagem adicional')
        self.outputLayout.addWidget(l3)
        self.saft_msg = QTextEdit()
        self.outputLayout.addWidget(self.saft_msg)
        
        updateSaftBin = QCommandLinkButton('Actualiza binario')
        self.connect(updateSaftBin, SIGNAL("clicked()"), self.update_saft_click)
        self.outputLayout.addWidget(updateSaftBin)
        
        resetSaftDate = QCommandLinkButton('Limpa a data')
        self.connect(resetSaftDate, SIGNAL("clicked()"), self.reset_saft_date)
        self.outputLayout.addWidget(resetSaftDate)
        
        saft_makeBtn = make_button('Gera e envia','send_saft.png')
        self.connect(saft_makeBtn, SIGNAL("clicked()"), self.saft_make_send)
        self.outputLayout.addWidget(saft_makeBtn)
        
        self.outputLayout.addStretch()
        if gl.saft_config_dict['saft_to'] is None:
            self.saft_mail_dest.setText('')
        else:
            self.saft_mail_dest.setText(gl.saft_config_dict['saft_to'])
        self.unit_name.setText(gl.saft_config_dict['commercial_name'].decode('utf-8'))

    
    def saft_periodCB_change(self, i):
        if i == 0:
            self.saft_month.setEnabled(True)
            self.saft_yearCBox.setEnabled(True)
        elif i == 1:
            self.saft_month.setEnabled(False)
            self.saft_yearCBox.setEnabled(True)
    
    def reset_saft_date(self):
        libpg.execute_query('update saft_config set saft_last_send=%s', ('1970-01-01',))
    
    def update_saft_click(self):
        file_name = 'SAF-T.exe'
        t0 = time.time()
        self.statusBarMain.showMessage('Start Download ' + file_name)
        flag, text = updater.update_saft_bin()
        if flag:
            self.statusBarMain.showMessage('Finish Download ' + file_name)
            gl.msg.append('Finish Download ' + file_name)
            t1 = time.time()
            self.statusBarMain.showMessage('Tempo decorrido: ' + stdio.seconds_to_hours(t1 - t0))
            gl.msg.append('Tempo decorrido: ' + stdio.seconds_to_hours(t1 - t0))
        else:
            self.statusBarMain.showMessage('ERROR on Download ' + file_name)
            QMessageBox.information(None,
                                    self.trUtf8(u'Erro de FTP'.encode('utf-8')),
                                    self.trUtf8(text), QMessageBox.StandardButtons(QMessageBox.Close),
                                    QMessageBox.Close)

    def saft_make_send(self):
        BATCH_SEND = False
        if stdio.file_ok('c:\\insoft\\mansaft.exe'):
            if not self.saft_mail_dest.text().isEmpty():
                a = self.saft_periodCB.currentIndex()
                if a == 0: # mensal
                    if self.saf_batch.text().isEmpty():
                        i,f = saft_time_frame(self.saft_month.currentIndex() + 1, int(self.saft_yearCBox.currentText()))
                        gl.saft_config_dict['saft_month'] = self.saft_month.currentIndex() + 1
                        gl.saft_config_dict['saft_year'] = str(self.saft_yearCBox.currentText())
                    else:
                        BATCH_SEND = True
                elif a == 1:
                    i = datetime.date(int(self.saft_yearCBox.currentText()), 1, 1)
                    f = datetime.date(int(self.saft_yearCBox.currentText()), 12, 31)
                    gl.saft_config_dict['saft_month'] = 13
                    gl.saft_config_dict['saft_year'] = str(self.saft_yearCBox.currentText())
                if BATCH_SEND:
                    c = str(self.saf_batch.text())
                    c = c.replace('.',',')
                    c = c.replace(' ',',')
                    c = c.replace(';',',')
                    xl = c.split(',')
                    for pc in xl:
                        i, f = saft_time_frame(int(pc), int(self.saft_yearCBox.currentText()))
                        gl.saft_config_dict['saft_month'] = int(pc)
                        gl.saft_config_dict['saft_year'] = str(self.saft_yearCBox.currentText())
                        gl.saft_config_dict['saft_to'] = str(self.saft_mail_dest.text())
                        gl.msg_to_sender = '<br>' + unicode(self.saft_msg.toPlainText()).encode('utf-8')
                        flag = libsaft.gera_saft(i, f, str(self.saft_mail_dest.text()))
                else:
                    gl.saft_config_dict['saft_to'] = str(self.saft_mail_dest.text())
                    gl.msg_to_sender = '<br>' + unicode(self.saft_msg.toPlainText()).encode('utf-8')
                    bc = 'Enviado\n' + str(self.saft_mail_dest.text()).replace(',','\n')
                    flag = libsaft.gera_saft(i, f, str(self.saft_mail_dest.text()))
            else:
                gl.msg = ['Sem destinatarios']
                flag = False
        else:
            gl.msg.append('File mansaft.exe not found')
            bc = 'Erro' + '\n'.join(gl.msg)
            flag = False
        if not flag:
            bc = 'Erro\n' + '\n'.join(gl.msg)
            form = report_viewer.PlainText('Mensagem de erro', bc)
            form.exec_()
        else:
            if BATCH_SEND:
                sys.exit(0)
            else:
                form = report_viewer.PlainText('Mensagem', bc)
                form.exec_()
            gl.msg = []
    
    def get_mails_saft(self):
        if libpg.check_field('saft_config', 'id'):
            xl = psql_check.get_saft_data()
            
    def save_mails_add(self):
        if self.saft_mail_dest.text().isEmpty():
            QMessageBox.information(self, self.trUtf8("Error"), self.trUtf8("""Os endereços foram limpos."""),
                                        QMessageBox.StandardButtons(QMessageBox.Ok))
        
        if libpg.check_field('saft_config', 'id'):
            libpg.execute_query('update saft_config set saft_to=%s',(str(self.saft_mail_dest.text()), ))
            gl.saft_config_dict['saft_to'] = str(self.saft_mail_dest.text())
        else:
            libpg.create_saft_table()
            libpg.execute_query('update saft_config set saft_to=%s',(str(self.saft_mail_dest.text()), ))
    
    
    def make_info(self,tx):
        self.clear_layout()
        self.garb.setPixmap(QPixmap('all_info.png'))
        self.outputLayout.addWidget(self.garb)
        info_restware = make_button('Parametros do Restware')
        self.connect(info_restware, SIGNAL("clicked()"), self.info_restware_click)
        self.outputLayout.addWidget(info_restware)
        
        info_psql = make_button('Estatisticas do Postgres')
        self.connect(info_psql, SIGNAL("clicked()"), self.info_psql_click)
        self.outputLayout.addWidget(info_psql)
        
        info_system = make_button(u'Informações do Sistema')
        info_system.setIcon(QIcon('sys_info.png'))
        self.connect(info_system, SIGNAL("clicked()"), self.info_windows_click)
        self.outputLayout.addWidget(info_system)
        printUserBtn = make_button('Imprime Utilizadores', 'user_list.png')
        self.connect(printUserBtn, SIGNAL("clicked()"), self.list_user_click)
        self.outputLayout.addWidget(printUserBtn)
        usr_Btn = make_button('Users', 'users.png')
        self.connect(usr_Btn, SIGNAL("clicked()"), self.check_user_click)
        self.outputLayout.addWidget(usr_Btn)
        self.outputLayout.addStretch()
    
    def make_backoffice(self):
        self.clear_layout()
        self.garb.setPixmap(QPixmap('backoffice.png'))
        self.outputLayout.addWidget(self.garb)
        invoice_browser = make_button('Navegador de Documentos')
        self.connect(invoice_browser, SIGNAL("clicked()"), self.doc_browser_click)
        self.outputLayout.addWidget(invoice_browser)
        client_browser = make_button('Navegador de Clientes')
        self.connect(client_browser, SIGNAL("clicked()"), self.client_browser_click)
        self.outputLayout.addWidget(client_browser)
        self.outputLayout.addStretch()
    
    def doc_browser_click(self):
        form = doc_browser.DocumentBrowser()
        form.exec_()
    
    def client_browser_click(self):
        form = client_browser.ClientBrowser()
        form.exec_()
    
    def info_restware_click(self):
        # c = self.psql_up()
        short = stdio.info_restware_short()
        hl = short[0]
        hl += stdio.info_restware_long()
        hl += short[1]
        form = report_viewer.PlainText(u'''Restware Info''', hl)
        form.exec_()
        ''' future detail for backup info'''
        # hl += stdio.info_restware_detail()
        # hl += stdio.info_psql()
        # print hl
        
    def info_psql_click(self):
        form = report_viewer.PlainText(u'Informações do PostgreSQL', stdio.info_psql())
        form.exec_()
    
    def info_windows_click(self):
        hl = ''
        hl += win_interface.system_stats()
        hl += win_interface.df()
        hl += win_interface.pc_info()
        form = report_viewer.PlainText(u'Informações do Sistema', hl)
        form.exec_()
    
    def soft_install_click(self):
        hl = win_interface.get_install_software()
        form = report_viewer.TableView(u'Informações do Sistema', hl,ini=False)
        form.exec_()
    
    def app_downloads(self, dwlist):
        t0 = time.time()
        root = '/bin/'
        directory = root
        try:
            ftp = ftplib.FTP(gl.ftp1[2], timeout=5)
            ftp.login(gl.ftp1[0], gl.ftp1[1])
            
            # Change to the proper directory
            stdio.dir_ok('c:\\tmp\\', create=True)
            ftp.cwd(directory)
            for n in dwlist:
                file_name = n[1]
                self.statusBarMain.showMessage('Start Download ' + file_name)
                gl.msg.append('Start Download ' + file_name)
                fhandle = open('c:\\tmp\\' + file_name, 'wb')
                ftp.retrbinary('RETR ' + file_name, fhandle.write)
                fhandle.close()
                # resp=ftp.sendcmd("MDTM %s" % file_name)
                self.statusBarMain.showMessage('Finish Download ' + file_name)
                gl.msg.append('Finish Download ' + file_name)
                self.grid_downloads.cellWidget(n[0], 1).layout().itemAt(1).widget().setChecked(False)
                t1 = time.time()
                self.statusBarMain.showMessage('Tempo decorrido: ' + stdio.seconds_to_hours(t1-t0))
                gl.msg.append('Tempo decorrido: ' + stdio.seconds_to_hours(t1-t0))
            ftp.close()
        except Exception as err:
            ftp.close()
            QMessageBox.information(None,
                                    self.trUtf8(u'Erro de FTP'.encode('utf-8')),
                                    self.trUtf8(str(err)) ,QMessageBox.StandardButtons(QMessageBox.Close), QMessageBox.Close)
    
    def sql_browser_click(self):
        # 14-01-2019
        if gl.dos == True:
            if GetSystemMetrics(0) == 800:
                void = QMessageBox.information( self, self.trUtf8("Display Error"), self.trUtf8("""Resolution to low"""),
                                                QMessageBox.StandardButtons(QMessageBox.Ok))
            else:
                form = dbbrowser.InsideSql()
                form.exec_()
        else:
            form = dbbrowser.InsideSql()
            form.exec_()
    
    def backup_test_click(self):
        status = stdio.make_backup()
        if status[0]:
            void = QMessageBox.information(None,
                                           self.trUtf8(""" Info """),
                                           self.trUtf8('Backup efectuado\n' + status[1] ),
                                           QMessageBox.StandardButtons(QMessageBox.Ok),
                                           QMessageBox.Ok) == QMessageBox.Ok
        else:
            void = QMessageBox.information(None,
                                           self.trUtf8(""" Erro """),
                                           self.trUtf8(u'Ocorreu um erro \n' + status[1]),
                                           QMessageBox.StandardButtons(QMessageBox.Ok),
                                           QMessageBox.Ok) == QMessageBox.Ok
    
    def backup_last(self):
        status = stdio.get_last_backup()
        if status[0]:
            a = ''
            for key,val in status[1].items():
                a += str(key) + ': ' + str(val) + '\n'
                
            void = QMessageBox.information(None,
                                           self.trUtf8(""" Info """),
                                           self.trUtf8('Backup efectuado\n' + a ),
                                           QMessageBox.StandardButtons(QMessageBox.Ok),
                                           QMessageBox.Ok) == QMessageBox.Ok
        else:
            void = QMessageBox.information(None,
                                           self.trUtf8(""" Erro """),
                                           self.trUtf8(u'Ocorreu um erro \n' + status[1]),
                                           QMessageBox.StandardButtons(QMessageBox.Ok),
                                           QMessageBox.Ok) == QMessageBox.Ok
    
    def restore_backup_click(self):
        if gl.pos_ini['host'] in ('localhost', '127.0.0.1'):
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            file_name = QFileDialog.getOpenFileName(self, "Backup file","c:\\backup" ,"backup (*.backup)")
            
            if file_name:
                gl.file_name = file_name
                form = restore_db.RestoreDialog()
                form.exec_()
        else:
            QMessageBox.warning(None, self.trUtf8("Erro de backup"),
                                self.trUtf8('NÃO É PERMITIDO REPOR BASE DE DADOS REMOTAS.'))
    
    def apply_setting_click(self):
        gl.pos_ini['port'] = str(self.portEdit.text())
        gl.pos_ini['host'] = str(self.ipEdit.text())
        self.portEdit.setText(gl.pos_ini['port'])
        self.ipEdit.setText(gl.pos_ini['host'])
        libpg.make_default(0)
    
    def test_connection_click(self):
        gl.pos_ini['port'] = str(self.portEdit.text())
        gl.pos_ini['host'] = str(self.ipEdit.text())
        self.portEdit.setText(gl.pos_ini['port'])
        self.ipEdit.setText(gl.pos_ini['host'])
        libpg.make_default(0)
        gl.c = gl.c + ' connect_timeout=' + str(self.time_out.text())
        time.sleep(0.23)
        t0 = time.time()
        a = psql_check.psql_listen()
        if a[0]:
            gl.pos_ini['host'] = str(self.ipEdit.text())
            self.portEdit.setText(gl.pos_ini['port'])
            self.ipEdit.setText(gl.pos_ini['host'])
            libpg.make_default(0)
            html =  "{:>14}".format('IP: ') + gl.pos_ini['host'] + '\n'
            html += '-' *40 + '\n'
            html += self.info_restware_short()[0]
            html += '\n'
            html += self.info_psql()
            t1 = time.time()
            html += 'Tempo decorrido: ' + str((t1 - t0))[0:6]
        else:
            t1 = time.time()
            html = ''' <!DOCTYPE
            html > < html
            lang = "pt_pt"> <head> <meta
            charset = "utf-8" >
            </head> <img
            src = "./upss.png"><br><font size="5" face="verdana" color="red"><strong> ''' + a[1].replace('\n','<br>') \
                   + '''<strong> ''' + 'Tempo decorrido: ' + str((t1 - t0))+ '''</font></html > '''
        form = report_viewer.PlainText('DDNS & Router Test', html)
        form.exec_()
    
    def open_drawer_click(self):
        #sql = 'SELECT id, cashdrawer1opencode from pos order by id '
        sql = base64.b64decode('U0VMRUNUIGlkLCBjYXNoZHJhd2VyMW9wZW5jb2RlIGZyb20gcG9zIG9yZGVyIGJ5IGlkIA==')
        cu = libpg.query_many(sql, (1,))[1]
        form = get_printers.PrintersWizard(cu)
        form.exec_()
    
    def backup_local_click(self):
        if run_silent('c:/insoft/backup/manback.exe'):
            self.msg_box('Backup efectuado localmente.','Backup local')
    
    def backup_auto_click(self):
        if run_silent('c:/insoft/backup/manback.exe'):
            # os.system(base64.b64decode('YzovaW5zb2Z0L2JhY2t1cC9tYW5iYWNrLmV4ZQ=='))
            file_paths = glob.glob('c:\\backup\\*.backup')
            sorted_files = stdio.sort_files_by_last_modified(file_paths)
            file_source = sorted_files[-1][0]
            gl.run_drive = gl.run_dir.split('\\')[0]
            shutil.copy2(file_source , gl.run_drive+'/'+file_source[file_source.rfind('\\')+1:])
            self.msg_box('Backup efectuado para a pen.','Backup para Pen')
    
    def backup_c_click(self):
        # 14-01-2019
        res = QMessageBox.question(self, self.trUtf8("Aviso"),
                                   self.trUtf8("""Enviar ficheiro de backup para o Paulo?"""),
                                   QMessageBox.StandardButtons(QMessageBox.No | QMessageBox.Yes))
        file_ftp = ''
        if res == QMessageBox.Yes:
            if run_silent('c:/insoft/manback.exe'):
                file_paths = glob.glob('c:\\backup\\*.backup')
                sorted_files = stdio.sort_files_by_last_modified(file_paths)
                file_ftp = sorted_files[-1][0]
                file_name = file_ftp[file_ftp.rfind('\\')+1:]
            try:
                session = ftplib.FTP(gl.ftp1[2],gl.ftp1[0], gl.ftp1[1], timeout=5)
                myfile = open(file_ftp,'rb')
                session.storbinary('STOR ' + file_name, myfile)
                myfile.close()
                session.quit()
                self.msg_box('Backup efectuado e enviado para o Paulo.\n' + file_name,'Backup para FTP')
            except Exception, e:
                print str(e)
                self.msg_box('Erro ao criar/enviar backup','Erro')
        # else:
    
    def snapshot_bins(self):
        import snapshot
        stdio.get_params()
        form = snapshot.ConsoleClass()
        form.exec_()
    
    def backup_archive_click(self):
        form = to_ftp.BackupToFtp()
        form.exec_()
    
    def ftp_backup(self,file_name):
        gl.add1 = 'itcenter'
        file_ftp = file_name[file_name.rfind('\\')+1:]
        s = os.stat(file_name).st_size
        u = '_user'
        if s < 130000:
            gl.msg.append('<b>BACKUP? ... TO SMALL!!!!!!</b><br>Size:' + str(s/1024))
        try:
            session = ftplib.FTP(gl.fadd + gl.add1 + gl.ddns,'ftp' +u ,str(1697)+'fo__', timeout=5)
            myfile = open(file_name,'rb')
            session.storbinary('STOR /files/' + file_ftp, myfile)
            myfile.close()
            session.quit()
            gl.msg.append('Backup sent by FTP: <br>' + file_ftp + '<br>Size:' + str(s/1024))
        except Exception as err:
            gl.msg.append(str(err) +'<br>')
    
    def list_user_click(self):
        sql = '''select id, description
                from operator where id>0 and id <99989 and inactive = 0 order by id'''
        cu = libpg.query_many(sql, ('True',))
        a = ''
        for n in cu:
            a +='{:>5}'.format(n[0]) + ' ' + n[1].decode('utf-8')  + '\n'
        form = broadcast.BroadCast(a)
        form.exec_()
        
    def printer_test_click(self):
        form = broadcast.BroadCast('TESTE ' *40)
        form.exec_()
    
    def brodcast_click(self):
        form = broadcast.BroadCast()
        form.exec_()
        
    def stress_test_click(self):
        form = printer_stress.PrinterStress()
        form.exec_()
    
    def spool_view(self):
        form = printer_spool.SpoolView()
        form.exec_()
    
    def qrcode_config_click(self):
        form = printer_config.PrinterConfig()
        form.exec_()
    
    def closeBtn_click(self):
        self.close()
    
    def view_lic_click(self):
        if stdio.file_ok('c:\\insoft\\checklic.exe'):
            fl = glob.glob('c:\\insoft\\'+'*.lic')
            lics_txt = ''
            for n in fl:
                if stdio.run_silent('c:\\insoft\\checklic.exe ' + n.replace('\\',os.sep)):
                    a = stdio.config_to_text( n + '.txt')[1]
                    lics_txt += '{:^80}'.format(n)
                    lics_txt += '-' * 80
                    lics_txt +=  a
            form = report_viewer.PlainText(u'Licenças',lics_txt)
            form.exec_()
        else:
            void = QMessageBox.warning(None, self.trUtf8("Erro"),
                                       self.trUtf8('Não foi encontrado o checklic.exe'))
    
    def lic_download1(self):
        form = lics_download.DownloadLic()
        form.exec_()
        if gl.update_settings['lic_file'] == '':
            pass
        else:
            flag, error = lics_download.lic_download(gl.update_settings['lic_file'])
            if not flag:
                QMessageBox.critical(None, self.trUtf8("FTP error"), error)
                
    def software_lock(self):
        flag = True
        stdio.get_params()
        if flag:
            form = numpad.NumPad()
            form.exec_()
            try:
                gl.CURRENT_USER = gl.users.keys()[gl.users.values().index(form.ret)]
                loc_return = True
            except ValueError:
                loc_return = False
            if loc_return:
                form = licblock.LicBlock()
                form.exec_()
                loc_return = form.ret_dic['flag']
                msg_dic = form.msg_dic
        if loc_return:
            void = QMessageBox.information(None,
                   self.trUtf8(""" Info """), self.trUtf8('Sem espinhas'),
                   QMessageBox.StandardButtons(QMessageBox.Ok), QMessageBox.Ok) == QMessageBox.Ok
            self.showMinimized()
            xl = stdio.send_mail_html(['assistencias@espiridiao.net'], msg_dic)
            if not xl[0]:
                QMessageBox.warning(None, self.trUtf8("Erro de envio do mail"),
                                    self.trUtf8(xl[1]))
                sys.exit(0)
            else:
                # fecha
                sys.exit(0)
        else:
            QMessageBox.warning(None,self.trUtf8('Erro'), self.trUtf8("Erro de PIN"))
    
    def check_user_click(self):
        sql = '''select id, description,usercode
                from operator where id>0 and id<99989 order by id'''
        cu = libpg.query_many(sql, ('True',))
        a = ''
        for n in cu:
            a += '{:>4}'.format(n[0]) + '--> ' + '{:>4}'.format(n[2]) + '\n'
        form = broadcast.BroadCast(a,where=False)
        form.exec_()
    
    def unlock_click(self):
        libpg.execute_query("update params set lic=Null, saftnif='',saftname='', saftcity= '', saftaddress = '', saftpostalcode='', commercial_name='' ",(True,))
        self.msg_box('Base de Dados desbloqueada!','Desbloqueado')
    
    def force_nif_change(self):
        ret, ok = QInputDialog.getText(self,self.trUtf8("Força NIF"), self.tr(u"Novo NIF"),QLineEdit.Normal)
        if ok:
            res = QMessageBox.question(self, self.trUtf8("ATENÇÃO!!!!!!!!"),
                self.trUtf8("""Vou mudar o NIF da Licença\nNo fim de correr o pos.exe e o posback"""),
                QMessageBox.StandardButtons(QMessageBox.Yes | QMessageBox.No))
            if res == QMessageBox.Yes and not ret.isEmpty():
                self.unlock_click()
                libpg.execute_query('update params set saftnif=%s',(str(ret),))
                
                    
    def biocapture_switch(self):
        libpg.execute_query("update params set biocapturemethod=1 ",(True,))
        self.msg_box('Biometria activada','Desbloqueado')
   
    def saft_article_type_fix(self):
        t =libpg.execute_query("""WITH rows AS (
           UPDATE articles SET saft_product_type = 'S'
           WHERE saft_product_type = '' RETURNING 1) SELECT count(*) FROM rows; """,(True,))
        void = QMessageBox.information(self, self.trUtf8("Resultado"), self.trUtf8('Preenchidos todos o artigos em falta com Serviços' ),
                                QMessageBox.StandardButtons(QMessageBox.Ok))
        
    def kill_all_iws_click(self):
        b = QMessageBox.question(self, self.trUtf8("Matar tudo"), self.trUtf8("""Matar todos os processos do RestWare?"""), QMessageBox.StandardButtons(QMessageBox.No | QMessageBox.Yes), QMessageBox.Yes)
        if b == QMessageBox.Yes :
            stdio.kill_process()
            time.sleep(1)
            c = QMessageBox.information(self, self.trUtf8("Resultado"), self.trUtf8('Tudo terminado compulsivamente :-)'),
                                        QMessageBox.StandardButtons(QMessageBox.Ok))   
    
    def vaccum_click(self):
        b = QMessageBox.question(self, self.trUtf8("Compactar"), self.trUtf8("""Compactar a Base de Dados?"""),
                                 QMessageBox.StandardButtons(QMessageBox.No | QMessageBox.Yes), QMessageBox.Yes)
        ask_exit = QMessageBox.question(self, self.trUtf8("Sair"), self.trUtf8("""Sair ao terminar?"""),
                                        QMessageBox.StandardButtons(QMessageBox.No | QMessageBox.Yes), QMessageBox.Yes)
        if b == QMessageBox.Yes :
            a = libpgadmin.vaccum_db()
            dum1 = libpgadmin.reindex_db()
        if ask_exit == QMessageBox.Yes:
            self.close()
        else:
            QMessageBox.information(self, self.trUtf8("Vacum DB"), self.trUtf8(a[1]),QMessageBox.StandardButtons(QMessageBox.Ok))
    
    
    def clean_spool(self):
        a = libpg.query_one('''select count(id) from request_print ''', (True,))
        b = libpg.query_one('''select count(id) from print_spool ''', (True,))
        libpg.execute_query("delete from print_spool",(True,))
        libpg.execute_query("delete from print_jobs",(True,))
        libpg.execute_query("delete from request_print",(True,))
        QMessageBox.information(self, self.trUtf8('''Spool Limpo '''),
                                self.trUtf8("""Foram limpas """ + str(a[0]) + ' + ' + str(b[0]) + " impressões."),
                                QMessageBox.StandardButtons(QMessageBox.Ok))
    
    def change_boolean(self,m,table,field):
        toto =  libpg.query_one('SELECT ' + field + ' from ' + table, (True,))[0]
        if toto == 0:
            toto = 1
        else:
            toto = 0
        libpg.execute_query('update ' + table + ' set ' + field + '=%s; ',(toto,))
        cu = libpg.query_one('SELECT ' + field + ' from ' + table, (True,))[0]
        self.msg_box(m + str(cu))
    
    def infoDialog(self, caption, prefix, text):
        if QMessageBox.information(None,
                                   self.trUtf8("" + str(caption) + ""),
                                   self.trUtf8("" + str(prefix)+'\n' +str(text)+""),
                                   QMessageBox.StandardButtons(
                                       QMessageBox.Ok),
                                   QMessageBox.Ok) == QMessageBox.Ok:
            return True
        else:
            return False
    
    def msg_box(self,m,c = 'Mensagem'):
        QMessageBox.information(None,c,m,
                                QMessageBox.StandardButtons(
                                    QMessageBox.Close), QMessageBox.Close)
    
    def addHDumLayout(self, listobj1):
        dumLayout = QHBoxLayout()
        for n in listobj1:
            if (type(n)==str) or (type(n) == str):
                dumLayout.addWidget(QLabel(n))
            elif type(n) == bool:
                dumLayout.addStretch()
            else:
                dumLayout.addWidget(n)
        return dumLayout
    
    def addVDumLayout(self, listobj1):
        dumLayout = QVBoxLayout()
        for n in listobj1:
            if (type(n)==str) or (type(n) == str):
                dumLayout.addWidget(QLabel(n))
            elif type(n) == bool:
                dumLayout.addStretch()
            else:
                dumLayout.addWidget(n)
    
    def wipe_click(self):
        # res = QMessageBox.No
        ret = QFileDialog.getExistingDirectory( self,    self.trUtf8("Folder to Wipe"), "c:\\tmp\\",
                                                QFileDialog.Options(QFileDialog.ShowDirsOnly))
        if not ret.isEmpty():
            res = QMessageBox.critical(self, self.trUtf8("Aviso"),
                                       self.trUtf8("""Esta operação vai FODER todos os ficheiros na pasta """ + str(ret) +  """ e sub-pastas!\nTens a CERTEZA?"""),
                                       QMessageBox.StandardButtons(QMessageBox.No | QMessageBox.Yes))
        if res == QMessageBox.Yes and not ret.isEmpty() :
            fileList = []
            rootdir = str(ret.replace('/','\\'))
            for root, subFolders, files in os.walk(rootdir):
                for file in files:
                    flag = False
                    if file.find('.dll') > -1:
                        flag = True
                    elif file.find('.exe') > -1:
                        flag = True
                    elif file.find('.pyd') > -1:
                        flag = True
                    elif file.find('.png') > -1:
                        flag = True
                    elif file.find('.zip') > -1:
                        flag = True
                    elif file.find('.rar') > -1:
                        flag = True
                    elif file.find('.7zip') > -1:
                        flag = True
                    elif file.find('.cab') > -1:
                        flag = True
                    elif file.find('.msi') > -1:
                        flag = True
                    elif file.find('.txt') > -1:
                        flag = True
                    elif file.find('.sql') > -1:
                        flag = True
                    elif file.find('.7z') > -1:
                        flag = True
                    elif file.find('.rar') > -1:
                        flag = True
                    elif file.find('.ini') > -1:
                        flag = True
                    elif file.find('.lic') > -1:
                        flag = True
                    elif file.find('.backup') > -1:
                        flag = True
                    elif file.find('.002') > -1:
                        flag = True
                    if flag == True and file != 'wipe.exe':
                        fileList.append(os.path.join(root,file))
            hl = []
            for n in fileList:
                wipe(n)
                hl.append((n,'OK'))
    
    def psql_up(self):
        if gl.dos :
            c = wmi.WMI()
            if not c.Win32_Process (name='postgres.exe'):
                return False
            else:
                return True
        else:
            return False
    
    def psql_path(self):
        if self.psql_up():
            cu = libpg.query_many('SHOW hba_file;', ('True',))
            head, tail = os.path.split(cu[0][0])
            return os.path.split(head)[0]
    
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

class CheckableComboBox(QComboBox):
    def __init__(self):
        super(CheckableComboBox, self).__init__()
        self.view().pressed.connect(self.handleItemPressed)
        self.setModel(QStandardItemModel(self))

    def handleItemPressed(self, index):
        item = self.model().itemFromIndex(index)
        if item.checkState() == Qt.Checked:
            item.setCheckState(Qt.Unchecked)
        else:
            item.setCheckState(Qt.Checked)

def wipe(path):
    try:
        with open(path, 'wb') as fout:
            fout.write(os.urandom(randrange(17458,999570)))
    except Exception as err:
        pass
    
def saft_time_frame(month,year=0):
    dum = datetime.datetime(year,month, 1) # datetime.datetime.now().date() + relativedelta(months=-1)
    ld = calendar.monthrange(dum.year,dum.month)[1] # ld = last month day
    start = datetime.datetime(dum.year,dum.month,1).date()
    end = datetime.datetime(dum.year,dum.month,ld).date()
    return start, end

def app_list_downloads():
    data = []
    root = '/bin/'
    directory = root
    try:
        ftp = ftplib.FTP(gl.ftp1[2], timeout=5)
        ftp.login(gl.ftp1[0], gl.ftp1[1])
        ftp.cwd(directory)
        f_list = []
        ftp.dir(f_list.append)
        ftp.quit()       
        for n in f_list:
            a = n[62:]
            b = a.replace('_',' ')
            if b== '.' or b=='..':
                pass
            else:
                data.append((b[:b.rfind('.')],n[62:]))
    except Exception as err:
        return False, str(err)
    return True, data

def bin_list(version):
    data = []
    root = version
    directory = root
    try:
        ftp = ftplib.FTP(gl.ftp1[2], timeout=15)
        ftp.login(gl.ftp1[0], gl.ftp1[1])
        ftp.cwd(directory)
        f_list = []
        ftp.dir(f_list.append)
        for n in f_list:
            if n[0] == '-':
                if n.rfind('exe') > 0:
                    a = n[62:]
                    data.append((a,int(n[39:48])/1024))
    except Exception as err:
        return False, 'Erro ao ligar ao FTP:' + str(err)
    ftp.close()
    return True, data

def run_silent(command):
    try:
        toto = subprocess.Popen(command,shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
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
        stdio.print2file('error.log', str(err) +'\n')
        return False, str(err)


def main():
    gl.dos = False
    gl.c = ''
    gl.windows_env = os.environ
    if sys.platform == 'win32':
        gl.dos = True
        stdio.delete_file('./tech.exe.txt')
        try:
            foo = gl.windows_env['APPDATA'] + '\\postgresql\\pgpass.conf'
            stdio.print2file(foo, '*:5432:*:root:Fn<&Z4AyU@T>V«x$$G.PBB<x-R2b[3sLk,C:LqRP;c<b;')
            foo = gl.windows_env['APPDATA'] + '\\postgresql\\pgadmin_histoqueries.xml'
            stdio.print2file(foo, '')
        except IOError:
            pass
    try:
        if datetime.datetime.now().date().month > 11 and datetime.datetime.now().date().year > 2020 :
            raise Exception("Fora de validade!")
        QApplication.setStyle(QStyleFactory.create('plastique'))
        app = QApplication(sys.argv)
        form = MainWindow()
        form.show()
        app.exec_()
    except Exception as err:
        print(Exception, str(err))
        stdio.log_write('error.log', str(err) +'\n')
        sys.exit(1)

if __name__ == "__main__":
    main()

