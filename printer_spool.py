#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QVBoxLayout,QTableWidget,QPushButton,QComboBox,QDialog
import libpg
import qlib
import ex_grid

class SpoolView(QDialog):
    def __init__(self,  parent = None):
        self.local_prt = ['Todas']
        self.remote_prt = ['Todas']
        self.get_info()
        super(SpoolView, self).__init__(parent)
        self.resize(800, 400)
        # self.setWindowFlags(Qt.WindowStaysOnTopHint|Qt.WindowTitleHint)
        self.setWindowTitle('Spool das impressoras') 
        masterLayout = QVBoxLayout(self)

        self.printer_typeCb = QComboBox()
        self.printer_typeCb.addItems(['Pedidos','Contas'])
        self.connect(self.printer_typeCb, SIGNAL("currentIndexChanged(int)"), self.printer_typeCb_change)
        self.printer_Cb = QComboBox()
        self.printer_Cb.addItems(self.remote_prt)
        refreshBTN = QPushButton('refresh')
        self.connect(refreshBTN, SIGNAL("clicked()"), self.refresh_click)
        exit_Btn = QPushButton('Sair')
        self.connect(exit_Btn, SIGNAL("clicked()"), self.exit_click)
        masterLayout.addLayout(qlib.addHLayout(['Tipo', self.printer_typeCb,'Impressora', self.printer_Cb,refreshBTN,exit_Btn]))
        
        self.grd_output = QTableWidget()
        self.grd_output.setSelectionBehavior(QTableWidget.SelectRows)
        self.grd_output.setSelectionMode(QTableWidget.SingleSelection)
        self.grd_output.setEditTriggers(QTableWidget.NoEditTriggers)
        self.grd_output.verticalHeader().setDefaultSectionSize(20)
        self.grd_output.setAlternatingRowColors (True)
        self.grd_output.verticalHeader().setVisible(False)
        self.grd_output.resizeColumnsToContents()
        masterLayout.addLayout(qlib.addHLayout([self.grd_output]))

    def get_info(self):
        d = libpg.query_many('Select id, description from printers', (True,))
        self.remote_dic = {1000:'Todas'}
        if not d == []:
            self.remote_prt = ['Todas']
            for n in range(0,len(d)):
                self.remote_prt.append(d[n][1])
                self.remote_dic[d[n][1]] = d[n][0]
        p = libpg.query_many('Select id, description from pos order by id', (True,))
        self.local_prt = ['Todas']
        for n in range(0,len(p)):
            self.local_prt.append(p[n][1])

    def printer_typeCb_change(self, i):
        if i == 1:
            self.printer_Cb.clear()
            self.printer_Cb.addItems(self.local_prt)
        else:
            self.printer_Cb.clear()
            self.printer_Cb.addItems(self.remote_prt)

    def refresh_click (self):
        if self.printer_typeCb.currentIndex() == 1:
            self.refresh_local(self.printer_Cb.currentIndex())
        else:
            self.refresh_remote(self.printer_Cb.currentIndex())

    def refresh_local(self, prt_id):
        if prt_id == 0: # todas
            sql = '''select id, printer_id,doc_id, doc_name,date_time_stamp, substring(filecontents for 10),second_print,ref_doctype_id
            from print_spool
            order by date_time_stamp desc '''
        else:
            sql = '''select id, printer_id,doc_id, doc_name,date_time_stamp, substring(filecontents for 10),second_print,ref_doctype_id
            from print_spool where printer_id = %s
            order by date_time_stamp desc '''
        dataset  = libpg.query_many(sql, (prt_id,))
        ex_grid.ex_grid_update(self.grd_output, {0:['ID', 'i'], 1:['printer_id', 'i'], 2:['doc_id', 'i'], 3:['doc_name', 's'], 
            4:['date_time_stamp', 'dt'], 5:['filecontents', 's'], 6:['second_print', 'i'], 7:['ref_doctype_id', 'i']}, dataset)

    def refresh_remote(self, prt_id):
        if prt_id == 0: # todas
            # sql = '''select request_print.id ,articles_description ,printers.description,date_time_stamp,message,printer_id,quant, table_sectors_id, table_id, operator_id,
            #       status,  price,  articles_id,linenum
            #     from request_print, printers
            #     where printer_id=printers.id  order by date_time_stamp desc, linenum asc'''
            sql = '''select request_print.id ,articles_description ,
            printers.description,date_time_stamp,
            message,
            printer_id,quant, sectors.description, table_id, operator.description,
                  status,  price,  articles_id,linenum
                from request_print
                inner join printers on request_print.printer_id=printers.id
                inner join operator on operator.id= request_print.operator_id
                inner join sectors on table_sectors_id= sectors.id
                order by date_time_stamp desc, linenum desc'''
        else:
            prt_id = self.remote_dic[str(self.printer_Cb.currentText())]
            sql = '''select request_print.id ,articles_description ,
            printers.description,date_time_stamp,
            message,
            printer_id,quant, sectors.description, table_id, operator.description,
                  status,  price,  articles_id,linenum
                from request_print
                inner join printers on request_print.printer_id=printers.id
                inner join operator on operator.id= request_print.operator_id
                inner join sectors on table_sectors_id= sectors.id
                where printer_id = %s order by date_time_stamp desc, linenum asc'''
            
        dataset  = libpg.query_many(sql, (prt_id,))
        ex_grid.ex_grid_update(self.grd_output, {0:['ID', 'i'],
                                                 1:['Artigo', 's'],
                                                 2:['Impressora', 's'],
                                                 3:['Data/Hora', 'dt'],
                                                 4:['Mensagem', 's'],
                                                 5:['printer_id', 'i'],
                                                 6:['Qtd', 'i'],
                                                 7:['Sector', 's'],
                                                 8:['Mesa', 'i'],
                                                 9:['Operador', 's'],
                                                 10:['status', 'i'],
                                                 11:[u'Preço', 'i'],
                                                 12:['Num Artigo', 'i'],
                                                 13:['Linha', 'i']}, dataset)
    def exit_click (self):
        self.close()


if __name__ == '__main__':
    pass



