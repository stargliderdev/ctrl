#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
from random import randrange

import libpg
import parameters as pa

def print_report(texto,printers=[1],print_random=False):
    random_id = randrange(100000,199999)
    request_id_text = ''
    if print_random:
        request_id_text = '\n# ' + str(random_id)
    for printer_id in printers:
        sql = '''INSERT INTO request_print(id,linenum,table_sectors_id,table_id, pos_id, operator_id,date_time_stamp, articles_id, articles_description,quant,message,printer_id )
        VALUES(%s,1,1,1,1,9999,%s,1,%s,1,%s,%s)'''
        data =(random_id,datetime.datetime.now().strftime('%Y.%m.%d_%H%M%S'),'Mensagem do Sistema ' + \
            str(pa.msg_c),unicode(texto).encode('utf-8') + request_id_text ,printer_id)
        libpg.execute_query(sql,data)
        libpg.execute_query('INSERT INTO print_jobs(printer_id,job_type,date_time_stamp) VALUES (%s,\'R\',%s)',
             (printer_id,datetime.datetime.now().strftime('%Y.%m.%d_%H%M%S')))
    return random_id
# TODO erro na linha 18 com acentos
if __name__ == '__main__':
    print('SO')