#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys

from PyQt4.QtGui import QLineEdit, QCheckBox, QApplication, QStyleFactory, QDialog, QVBoxLayout, QPushButton, QMessageBox
from PyQt4.QtCore import Qt, SIGNAL, QSize
import libpg
import parameters as gl
import qlib


class ClientEdit(QDialog):
    def __init__(self, data_dic, parent=None):
        super(ClientEdit, self).__init__(parent)
        self.data_dic = data_dic
        self.setWindowTitle('Edita Cliente')
        masterLayout = QVBoxLayout(self)
        self.id = QLineEdit()
        self.id.setReadOnly(True)
        self.inactive = QCheckBox('Inactivo')
        masterLayout.addLayout(qlib.addHLayout(['Numero', self.id, self.inactive]))
        self.nif = QLineEdit()
        masterLayout.addLayout(qlib.addHLayout(['NIF', self.nif]))
        self.name = QLineEdit()
        masterLayout.addLayout(qlib.addHLayout(['Nome', self.name]))
        self.address = QLineEdit()
        masterLayout.addLayout(qlib.addHLayout(['Morada', self.address]))
        self.postal_code_1 = QLineEdit()
        self.postal_code_2 = QLineEdit()
        masterLayout.addLayout(qlib.addHLayout(['CP1', self.postal_code_1, self.postal_code_2]))
        self.postal_code_3 = QLineEdit()
        masterLayout.addLayout(qlib.addHLayout(['Localidade:', self.postal_code_3]))
        self.phone = QLineEdit()
        backwordBtn = QPushButton('<<')
        self.connect(backwordBtn, SIGNAL("clicked()"), self.back_click)
        forwarddBtn = QPushButton('>>')
        self.connect(forwarddBtn, SIGNAL("clicked()"), self.forw_click)
        saveBtn = QPushButton('Grava')
        self.connect(saveBtn, SIGNAL("clicked()"), self.save_click)
        cancelBtn = QPushButton('Sair')
        masterLayout.addLayout(qlib.addHLayout([backwordBtn,forwarddBtn, saveBtn, cancelBtn]))
        self.connect(cancelBtn, SIGNAL("clicked()"), self.cancel_click)
        
        masterLayout.addStretch()
        self.refresh_form()
    
    def refresh_form(self):
        self.inactive.setChecked(0)
        self.id.setText(str(self.data_dic['id']))
        self.nif.setText(self.data_dic['nif'])
        self.name.setText(self.data_dic['name'].decode('utf-8'))
        self.address.setText(self.data_dic['address'].decode('utf-8'))
        self.postal_code_1.setText(str(self.data_dic['postal_code_1']))
        self.postal_code_2.setText(str(self.data_dic['postal_code_2']))
        try:
            if self.data_dic['postal_code_3'] is None:
                self.postal_code_3.setText('')
            else:
                self.postal_code_3.setText((self.data_dic['postal_code_3']).decode('utf-8'))
        except TypeError:
            pass
        try:
            self.phone.setText(self.data_dic['phone'])
        except TypeError:
            pass
        if self.data_dic['inactive'] == 1:
            self.inactive.setChecked(True)
        else:
            pass
    
    def save_click(self):
        try:
            if self.inactive.isChecked():
                inactive = 1
            else:
                inactive = 0
            libpg.execute_query('update clients set name=%s, address=%s, postal_code_1=%s, postal_code_2=%s, postal_code_3=%s,'
                                'nif=%s, inactive=%s'
                        'where id=%s', (unicode(self.name.text()).encode('utf-8'),
                                        unicode(self.address.text()).encode('utf-8'),
                                        int(self.postal_code_1.text()),
                                        int(self.postal_code_2.text()),
                                        unicode(self.postal_code_3.text()).encode('utf-8'),
                                        str(self.nif.text()).upper(),
                                        inactive,
                                        int(self.id.text())))
    
        except ValueError:
            void = QMessageBox.information(self, self.trUtf8("Erro de entrada de dados"), self.trUtf8("""Campo interio com letra!"""),
                                           QMessageBox.StandardButtons(QMessageBox.Ok))

        
    def back_click(self):
        record = int(self.id.text()) - 1
        self.read_record(record)
        if self.data_dic is None:
            pass
        else:
            self.refresh_form()
        
    def forw_click(self):
        record = int(self.id.text()) + 1
        self.read_record(record)
        if self.data_dic is None:
            pass
        else:
            self.refresh_form()
        
    def cancel_click(self):
        self.close()

    def read_record(self,record_id):
        flag, di = libpg.get_record_dic('select * from clients where id = %s', (record_id,))
        self.data_dic = di
    

def main():
    pass


if __name__ == '__main__':
    main()
