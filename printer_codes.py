#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QHBoxLayout,QVBoxLayout, QLabel,QMessageBox,QPushButton,QDialog,QButtonGroup
import libpg


class PrintersCodesWizard(QDialog):
    def __init__(self, pos_local_printer, parent = None):
        super(PrintersCodesWizard,   self).__init__(parent)
        #self.resize(800, 600)
        self.setWindowTitle('Escolha de Drive') 
        #self.get_data()
        self.toto = pos_local_printer
        mainLayout = QVBoxLayout(self)
        self.printers_dic = {'Epson':['22+27+08+256',0],'Star':['22+27+08+256',0],'EuroSys':['44+34+566',1],'Toshiba':['88+56+54+32',1]}
        printers = [] 
        for item in self.printers_dic:
            printers.append(item)
        mainLayout.addLayout(self.make_buttons(printers))

        # butoes
        self.closeBtn = QPushButton('Fechar') 
        self.setSizeHeight(self.closeBtn,60)
        self.connect(self.closeBtn, SIGNAL("clicked()"), self.closeBtn_click)
        mainLayout.addWidget(self.closeBtn)

    def make_buttons(self,data):
        self.salesButtonsGroup = QButtonGroup()
        totoLayout = QHBoxLayout()
        c = 1
        for n in data:
            btn = QPushButton(n)
            self.setSizes(btn, 60)
            self.salesButtonsGroup.addButton(btn, c)
            totoLayout.addWidget(btn)
            c +=1
            
        self.connect(self.salesButtonsGroup, SIGNAL("buttonClicked(QAbstractButton *)"), self.button_group_click) 
        return totoLayout

    def button_group_click(self,printer_name):
        printer = self.printers_dic[str(printer_name.text())]
        self.change_code(str(printer[0]))
        QMessageBox.information(None,\
        self.trUtf8('Actualizar ini'),
        self.trUtf8('Colocar no ini: cashdrawerdirectIO=' + str(printer[1])),
        QMessageBox.StandardButtons(
        QMessageBox.Close), QMessageBox.Close)


    def code_epson_btn_click(self):
        dum = self.code_epson_btn.text().split('\n')
        self.change_code(str(dum[1]))
        self.close()
    
    def code_star_btn_click(self):
        dum = self.code_star_btn.text().split('\n')
        self.change_code(str(dum[1]))
        self.close()
    
    def code_eurosys_btn_click(self):
        dum = self.code_eurosys_btn.text().split('\n')
        self.change_code(str(dum[1]))
        self.close()

    def code_toshiba_btn_click(self):
        dum = self.code_toshiba_btn.text().split('\n')
        self.change_code(str(dum[1]))
        self.close()

    
    def closeBtn_click(self):
        self.close()

    def change_code(self,code):
        libpg.execute_query('update pos set cashdrawer1opencode = %s where id = %s',(code,self.toto))

    #-------------------------------------------------
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
