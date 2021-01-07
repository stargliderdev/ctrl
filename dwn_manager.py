#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *


class TagsInputDialog(QDialog):
    def __init__(self,  parent = None):
        super(TagsInputDialog,  self).__init__(parent)
        self.setWindowTitle('test')
        masterLayout = QVBoxLayout(self)
        self.resize(600, 400)
        
        self.dest_file_path = ['c:\\tmp','c:\\insoft']
        self.grid = QTableWidget()
        masterLayout.addWidget(self.grid)
        self.fill_table()

        btn = QPushButton('test')
        masterLayout.addWidget(btn)
        self.connect(btn, SIGNAL("clicked()"), self.run_click)
        QApplication.setStyle(QStyleFactory.create('plastique'))
    
    def run_click(self):
        for linha in range(0, self.grid.rowCount()):
                print(self.grid.cellWidget(linha, 0).layout().itemAt(1).widget().isChecked())

    def fill_table(self):
        self.grid.setSelectionBehavior(QTableWidget.SelectRows)
        self.grid.setSelectionMode(QTableWidget.SingleSelection)
        self.grid.setEditTriggers(QTableWidget.NoEditTriggers)
        self.grid.verticalHeader().setDefaultSectionSize(30)
        self.grid.setAlternatingRowColors (True)
        self.grid.verticalHeader().setVisible(False)

        self.grid.setColumnCount(3)
        self.grid.setHorizontalHeaderLabels(['','Data1','Data2'])

        line = 0
        data_set = [['pos','c:\\insoft'],['posback','c:\\insoft'],['mansaft','c:\\tmp'],['postgresql','c:\\tmp'],
        ['system','c:\\insoft'],['odbc','c:\\insoft']]
        self.grid.setRowCount(len(data_set))

        for n in data_set:
            self.grid.setCellWidget(line, 0, self.checkBoxGrid())

            item = QTableWidgetItem()
            self.grid.setItem(line, 1,item )
            item.setText(n[0])
            c = QComboBox()
            # c.setMaximumHeight(20)
            c.setEditable(True)
            c.addItems(self.dest_file_path)
            c.setEditText(n[1])
            self.grid.setCellWidget(line, 2, c)

            line +=1

        self.grid.resizeColumnsToContents()

    def checkBoxGrid(self, label = ''):
        w = QWidget()
        l = QHBoxLayout(w)
        l.setContentsMargins(0,0,0,0)
        l.addStretch()
        c = QCheckBox(label)
        l.addWidget(c)
        l.addStretch()
        return w

if __name__ == '__main__':
    pass