#!/usr/bin/python
# -*- coding: utf-8 -*-
import glob
import os

try:
    import ctypes.wintypes
except:
    pass
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import shutil

import qlib
import ex_grid
import ftp_lic
import parameters as gl
import stdio

class DownloadLic(QDialog):
    def __init__(self, one = True, mode = 1, nif = -1 , parent = None):
        super(DownloadLic, self).__init__(parent)
        self.resize(760, 400)
        self.unrar = one
        self.mode = mode
        gl.update_settings['run'] = False
        self.setWindowTitle(u'Download de Licenças 1.0')
        masterLayout = QVBoxLayout(self)

        self.current_path = 'c:\\tmp\\'
        self.nif = QLineEdit()
        se_nif_Btn = QToolButton()
        se_nif_Btn.setIcon(QIcon('search.png'))
        self.connect(se_nif_Btn, SIGNAL("clicked()"), self.refresh_search)
        self.make_dir = QCheckBox('Cria Dir')
        if nif == -1:
            self.nif.setText('')
            self.get_nif = False
        else:
            self.nif.setText(str(nif))
            self.get_nif = True
        masterLayout.addLayout(qlib.addHLayout(['Contribuinte:', self.nif,se_nif_Btn,self.make_dir, True]))

        self.grid_search = QTableWidget()
        self.grid_search.setSelectionBehavior(QTableWidget.SelectRows)
        self.grid_search.setSelectionMode(QTableWidget.SingleSelection)
        self.grid_search.setEditTriggers(QTableWidget.NoEditTriggers)
        self.grid_search.verticalHeader().setDefaultSectionSize(20)
        self.grid_search.setAlternatingRowColors(True)
        self.grid_search.verticalHeader().setVisible(False)
        self.grid_search.resizeColumnsToContents()
        masterLayout.addLayout(qlib.addHLayout([self.grid_search]))

        self.download_Btn = QPushButton('Download')
        self.connect(self.download_Btn, SIGNAL("clicked()"), self.download_click)
        
        self.exit_Btn = QPushButton('Sair')
        self.connect(self.exit_Btn, SIGNAL("clicked()"), self.exit_click)
        if mode == 1:
            masterLayout.addLayout(qlib.addHLayout([self.download_Btn, self.exit_Btn]))
            self.unrar = True
            self.download_Btn.setText('Continuar')
            self.exit_Btn.setText(u'Cancelar')
            self.serverChk = QCheckBox('Servidor')
            self.serverChk.setCheckable(True)
            self.unlockCkb = QCheckBox('Un-Lock')
            self.unlockCkb.setCheckable(True)
            self.print_rpt = QCheckBox('Imprime')
            self.print_rpt.setCheckable(True)
            self.print_rpt.setChecked(True)
            self.send_mail = QCheckBox('Envia Mail')
            self.send_mail.setCheckable(True)
            self.send_mail.setChecked(True)
            self.autoExitChk = QCheckBox('Sair depois de terminar')
            self.compressChk = QCheckBox('Comprimir DB')
            self.rebootChk = QCheckBox('Reboot')
            masterLayout.addLayout(qlib.addHLayout([self.serverChk, self.unlockCkb, self.print_rpt, self.send_mail, self.autoExitChk,self.compressChk,
                                                    self.rebootChk, True]))
            masterLayout.addLayout(qlib.addHLayout([self.download_Btn,self.exit_Btn]))
        else:
            masterLayout.addLayout(qlib.addHLayout([self.download_Btn,self.exit_Btn]))
        if self.get_nif:
            self.refresh_search()
        if gl.server_data['server']:
            self.serverChk.setCheckState(2)

    def refresh_search(self):
        c = str(self.nif.text())
        if len(c) > 3:
            a = ftp_lic.get_lic(nif=c)
            if a[0] :
                b = a[1]
                ex_grid.ex_grid_update(self.grid_search, {0:['Nome', 's'], 1:['NIF', 'i'], 2:[u'Versão', 's'], 3:['Ficheiro', 's']}, b)
                self.grid_search.setColumnWidth(0,250)
            else:
                QMessageBox.information(None,
                    self.trUtf8(u'Pesquisa da Licença'.encode('utf-8')),
                    self.trUtf8(u'Licença(s) com  <br>NIF <b>'.encode('utf-8') +
                                self.nif.text() + u'</b><br> Não encontrada(s)'.encode('utf-8')) + '<br>' + a[1],
                    QMessageBox.StandardButtons(QMessageBox.Close), QMessageBox.Close)
                self.close()
        else:
            QMessageBox.information(None,
                                    self.trUtf8(u'Erro de pesquisa'),
                                    self.trUtf8(u'No minimo 3 digitos'),
                                    QMessageBox.StandardButtons(QMessageBox.Close), QMessageBox.Close)
    def download_click (self):
        gl.update_settings = {'run': True, 'server': self.serverChk.checkState(), 'unlock': self.unlockCkb.checkState(),
                              'mail': self.send_mail.checkState(), 'print': self.print_rpt.checkState(),
                              'autoexit': self.autoExitChk.checkState(), 'reboot': self.rebootChk.checkState(),
                              'lic_file':'','vaccum':self.compressChk.checkState()}
        try:
            try:
                gl.update_settings['lic_file'] = str(self.grid_search.item(self.grid_search.currentRow(), 3).text())
                if self.mode == 0:
                    QMessageBox.information(None,
                                            self.trUtf8('''Download da Licença'''),
                                            self.trUtf8('''Licença de '''+ self.grid_search.item(self.grid_search.currentRow(), 0).text()) + u'<br>Versão '+
                                            self.grid_search.item(self.grid_search.currentRow(), 2).text() + '''\n Descarregada com sucesso''',
                                            QMessageBox.StandardButtons(QMessageBox.Close), QMessageBox.Close)
                if self.unrar :
                    self.close()
            except AttributeError:
                QMessageBox.critical(None, self.trUtf8("Erro de operação"), self.trUtf8('Tens de escolher uma licença'))
                pass
        except Exception as err:
            QMessageBox.critical(None, self.trUtf8("Exception error in lics_download"), self.trUtf8(str(err)))
            gl.update_settings['run'] = False
            gl.update_settings['lic_file'] = ''
            self.exit_click()

    def exit_click (self):
        gl.update_settings = {'run':False,'server': self.serverChk.checkState(), 'unlock': self.unlockCkb.checkState(),
                             'mail':self.send_mail.checkState(),'print':self.print_rpt.checkState(),
                              'autoexit': self.autoExitChk.checkState(),'reboot':self.rebootChk.checkState()}
        self.close()

