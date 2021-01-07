#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
try:
    import psycopg2
except ImportError:
    pass

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import parameters as pa
import stdio
import dbmain
import ex_grid
import libpgadmin
import libpg

class InsideSql(QDialog):
    def __init__(self,  parent = None):
        super(InsideSql, self).__init__(parent)
        self.resize(1000, 730)
        self.fields = []
        self.setWindowTitle('Dentro de ficheiros')
        masterLayout = QVBoxLayout(self)

        self.run_sqlBtn = QPushButton('Run')
        self.connect(self.run_sqlBtn, SIGNAL("clicked()"), self.run_sql_click)
        self.statusEdit = QLabel()
        self.exit_Btn = QPushButton('Exit')
        masterLayout.addLayout(self.addHDumLayout([self.run_sqlBtn, True, self.statusEdit,self.exit_Btn]))

        workLayout = QHBoxLayout()

        self.tablesList = QListWidget()
        self.tablesList.setMaximumWidth(140)
        self.connect(self.tablesList, SIGNAL("itemDoubleClicked(QListWidgetItem*)"), self.table_list_click)

        workLayout.addWidget(self.tablesList)

        sql_Layout = QVBoxLayout()
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
        self.sqlText = QTextEdit()
        self.sqlText.setPalette(palette)
        self.sqlText.setFont(font)
        self.sqlText.setMaximumHeight(200)

        # self.tabuladorTabWidget = QTabWidget()
        self.make_grid_tab()
        # self.tabuladorTabWidget.addTab(self.tab1, 'Dados')
        # self.make_info_tab()
        # self.tabuladorTabWidget.addTab(self.tab2, 'Info')

        exportCSVBtn = QPushButton('To CSV')
        self.connect(exportCSVBtn, SIGNAL("clicked()"), self.export_to_csv)
        exportTxtBtn = QPushButton('To TXT')
        self.connect(exportTxtBtn, SIGNAL("clicked()"), self.export_to_txt)
        sql_Layout.addLayout(self.addHDumLayout([exportCSVBtn, exportTxtBtn]))
        sql_Layout.addLayout(self.addVDumLayout([self.sqlText]))
        # sql_Layout.addWidget(self.tabuladorTabWidget)
        sql_Layout.addWidget(self.grid)
        workLayout.addLayout(sql_Layout)

        masterLayout.addLayout(workLayout)
        
        self.connect(self.exit_Btn, SIGNAL("clicked()"), self.exit_click)
        self.set_vars()
        self.update_tables()

    def make_grid_tab(self):
        # self.tab1 = QWidget()
        mainTabLayout = QVBoxLayout() #self.tab1)
        tabLayout = QVBoxLayout()
        self.grid = QTableWidget()
        self.grid.setSelectionBehavior(QTableWidget.SelectRows)
        self.grid.setSelectionMode(QTableWidget.ExtendedSelection)
        self.grid.setEditTriggers(QTableWidget.NoEditTriggers)
        self.grid.verticalHeader().setDefaultSectionSize(20)
        self.grid.setAlternatingRowColors (True)
        self.grid.verticalHeader().setVisible(False)
        self.grid.resizeColumnsToContents()
        # tabLayout.addWidget(self.grid)
        mainTabLayout.addWidget(self.grid)

    def make_info_tab(self):
        self.tab2 = QWidget()
        mainTabLayout = QVBoxLayout(self.tab2)
        tabLayout = QVBoxLayout()
        self.info_tableText = QTextEdit()

        tabLayout.addWidget(self.info_tableText)
        mainTabLayout.addLayout(tabLayout)

    def user_change_click(self, idx):
        libpg.make_default(idx)
        # testa a password e dá erro se não for valida
        r = libpg.check_alive()
        if r[0]:
            pass
        else:
            errorMessage=QErrorMessage(self)
            errorMessage.showMessage(r[1])

    def export_to_csv(self):
        try:
            table_name =  str(self.tablesList.currentItem().text())
            file_name = QFileDialog.getSaveFileName(self, "Export Table","c:\\tmp\\" +  table_name + '.csv' ,"CSV (*.csv)")
            if file_name != "":
                sql = '''COPY (select * from ''' +  table_name + ''' ) TO \'''' + str(file_name) + '''\'  DELIMITER ';' CSV HEADER;'''
                dbmain.execute_query(sql, (True,))
        except AttributeError:
            pass

    def export_to_txt(self):
        try:
            table_name =  str(self.tablesList.currentItem().text())
            file_name = QFileDialog.getSaveFileName(self, "Export Table","c:\\tmp\\" +  table_name + '.txt' ,"TEXT (*.txt")
            if file_name != "":
                sql = '''COPY (select * from ''' +  table_name + ''' ) TO \'''' + str(file_name) + '''\'  DELIMITER '|';'''
                dbmain.execute_query(sql, (True,))
        except AttributeError:
            pass


    def exit_click(self):
        self.close()

    def goto_sql_click(self, txt):
        a = self.sql_indexCombo.currentIndex()
        if a > 0:
            if a == 1:
                self.sqlText.setPlainText('SELECT datname, pid, usename, application_name, client_addr, query FROM pg_stat_activity;')
            elif a == 2:
                self.sqlText.setPlainText('SELECT client_addr, state_change, query FROM pg_stat_activity;')
            self.run_sql_click()

    def refresh_info(self):
        div_title = '''<div style="margin-bottom: 10px; margin-left: 10px;"><h3 class='round_title'>'''
        div_end = '''</h3></div>\n'''
        div_label = '''<div style="margin-bottom: 10px; margin-left: 10px;"><h3 class='round_conner'>'''
        div_value = '''<h3 class="round_small">'''
        toto = '''<!DOCTYPE html><html lang="pt_pt"><head><meta charset="utf-8">
                    <style> .round_conner {color:#000000; font:14px verdana,sans-serif; display: inline; background:#56C5EA;
                    height: 25px; border-radius: 7px; padding-left:10px; padding-right:10px; padding-bottom:3px; padding-top:2px;
                    text-align:right; } .round_title {color:#000000; font:19px verdana,sans-serif; background:#56C5EA; height: 25px;
                    border-radius: 7px; padding-left:10px; padding-right:10px; padding-bottom:3px; padding-top:2px; text-align:center;
                    } .round_small {color:#FFDF00; font:14px verdana,sans-serif; display: inline; background:#6F4E37;6F4E37 height: 25px;
                    border-radius: 4px; padding-left:10px; padding-right:10px; padding-bottom:3px; padding-top:2px; text-align:right;
                    } .round_tags {color:#ffffff; font:10px verdana,sans-serif; display: inline; background:#6FD000; height: 25px;
                    border-radius: 4px; padding-left:10px; padding-right:10px; padding-bottom:3px; padding-top:2px; text-align:right;
                    } .terminal {color:#00DD00; font:14px verdana,sans-serif; background-color:#000000; border-radius: 6px; padding-left:10px;
                    padding-right:10px; padding-bottom:4px; padding-top:2px; text-align:left; } #label { border: solid #CCC 1.0pt; text-align: center;
                    font-family: Verdana; font-size: 10px; color: #333; font-weight: bold; vertical-align: middle; height: 20px; } </style>
                    </head>'''
        td_caixa= '<tr><td style="color: #000080 ; font-family:Verdana; font-size:14px">'
        td_data = '<td id="label">'
        td_end = '</td></tr>\n'
        toto += ''' <table>'''

        for n in self.fields:
            toto += td_caixa + n[0] + '</td>' + td_data + n[1] + td_end
        toto += '</table>\n</html>'
        # stdio.print2file('f.html', toto)
        self.info_tableText.setText(toto)

    def set_edit_mode_click(self):
        self.edit_mode = not(self.edit_mode)
        if self.edit_mode == True:
            self.grid.setSelectionMode(QTableWidget.SingleSelection)
            self.grid.setEditTriggers(QTableWidget.AllEditTriggers)
            self.connect(self.grid,  SIGNAL("itemChanged(QTableWidgetItem*)"), self.cell_update)
        else:
            self.grid.setSelectionMode(QTableWidget.ExtendedSelection)
            self.grid.setEditTriggers(QTableWidget.NoEditTriggers)
            self.disconnect(self.grid,  SIGNAL("itemChanged(QTableWidgetItem*)"), self.cell_update)

    def vacuum_click(self):
        self.sqlText.setPlainText(libpgadmin.vaccum_db()[1])
        self.sqlText.appendPlainText(libpgadmin.reindex_db()[1])

    def cell_update(self):
        value = self.grid.currentItem().text() #.encode('utf-8')
        id = self.grid.item(self.grid.currentRow(), 0).text() #
        sql = 'update ' +  self.table_name + ' set ' + str(self.grid.horizontalHeaderItem(self.grid.currentColumn()).text()) + ' = %s  where id = %s'
        data = (self.format_value(value), str(id))
        dbmain.execute_query(sql, data)

    def cp_macros_click(self):
        macro_id = self.macrosCombo.currentIndex()
        if macro_id == 0:
            self.sqlText.clear()
            self.sqlText.setPlainText('''CREATE DATABASE insoft
                   WITH OWNER = root
            ENCODING = 'UTF8'
            TABLESPACE = pg_default
            LC_COLLATE = 'Portuguese_Portugal.1252'
            LC_CTYPE = 'Portuguese_Portugal.1252'
            CONNECTION LIMIT = -1;\nBuildind database''')
            self.sqlText.setPlainText(libpgadmin.create_database_insoft()[1])

        elif macro_id == 1:
            reply = QMessageBox.question(self, "Re-indexar DB",
                    "Faço o Vacuum e a re-indexação?",
                    QMessageBox.No | QMessageBox.Yes )
            if reply == QMessageBox.Yes:
                self.sqlText.setPlainText('Re-indexando a Base de dados\n pode demorar algum tempo')
                self.sqlText.repaint()
                self.sqlText.setPlainText(libpgadmin.vaccum_db()[1])
                self.sqlText.appendPlainText(libpgadmin.reindex_db()[1])

    def run_sql_click(self):
        self.fields = []
        self.edit_mode = True
        self.set_edit_mode_click()
        sql = str(self.sqlText.toPlainText()).encode('utf-8')
        self.grid.setRowCount(0)
        if sql.split()[0].lower() == 'select'.lower():
            dataset = self.sql_query(sql)           
            if dataset[0] :
                if dataset[1] > 0 :
                    conn = psycopg2.connect(pa.c)
                    curs = conn.cursor()
                    curs.execute(sql)
                    curs.close()
                    columns = {}
                    c_col = 0
                    for n in curs.description:
                        columns[c_col] = [n[0], self.query_field_type(n[1]) ]
                        # self.fields.append([n['column_name'], n['data_type']])
                        c_col +=1
                    ex_grid.ex_grid_update(self.grid, columns, dataset[1], nulls = True)
                    self.grid.resizeColumnsToContents()
                    self.statusEdit.setText('columns:' + str(c_col -1) +' rows:' + str(len(dataset[1])))
                    # self.refresh_info()
                else: # há um erro
                    self.grid_on_cell()
                    item = QTableWidgetItem()
                    item.setTextAlignment(Qt.AlignTop|Qt.AlignLeft)
                    item.setText(dataset[1])
                    self.grid.setItem(0, 0, item)
            else: # há um erro
                self.grid_on_cell()
                item = QTableWidgetItem()
                item.setTextAlignment(Qt.AlignTop|Qt.AlignLeft)
                item.setText(dataset[1])
                self.grid.setItem(0, 0, item)
        else:
            t0 = time.time()
            toto = self.sql_execute(sql)
            self.grid_on_cell()
            item = QTableWidgetItem()
            item.setTextAlignment(Qt.AlignTop|Qt.AlignLeft)
            if toto[0]:
                if toto[1] == False:
                    item.setText(toto[1])
                    self.grid.setItem(0, 0, item)
                    # self.sql_indexCombo.addItem(sql)
                else:
                    t1 = time.time()
                    a = 'Tempo decorrido: ' + stdio.seconds_to_hours(t1-t0)
                    item.setText(a)
                    self.grid.setItem(0, 0, item)
            else:
                item.setText(toto[1])
                self.grid.setItem(0, 0, item)

    def sql_query(self, sql,  data = (True, )):
        try:
            conn = psycopg2.connect(pa.c)
            cur = conn.cursor()
            conn.set_client_encoding('UTF8')
            cur.execute(sql, data)
            hl = cur.fetchall()
            if len(hl) > 0:
                return True, hl
            return True, [('Sem dados','')]
        except Exception as e:
            return False, 'SQL Execute SQL Error\n' + str(e) +  sql + str(data)

    def sql_execute(self, sql):
        try:
            conn = psycopg2.connect(pa.c)
            cur = conn.cursor()
            conn.set_client_encoding('UTF8')
            cur.execute(sql, (True,))
            cur.close()
            conn.commit()
            return True, 'OK'
        except Exception as e:
            return False, 'SQL Error\n' + str(e) +  sql

    def query_field_type(self, b):
        if b in (23,21, 20, 1700):
            return 'i'
        elif b in (1043, 1042, 25):
            return 's'
        elif b == 1082:
            return 'dt'
        elif b == 1114:
            return 'd'
        elif b == 16:
            return 'b'
        else:
            return None

    def grid_on_cell(self):
        self.grid.clear()
        self.grid.setColumnCount(1)
        self.grid.setHorizontalHeaderLabels(['Mensagem'])
        self.grid.setRowCount(0)
        self.grid.setRowCount(1)
        self.grid.setColumnWidth(0, 600)
        self.grid.setRowHeight(0, 200)

    def table_list_click(self):
        self.fields = []
        self.grid.clear()
        self.grid.setColumnCount(0)
        self.grid.setRowCount(0)
        self.grid.repaint()
        self.edit_mode = True
        self.set_edit_mode_click()
        self.table_name = str(self.tablesList.currentItem().text())
        self.table_index = self.tables_dict[self.table_name]
        table_ask  = dbmain.get_table_data('SELECT * from ' + self.table_name + ' order by ' +  self.table_index) #[1]
        if table_ask[0]:
            dataset = table_ask[1]
            columns = {}
            c_col = 0
            for n in get_fields(self.table_name):
                columns[c_col] = [n['column_name'], self.get_control(n['data_type']) ]
                self.fields.append([n['column_name'], n['data_type']])
                c_col +=1
            ex_grid.ex_grid_update (self.grid, columns, dataset, nulls = True)
            self.grid.resizeColumnsToContents()
            self.statusEdit.setText('columns:' + str(c_col -1) +' rows:' + str(len(dataset)))
            # self.refresh_info()
        else:
            self.grid_on_cell()
            item = QTableWidgetItem()
            item.setTextAlignment(Qt.AlignTop | Qt.AlignLeft)
            item.setText('TABLE NOT FOUND')
            self.grid.setItem(0, 0, item)
            
    def update_tables(self):
        toto = []
        for key, value in self.tables_dict.items():
            toto.append(key)
        self.tablesList.addItems(toto)

    def get_control(self,data_type):
        toto = ''
        if data_type == 'boolean':
            toto = 'b'
        elif data_type == 'character varying' or data_type == 'character' :
            toto = 's'
        elif data_type == 'text':
            toto = 's'
        elif data_type == 'timestamp without time zone' or data_type == 'time without time zone' :
            toto = 'dt'
        # elif data_type == ''
        elif data_type == 'date':
            toto = 'd'
        elif data_type == 'numeric':
            toto = 'i'
        elif data_type == 'smallint':
            toto = 'i'
        elif data_type == 'bigint':
            toto = 'i'
        elif data_type == 'integer':
            toto = 'i'
        return toto

    def format_value(self, value):
        toto =value.toInt()
        if toto[1] == True:
            return str(toto[0])
        else:
            return  str(value).encode('utf-8')

    def set_vars(self):
        self.type_code_dict = {}
        self.type_code_dict[20]='i'
        self.type_code_dict[23]='i'
        self.type_code_dict[1043]='s'
        self.type_code_dict[1700]='i'
        self.type_code_dict[1114]='d'
        self.type_code_dict[1042]='s'
        self.type_code_dict[21]='i'
        self.type_code_dict[25]='s'
        self.edit_mode = False
        self.table_name = ''
        self.table_index = ''
        self.tables_dict = {'articles':'id','articles_barcode': 'articles_id', 'articles_composition': 'articles_id','articles_exclusions': 'articles_id',
            'articles_sectors':'articles_id','articles_top':'articles_id', 'articles_top_def': 'id',
            'articlescost_': 'articles_id', 'attendance_records': 'id','branches' :'id',
        'cashier':'id', 'clients': 'id', 'clients_bio':'id', 'clients_new':'name', 'config_view_receipts_selection':'id',
        'countries':'id', 'currencies':'id', 'docsequence':'doctype_id', 'doctype':'id',
        'extras_articles':'master_articles_id', 'families':'id', 'families_groups':'id', 'families_types': 'id',
        'initial_stock':'id','interface_jobs':'idserial','label_printers':'id', 'messages':'id', 'messages_articles':'articles_id',
        'monitor_slots':'monitor_id', 'monitor_slots_history':'monitor_id', 'monitor_slots_history_header':'monitor_id',
        'monitor_slots_stats':'monitor_id', 'mov_':'id', 'movcaixa_types':'id', 'movdet_':'id', 'operator':'id',
                            'operator_inclusions':'operator_id',
        'params':'id', 'payment_type':'id', 'pending_extracts':'pos_id', 'pos':'id', 'pricelist_hh':'id',
        'print_jobs':'id','print_spool':'id', 'printers':'id', 'purchases_':'id', 'purchasesdet_':'id',
        'purchasesorigin_':'id', 'report_consumption':'client_id', 'report_existing_stock':'id','report_max_stock':'id',
        'report_min_stock':'id','report_rep_stock':'id', 'report_sales':'id', 'report_sales_tax':'id',
        'request_jobs':'id', 'request_log':'id', 'request_print':'id', 'request_print_sequence':'pos_id',
        'request_sequence':'pos_id', 'request_spool':'pos_id', 'rtables':'id', 'rtables_autoload':'sectors_id',
        'rtables_autoload_formula':'sectors_id', 'rtables_cards':'id', 'rtables_mov':'table_sectors_id',
        'saft_config':'id','sectors':'id','series':'id', 'stables':'id', 'stables_mov':'stables_pos_id', 'suppliers':'id',
        'suppliers_articles':'id','suppliers_contacts':'id','table_name':'id','tax':'id', 'tax_exemption':'id',
                            'timesheets':'operator_id'}

        import collections

        self.tables_dict = collections.OrderedDict(sorted(self.tables_dict.items()))

    def addHDumLayout(self, listobj1, label_size = 120, label_align = Qt.AlignVCenter|Qt.AlignRight):
        """ v 2.0 SET2012"""
        dumLayout = QHBoxLayout()
        for n in listobj1:
            if (type(n)==str) or (type(n) == str):
                toto = QLabel(n)
                toto.setMinimumWidth(label_size)
                toto.setMaximumWidth(label_size)
                toto.setAlignment(label_align)
                dumLayout.addWidget(toto)
            elif type(n) == bool:
                dumLayout.addStretch()
            else:
                dumLayout.addWidget(n)
        return dumLayout

    def addVDumLayout(self, listobj1, label_size = 120, align = Qt.AlignVCenter|Qt.AlignRight):
        """ v 2.0 SET2012"""
        dumLayout = QVBoxLayout()
        for n in listobj1:
            if (type(n)==str) or (type(n) == str):
                toto = QLabel(n)
                toto.setMinimumWidth(label_size)
                toto.setMaximumWidth(label_size)
                toto.setAlignment(align)
                dumLayout.addWidget(toto)
            elif type(n) == bool:
                dumLayout.addStretch()
            else:

                dumLayout.addWidget(n)
        return dumLayout


def get_fields(table):
    "Retrieve field list for a given table"
    conn = psycopg2.connect(pa.c)
    cur = conn.cursor()
    conn.set_client_encoding('UTF8')
    rows = query(conn, """
        SELECT column_name, data_type,
            is_nullable,
            character_maximum_length,
            numeric_precision, numeric_precision_radix, numeric_scale,
            column_default
        FROM information_schema.columns
        WHERE table_name=%s
        ORDER BY ordinal_position""", table)
    return rows


def query(conn, sql,*args):
    "Execute a SQL query and return rows as a list of dicts"
    cur = conn.cursor()
    ret = []
    try:
        cur.execute(sql, args)
        for row in cur:
            dic = {}
            for i, value in enumerate(row):
                field = cur.description[i][0]
                dic[field] = value
            ret.append(dic)
        return ret
    finally:
        cur.close()

if __name__ == '__main__':
    pass

