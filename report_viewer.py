# -*- coding: utf-8 -*-
from PyQt4.QtCore import Qt,SIGNAL
from PyQt4.QtGui import QDialog, QPrintPreviewDialog, QPushButton, QPrinter, QTextBrowser, QVBoxLayout, QTableWidget, \
    QFont, QPlainTextEdit, QPalette, QBrush, QColor
import ex_grid
class BrowserView(QDialog):
    def __init__(self, title, html, w=700, h=500, parent = None):
        """ mostra uma variavel contendo html num browser """
        super(BrowserView,  self).__init__(parent)
        # if size == 0:
        #
        # elif size == 1:
        #     self.resize(700, 500)
        # elif size == 2:
        #     self.resize(400,300)
        # elif size == 3:
        #     self.resize(1024,768)
        self.resize(w,h)
        self.setWindowTitle(title) 
        self.browserWebView = QTextBrowser(self)
        layout = QVBoxLayout()
        layout.addWidget(self.browserWebView)
        self.close_btn = QPushButton('Fecha')
        self.close_btn.setFocus()
        self.connect(self.close_btn, SIGNAL("clicked()"), self.close_click)
        layout.addWidget(self.close_btn)
        self.setLayout(layout)
        self.impressor=QPrinter()
        self.dialogo=QPrintPreviewDialog()
        # self.browserWebView.setHtml(html.decode('utf-8'))
        self.browserWebView.setHtml(html)
        
    
    def close_click(self):
        self.close()
    # def previaImpressao(self,arg):
    #     self.dialogo.exec_()

class TableView(QDialog):
    def __init__(self, title, dataset, size = 1,ini=True, parent = None):
        super(TableView,  self).__init__(parent)

        if size == 1:
            self.resize(700, 500)
        elif size == 2:
            self.resize(400,300)
        elif size == 3:
            self.resize(1024,768)

        self.setWindowTitle(title)
        masterLayout = QVBoxLayout(self)
        self.grid = QTableWidget()
        self.grid.setSelectionBehavior(QTableWidget.SelectRows)
        self.grid.setSelectionMode(QTableWidget.SingleSelection)
        self.grid.setEditTriggers(QTableWidget.NoEditTriggers)
        self.grid.verticalHeader().setDefaultSectionSize(22)
        self.grid.verticalHeader().setVisible(False)
        self.grid.setColumnCount(4)
        self.grid.setRowCount(len(dataset))
        if ini:
            ex_grid.ex_grid_ini(self.grid, dataset)
        else:
            ex_grid.ex_grid_info(self.grid,dataset)
        self.grid.setAlternatingRowColors(True)
        self.grid.setStyleSheet("""alternate-background-color: #e6f2ff;font-family: arial, helvetica, sans-serif;""")
        self.grid.resizeColumnsToContents()
        # siteUrl = QUrl(website)
        masterLayout.addWidget(self.grid)
        close_btn = QPushButton('Fecha')
        self.connect(close_btn, SIGNAL("clicked()"), self.close_click)
        masterLayout.addWidget(close_btn)

    def close_click(self):
        self.close()

class PlainText(QDialog):
    def __init__(self,title, text, parent=None):
        super(PlainText,  self).__init__(parent)
        self.setWindowTitle(title)
        self.resize(700, 500)
        mainLayout = QVBoxLayout(self)
        palette = QPalette()
        brush = QBrush(QColor(0, 255, 0))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Text, brush)
        brush = QBrush(QColor(0, 0, 0))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Base, brush)
        brush = QBrush(QColor(0, 255, 0))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive, QPalette.Text, brush)
        brush = QBrush(QColor(0, 0, 0))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive, QPalette.Base, brush)
        brush = QBrush(QColor(165, 164, 164))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.Text, brush)
        brush = QBrush(QColor(244, 244, 244))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.Base, brush)
        font = QFont('courier new', 10)
        font.setWeight(80)
        font.setBold(False)
        self.mensagem = QPlainTextEdit()
        self.mensagem.setPalette(palette)
        self.mensagem.setFont(font)
        self.mensagem.setReadOnly(True)
        self.mensagem.setFont(font)
        self.mensagem.setPlainText(text)
        mainLayout.addWidget(self.mensagem)
        self.closeBtn = QPushButton('Sair')
        # self.closeBtn.setMinimumHeight(50)
        self.connect(self.closeBtn, SIGNAL("clicked()"), self.closeBtn_click)
        mainLayout.addWidget(self.closeBtn)
    
    def closeBtn_click(self):
        self.close()

if __name__ == '__main__':
    pass