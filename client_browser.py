#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from PyQt4.QtCore import Qt, SIGNAL

from PyQt4.QtGui import QHBoxLayout, QVBoxLayout, QPushButton, QDialog, QApplication, QComboBox, QLineEdit, QToolButton, \
    QTableWidget, \
    QStyleFactory, QFileDialog, QIcon

import client_edit
import ex_grid
import qlib as qc 
import libpg


class ClientBrowser(QDialog):
    def __init__(self, parent=None):
        super(ClientBrowser, self).__init__(parent)
        self.resize(700, 500)
        dum = libpg.query_many('select description from doctype order by id')
        self.setWindowTitle('Navegador de Clientes')
        masterLayout = QVBoxLayout(self)
        filterLayout = QHBoxLayout()
        buttonLayout = QHBoxLayout()
        
        self.nifEdt = QLineEdit()
        self.nifEdt.setMinimumWidth(100)
        self.nifEdt.setMaximumWidth(100)
        self.nameClientEdt = QLineEdit()
        self.sortByCbx = QComboBox()
        self.sortByCbx.addItems(['Numero', 'Nome', 'NIF'])
        self.connect(self.sortByCbx, SIGNAL("currentIndexChanged(QString)"), self.run_click)
        exportCsvBtn = QToolButton()
        exportCsvBtn.setIcon(QIcon('excel.png'))
        exportCsvBtn.clicked.connect(self.export_csv)
        searchTbn = QToolButton()
        searchTbn.setIcon(QIcon('search.png'))
        searchTbn.clicked.connect(self.run_click)
        
        filterLayout.addLayout(qc.addHLayout(['NIF', self.nifEdt, 'Nome', self.nameClientEdt, self.sortByCbx,searchTbn, True, exportCsvBtn], lw=40))
        masterLayout.addLayout(filterLayout)
        self.gridClients = QTableWidget()
        self.gridClients = QTableWidget()
        self.gridClients.setSelectionBehavior(QTableWidget.SelectRows)
        self.gridClients.setSelectionMode(QTableWidget.SingleSelection)
        self.gridClients.setEditTriggers(QTableWidget.NoEditTriggers)
        self.gridClients.verticalHeader().setDefaultSectionSize(20)
        self.gridClients.setAlternatingRowColors(True)
        self.gridClients.verticalHeader().setVisible(False)
        self.gridClients.resizeColumnsToContents()
        self.gridClients.doubleClicked.connect(self.table_click)
        masterLayout.addWidget(self.gridClients)
        
        exitBtn = QPushButton('Sair')
        buttonLayout.addWidget(exitBtn)
        exitBtn.clicked.connect(self.exit_click)
        
        masterLayout.addLayout(buttonLayout)

    def run_click(self):
        filter = ''
        ord_by = ''
        filter_list = []
        if not self.nameClientEdt.text() == '':
            filter_list.append('lower(name) like \'%%' + unicode(self.nameClientEdt.text()).encode('utf-8').lower() + '%%\'')
        if not self.nifEdt.text() == '':
            filter_list.append(' nif like \'%%' + str(self.nifEdt.text()) +  '%%\'')
        if len(filter_list) >0:
            filter = 'WHERE '
            filter += ' and '.join(filter_list)
        sql = '''select id,name, address, nif, Cast(Case
            When inactive=1 Then \'Sim\'
            ELSE \'Não\' END   AS Varchar(4)) as inac   from clients '''
        sql += filter
        
        if self.sortByCbx.currentIndex() == 0:
            ord_by = 'id'
        elif self.sortByCbx.currentIndex() == 1:
            ord_by = 'name'
        if self.sortByCbx.currentIndex() == 2:
            ord_by = 'nif'
        sql += '''order by ''' + ord_by
        xl = libpg.query_many(sql)
        ex_grid.ex_grid_update(self.gridClients, {0: ['Num', 'i'],
                                                  1: ['Nome', 's'],
                                                  2: ['Morada', 's'],
                                                  3: ['NIF', 's'],
                                                  4: ['Inactivo', 's'],
                                                  }, xl)
        self.gridClients.setColumnWidth(0, 80)
        self.gridClients.setColumnWidth(1, 250)
        self.gridClients.setColumnWidth(6, 100)


    def table_click(self):
        client_id = str(self.gridClients.item(self.gridClients.currentRow(), 0).text())
        flag, di = libpg.get_record_dic('select * from clients where id = %s', (client_id,))
        form = client_edit.ClientEdit(di)
        form.exec_()
        self.run_click()
        
    
    def export_csv(self):
        file_name = QFileDialog.getSaveFileName(self, "Exporta Clientes ", "c:\\tmp\\" , "CSV (*.csv)")
        SEP = ';'
        csv = u'Lista de Clientes\n'
        if file_name != "":
            for linha in range(0, self.gridClients.rowCount()):
                csv += str(self.gridClients.item(linha, 0).text()) + SEP
                csv += '\"' + unicode(self.gridClients.item(linha, 1).text()) + '\"' + SEP
                csv += '\"' + unicode(self.gridClients.item(linha, 2).text()) + '\"' + SEP
                csv += '\"' + unicode(self.gridClients.item(linha, 3).text()) + '\"' + SEP
                csv += '\"' + unicode(self.gridClients.item(linha, 4).text()) + '\"' + SEP
                csv += '\n'
            f = open(file_name , 'w')
            f.write(csv.encode('utf8'))
            f.close()
        

    def exit_click(self):
        self.close()

def main():
    pass

if __name__ == '__main__':
    main()
