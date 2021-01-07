#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

from PyQt4.QtCore import Qt, SIGNAL
from PyQt4.QtGui import QDialog, QVBoxLayout, QComboBox,  QTextEdit, QPushButton, QApplication, QStyleFactory,  QDesktopWidget

import parameters as gl
import qlib
import qlib as qc
import rebuild
import stdio


class PrinterConfig(QDialog):
    def __init__(self, parent=None):
        super(PrinterConfig, self).__init__(parent)
        # vars
        gl.printer_conf_dict = {'BIRCH': (0, 1, 'BYOPOS 4.0', 1, 'byopos_4.0'),
                                'Toshiba A00': (1, 1, 'TOSHIBA Windows Driver\nPartilhada no Windows', 1, 'TOSHIBA'),
                                'EPSON T-20': (0, 1, 'Epson OPOS 2.8', 1, 'epson_opos_2.8'),
                                'EPSON T-20 II': (0, 1, 'Epson OPOS 2.8', 1, 'epson_opos_2.8'),
                                'EPSON T-88 III': (0, 2, 'Epson OPOS 2.8', 1, 'epson_opos_2.8')
                                }
        gl.printer_conf_models = []
        for n in gl.printer_conf_dict.keys():
            gl.printer_conf_models.append(n)
        self.resize(600, 400)
        self.center()
        self.setWindowTitle('Configura impressora para QR code')
        masterLayout = QVBoxLayout(self)
        self.printerModelCBox = QComboBox()
        self.printerModelCBox.addItems(gl.printer_conf_models)

        self.connect(self.printerModelCBox, SIGNAL("currentIndexChanged(int)"), self.model_change)
        self.printerDirectIOCBox = QComboBox()
        self.printerDirectIOCBox.addItems(['Sim',u'Não'])
        self.printerDirectIOCBox.setMaximumWidth(80)
        self.printerQrCodeCBox = QComboBox()
        self.printerQrCodeCBox.setMaximumWidth(220)
        self.printerQrCodeCBox.addItems([u'Não Imprime', 'Imprime Nativo', 'Imprime Imagem'])
        self.printerDriverLabel = QTextEdit()
        self.printerDriverLabel.setReadOnly(True)
        
        
        masterLayout.addLayout(qc.addVLayout(['Impressora',self.printerModelCBox]))
        masterLayout.addLayout(qc.addVLayout(['printerdirectIO',self.printerDirectIOCBox]))
        masterLayout.addLayout(qc.addVLayout(['QrCode',self.printerQrCodeCBox]))
        masterLayout.addWidget(self.printerDriverLabel)
        

        self.okBtn = QPushButton('Grava')
        self.okBtn.setMinimumHeight(60)
        self.okBtn.setMinimumWidth(400)
        cancelBtn = QPushButton('Sair')
        cancelBtn.setMinimumWidth(60)
        cancelBtn.setMaximumHeight(60)
        
        self.connect(self.okBtn, SIGNAL("clicked()"), self.ok_click)
        
        cancelBtn.clicked.connect(self.exit_click)
        masterLayout.addStretch()
        masterLayout.addLayout(qlib.addHLayout([self.okBtn, True, cancelBtn]))
        self.printerModelCBox.setCurrentIndex(1)

    def ok_click(self):
        rebuild.update_inipos_newkeys('c:\\insoft\pos.ini', printerdirectio=str(self.printerDirectIOCBox.currentIndex()), qrcode=str(self.printerQrCodeCBox.currentIndex()))
    
    def exit_click(self):
        self.close()
    
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def model_change(self, t):
        # print(t)
        # print(self.printerModelCBox.currentText())
        self.printerDirectIOCBox.setCurrentIndex(gl.printer_conf_dict[str(self.printerModelCBox.currentText())][0])
        self.printerQrCodeCBox.setCurrentIndex(gl.printer_conf_dict[str(self.printerModelCBox.currentText())][1])
        self.printerDriverLabel.setText(gl.printer_conf_dict[str(self.printerModelCBox.currentText())][2])

def main():
    app = QApplication(sys.argv)
    QApplication.setStyle(QStyleFactory.create('plastique'))
    form = PrinterConfig()
    form.show()
    app.exec_()


if __name__ == '__main__':

    main()


