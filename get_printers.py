#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import printer_codes

class PrintersWizard(QDialog):
    def __init__(self, printers,parent = None):
        super(PrintersWizard,   self).__init__(parent)
        self.setWindowTitle('Escolher Impressoras')
        self.toto = -1
        mainLayout = QVBoxLayout(self)
        mainLayout.addLayout(self.make_buttons(printers) )
        # butoes
        self.closeBtn = QPushButton('Fechar') 
        self.setSizeHeight(self.closeBtn,60)
        self.connect(self.closeBtn, SIGNAL("clicked()"), self.closeBtn_click)

        mainLayout.addWidget(self.closeBtn)

    def make_buttons(self,data):
        self.salesButtonsGroup = QButtonGroup()
        totoLayout = QHBoxLayout()
        for n in data:
            btn = QPushButton(str(n[0]))
            self.setSizes(btn, 60)
            self.salesButtonsGroup.addButton(btn, int(n[0]))
            totoLayout.addWidget(btn)
            
        self.connect(self.salesButtonsGroup, SIGNAL("buttonClicked(int)"), self.button_group_click) 
        return totoLayout

    def button_group_click(self,status_id):
        self.toto = status_id
        print('status_id',status_id)
        self.close()
        form = printer_codes.PrintersCodesWizard(status_id)
        form.exec_()
        self.close()

    def closeBtn_click(self):
        self.toto = -1
        self.close()

    def setSizes(self, object,value = 60):
        object.setMaximumHeight (value)
        object.setMinimumHeight(value)
        object.setMaximumWidth(value+20)
        object.setMinimumWidth(value)
    
    def setSizeHeight(self, object, value):
        object.setMaximumHeight(value)
        object.setMinimumHeight(value)
        

if __name__ == '__main__':
    pass