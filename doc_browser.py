#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from PyQt4.QtCore import Qt, SIGNAL

from PyQt4.QtGui import QHBoxLayout, QVBoxLayout, QPushButton, QDialog, QApplication, QComboBox, QLineEdit, QToolButton, \
    QTableWidget, \
    QStyleFactory, QLabel, QIcon, QCheckBox, QFileDialog

import date_input
import ex_grid
import qlib as qc 
import parameters as gl
import libpg
import stdio


class DocumentBrowser(QDialog):
    def __init__(self, parent=None):
        super(DocumentBrowser, self).__init__(parent)
        self.resize(800, 600)
        dum = libpg.query_many('select description from doctype order by id')
        self.setWindowTitle('Todas as datas')
        gl.DOCTYPE = ['*']
        for n in dum:
            gl.DOCTYPE.append(n[0])
        self.date_ini = None
        self.date_end = None
        masterLayout = QVBoxLayout(self)
        filterLayout = QHBoxLayout()
        buttonLayout = QHBoxLayout()
        self.docTypeCbx = QComboBox()
        self.docTypeCbx.setMinimumWidth(60)
        self.docTypeCbx.setMaximumWidth(60)
        self.docTypeCbx.addItems(gl.DOCTYPE)
        self.docTypeCbx.setCurrentIndex(2)
        self.docNumEdt = QLineEdit()
        self.docNumEdt.setMinimumWidth(100)
        self.docNumEdt.setMaximumWidth(100)
        self.dateLbl = QLabel()
        self.dateLbl.setText('Todas')
        dateInputTB = QToolButton()
        dateInputTB.setIcon(QIcon('calendar.png'))
        dateInputTB.clicked.connect(self.get_dates)
        
        self.nifEdt = QLineEdit()
        self.nifEdt.setMinimumWidth(100)
        self.nifEdt.setMaximumWidth(100)
        self.valueEdt = QLineEdit()
        self.valueEdt.setMinimumWidth(80)
        self.valueEdt.setMaximumWidth(80)
        self.onlyNifChk = QCheckBox(u'Só com NIF')

        exportCsvBtn = QToolButton()
        exportCsvBtn.setIcon(QIcon('excel.png'))
        exportCsvBtn.clicked.connect(self.export_csv)
        
        searchTbn = QToolButton()
        searchTbn.setIcon(QIcon('search.png'))
        searchTbn.clicked.connect(self.run_click)
        
        filterLayout.addLayout(qc.addHLayout(['Tipo', self.docTypeCbx,'Num.', self.docNumEdt, dateInputTB, 'NIF', self.nifEdt, 'Valor', self.valueEdt,
                                              self.onlyNifChk,searchTbn, True,exportCsvBtn ], lw=40))
        masterLayout.addLayout(filterLayout)
        self.gridDocs = QTableWidget()
        self.gridDocs = QTableWidget()
        self.gridDocs.setSelectionBehavior(QTableWidget.SelectRows)
        self.gridDocs.setSelectionMode(QTableWidget.SingleSelection)
        self.gridDocs.setEditTriggers(QTableWidget.NoEditTriggers)
        self.gridDocs.verticalHeader().setDefaultSectionSize(20)
        self.gridDocs.setAlternatingRowColors(True)
        self.gridDocs.verticalHeader().setVisible(False)
        self.gridDocs.resizeColumnsToContents()
        self.gridDocs.doubleClicked.connect(self.view_detail_click)
        
        masterLayout.addWidget(self.gridDocs)
        self.gridDet = QTableWidget()
        self.gridDet = QTableWidget()
        self.gridDet.setSelectionBehavior(QTableWidget.SelectRows)
        self.gridDet.setSelectionMode(QTableWidget.SingleSelection)
        self.gridDet.setEditTriggers(QTableWidget.NoEditTriggers)
        self.gridDet.verticalHeader().setDefaultSectionSize(20)
        self.gridDet.setAlternatingRowColors(True)
        self.gridDet.verticalHeader().setVisible(False)
        self.gridDet.resizeColumnsToContents()
        masterLayout.addWidget(self.gridDet)
        exitBtn = QPushButton('Sair')
        buttonLayout.addWidget(exitBtn)
        exitBtn.clicked.connect(self.exit_click)
        
        masterLayout.addLayout(buttonLayout)

    def run_click(self):
        filter = ''
        filter_list = []
        self.gridDet.setColumnCount(0)
        
        
        if not self.date_ini is None:
            filter_list.append(' (mov_.date_time_stamp >=\'' + self.date_ini + ' 00:00:00 \' and mov_.date_time_stamp<=\'' + self.date_end + ' 23:59:59 \')'  )
        if self.onlyNifChk.isChecked():
            filter_list .append(' mov_.client_nif not like \'\' ')
        if not self.docTypeCbx.currentText() == '*':
            filter_list.append('mov_.doctype_id = (select id from doctype where description=\'' + str(self.docTypeCbx.currentText()) + '\') ')
        else:
            filter_list.append('mov_.doctype_id > 0')
        if not self.docNumEdt.text() == '':
            filter_list.append('mov_.id=' + str(self.docNumEdt.text()))

        if not self.nifEdt.text() == '':
            filter_list.append(' mov_.client_nif =\'' + str(self.nifEdt.text()) +  '\'')
        if not self.valueEdt.text() == '':
            total = str(self.valueEdt.text()).replace('.','')
            total = total.replace(',','')
            filter_list.append( ' mov_.total_value=' + total)
        if len(filter_list) >0:
            filter = 'WHERE '
            filter += ' and '.join(filter_list)
    
        sql = '''select doctype.description || ' ' || mov_.id  || '/' || mov_.series_id as fact,
                   date_time_stamp ,
                   total_value/100,
                   operator_description,
                   table_id || ':' || table_sectors_description as tbl_sect,
                   client_id,
                   client_name,
                   client_nif,
                   payment_type.description,mov_.extract_ref
            from mov_
            inner join doctype on doctype.id = mov_.doctype_id
            inner join payment_type on payment_type.id= mov_.payment_type_id '''
        sql += filter
        sql += '''order by mov_.date_time_stamp desc'''
        xl = libpg.query_many(sql)
        ex_grid.ex_grid_update(self.gridDocs, {0: ['D/N/S', 's'],
                                               1: ['Data', 'dt'],
                                               2: ['Total', 'f2'],
                                               3: ['Operador', 's'],
                                               4: ['Mesa/Sector', 's'],
                                               5: ['Cli. #', 'i'],
                                               6: ['Cliente', 's'],
                                               7: ['NIF', 's'],
                                               8: ['M. Pag.', 's'],
                                               9: ['Extracto','s']}, xl)
        self.gridDocs.setColumnWidth(0,80)
        self.gridDocs.setColumnWidth(2,60)
        self.gridDocs.setColumnWidth(7, 100)

    def view_detail_click(self):
        a = self.gridDocs.item(self.gridDocs.currentRow(), 0).text()
        a = a.split(' ')
        i = a[1].split('/')[0]
        sql = ''' select linenum, quant, artcod, artdes, tax, discount, unitprice/100, price/100
                from movdet_
                where id=%s and doctype_id=(select id from doctype where description = %s)
                order by linenum'''
        
        xl = libpg.query_many(sql, (str(i),str(a[0])))
        ex_grid.ex_grid_update(self.gridDet, {0: ['Linha', 'i'],
                                               1: ['QT', 'f2'],
                                               2: ['Code', 'i'],
                                               3: ['Artigo', 's'],
                                               4: ['IVA', 'f2'],
                                               5: ['Desc', 'f2'],
                                               6: ['UN', 'f2'],
                                               7: [u'Preço', 'f2']
                                              }, xl)
        self.gridDet.setColumnWidth(0, 50)
        self.gridDet.setColumnWidth(1, 50)
        self.gridDet.setColumnWidth(2, 70)
        self.gridDet.setColumnWidth(3, 190)
        self.gridDet.setColumnWidth(4, 55)
        self.gridDet.setColumnWidth(6, 80)
        self.gridDet.setColumnWidth(7, 80)

    def export_csv(self):
        file_name = QFileDialog.getSaveFileName(self, "Exporta Facturas ", "c:\\tmp\\" , "CSV (*.csv)")
        SEP = ';'
        csv = u'Lista de Facturas com NIF\n'
        if file_name != "":
            for linha in range(0, self.gridDocs.rowCount()):
                csv += '\"' + unicode(self.gridDocs.item(linha, 0).text()) +'\"' + SEP
                csv += '\"' + unicode(self.gridDocs.item(linha, 1).text())[0:10] + '\"' + SEP
                csv += unicode(self.gridDocs.item(linha, 2).text()) + SEP
                csv += '\"' + unicode(self.gridDocs.item(linha, 3).text()) + '\"' + SEP
                csv += '\"' + unicode(self.gridDocs.item(linha, 4).text()) + '\"' + SEP
                csv += unicode(self.gridDocs.item(linha, 5).text()) + SEP
                csv += '\"' + unicode(self.gridDocs.item(linha, 6).text()) + '\"' + SEP
                csv += '\"' + unicode(self.gridDocs.item(linha, 7).text()) + '\"' + SEP
                csv += '\"' + unicode(self.gridDocs.item(linha, 8).text()) + '\"' + SEP
                csv += '\"' +unicode(self.gridDocs.item(linha, 9).text()) + '\"' + SEP
                csv += '\n'
            f = open(file_name , 'w')
            f.write(csv.encode('utf8'))
            f.close()


    def get_dates(self):
        form = date_input.DateInput('Intervalo de Datas')
        form.exec_()
        if form.ret[0]:
            self.docNumEdt.clear()
            self.date_ini = form.ret[1].strftime('%Y-%m-%d')
            self.date_end = form.ret[2].strftime('%Y-%m-%d')
            self.setWindowTitle('Entre ' + form.ret[1].strftime('%d-%m-%Y') + ' a ' + form.ret[2].strftime('%d-%m-%Y'))

    def exit_click(self):
        self.close()

if __name__ == '__main__':
    pass