def copy_lic(lic_file):
    lic_file = lic_file.replace('/','\\')
    lic_file_name = os.path.basename(str(lic_file))
    for fl in glob.glob("c:\\tmp\\*.lic"):
        os.remove(fl)
    for fl in glob.glob("c:\\insoft\\*.lic"):
        os.remove(fl)
    for fl in glob.glob("c:\\insoft\\*.txt"):
        os.remove(fl)
    shutil.copy2(lic_file, 'c:\\tmp\\')
    stdio.run_silent("7z.exe e " + "c:\\tmp\\" + lic_file_name + " -oc:\\tmp\\")
    rootdir = 'c:\\tmp\\'
    dum = [name for name in os.listdir(rootdir) if os.path.isfile(os.path.join(rootdir, name))]
    for g in dum:
        if g.find('.lic') > -1:
            shutil.copy2(rootdir + g, 'c:\\insoft\\')

def lic_download(lic_file):
    extract_to = lic_file.replace('.rar','')
    stdio.dir_ok('c:\\tmp\\' + extract_to)
    ftp_return = ftp_lic.get_lic_ftp(lic_file, lic_file)
    if ftp_return[0]:
        if lic_file.find('rar') > -1:
            #     está compactado
            stdio.run_silent("7z.exe e " + "c:\\tmp\\" + lic_file + " -y -oc:\\tmp\\" + extract_to + "\\")
        else:
            # não está compactado
            pass
    else:
        return False, ftp_return
    return True, ''
    
def lic_clean(target_dir, lic_file, lic_paths):
    dir_to_delete = lic_file.replace('.rar', '')
    # target_dir = data_dict['target_dir']
    void = stdio.dir_ok(target_dir)
    for fl in glob.glob('c:\\tmp\\' + lic_file + "\\*.lic"):
        os.remove(fl)
    for fl in glob.glob("c:\\tmp\\*.lic"):
        os.remove(fl)
    for fl in glob.glob("c:\\tmp\\*.rar"):
        os.remove(fl)
    for n in lic_paths:
        for fl in glob.glob( n + '\\*.lic'):
            os.remove(fl)
        for fl in glob.glob(n + '\\*.txt'):
            os.remove(fl)
    try:
        shutil.rmtree('c:\\tmp\\' + dir_to_delete)
    except Exception as err:
        print('erro 200')
        pass
    
def lic_copy(lic_file, target_dir, lic_paths):
    gl.ERROR_STRING = ''
    rootdir = 'c:\\tmp\\' + lic_file.replace('.rar','') + '\\'
    void = stdio.dir_ok(target_dir)
    file_list = []
    lic_path = lic_paths
    for lics in lic_path:
        dum = [name for name in os.listdir(rootdir) if os.path.isfile(os.path.join(rootdir, name))]
        for g in dum:
            if g.find('.lic') > -1:
                file_list.append(lics + '\\' + g)
                shutil.copy2(rootdir + g, lics + '\\' + g)
    flag = True
    for n in file_list:
        a = stdio.file_ok(n)
        if a:
            pass
        else:
            flag = False
            gl.ERROR_STRING += 'ficheiro não copiado ' + target_dir + '\\' + n + '<br>'
            # print('error copying file', target_dir + n)
    return flag


def lic_files_path(target_dir, recursive = True):
    file_list = []
    auxiliaryList = []
    if recursive:
        if target_dir == 'c:\\insoft':
            file_list.append(target_dir)
        path = target_dir
        for root, dirs, files in os.walk(path):
            for file_name in files:
                if file_name.endswith(".lic"):
                    a = root.split('\\')
                    if len(a) == 2:
                        file_list.append(root)
                    elif len(a) == 3:
                        if a[2].find('impressoras') > -1:
                            file_list.append(root)
                        if a[2].find('pda') > -1:
                            file_list.append(root)
                        if a[2].find('tab') > -1:
                            file_list.append(root)
                    elif len(a) == 4:
                        file_list.append(root)
        for word in file_list:
            if word not in auxiliaryList:
                auxiliaryList.append(word)
    else:
        auxiliaryList.append(target_dir)
    return auxiliaryList

def get_lic_nif(lic_file):
    check_lic_path = os.path.dirname(lic_file+'\\')
    if stdio.file_ok(lic_file + '\\insoft.lic'):
        lic_file = lic_file + '\\insoft.lic'
    else:
        if stdio.file_ok(lic_file + '\\pos.lic'):
            lic_file = lic_file + '\\pos.lic'
        else:
            if stdio.file_ok(lic_file + '\\posback.lic'):
                lic_file = lic_file + '\\posback.lic'
    if stdio.run_silent(check_lic_path + '\\checklic.exe ' + lic_file):
        a = stdio.read_config_file(lic_file + '.txt')
        for f in a:
            c = f.find('NIFSAFT')
            if c > -1:
                return True, f.split('=')[1].strip()
        return False, -1
        
if __name__ == '__main__':
    pass
