#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *



class FtpTarget(QDialog):
    def __init__(self, parent = None):
        super(FtpTarget,   self).__init__(parent)
        #self.resize(800, 600)
        
        self.setWindowTitle('Escolha do Servidor') 
        #self.get_data()
        self.toto = -1

        mainLayout = QVBoxLayout(self)
        espBtn = QPushButton('Server Esp',)
        self.setSizes(espBtn, 60)
        self.connect(espBtn, SIGNAL("clicked()"), self.espBtn_click)
        pauBtn = QPushButton('Server Pau',)
        self.setSizes(pauBtn, 60)
        self.connect(pauBtn, SIGNAL("clicked()"), self.pauBtn_click)
        mainLayout.addLayout(self.addHDumLayout([espBtn,pauBtn]))
        
        # butoes
        self.closeBtn = QPushButton('Fechar') 
        self.setSizeHeight(self.closeBtn,60)
        self.connect(self.closeBtn, SIGNAL("clicked()"), self.closeBtn_click)

        mainLayout.addWidget(self.closeBtn)

    
    def espBtn_click(self):
        self.toto =1
        self.close()
    
    def pauBtn_click(self):
        self.toto = 2
        self.close()

    def closeBtn_click(self):
        self.toto = -1
        self.close()

    def setSizes(self, object,value = 60):
        
        object.setMaximumHeight (value)
        object.setMinimumHeight(value)
        object.setMaximumWidth(value+20)
        object.setMinimumWidth(value)

    def setSizeWidth(self, object, value):
        object.setMaximumWidth(value)
        object.setMinimumWidth(value)
    
    def setSizeHeight(self, object, value):
        object.setMaximumHeight(value)
        object.setMinimumHeight(value)

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
        return dumLayout

    def parseField(self, field_name):
        # v2
        dum = self.item_data[field_name]
        if type(dum) == int:
            return str(dum)
        elif dum == None:
            return ''
        else:
            return dum.decode('utf-8')            


if __name__ == '__main__':
    pass
