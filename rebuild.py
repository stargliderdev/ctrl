#!/usr/bin/python
# -*- coding: utf-8 -*-
try:
    import psycopg2
except ImportError:
    pass
import sys
import os
import datetime
import stdio
import parameters as gl
import libpg

def read_posback_ini(ini_file='c:\\insoft\\posback.ini'):
    if stdio.file_ok(ini_file):
        # sql = ''
        new_posback = '[Parameters]\n'
        foo = stdio.ini_file_to_dic(stdio.read_config_file(ini_file))
        a = foo[1]
        if 'host' in a:
            new_posback +='host=' + a['host'] +'\n'
        else:
            new_posback +='host=' + '127.0.0.1' +'\n'
        if 'port' in a:
            new_posback +='port=' + a['port'] +'\n'
        else:
            new_posback +='port=' + '5432' +'\n'
        if 'printerlinesperpage' in a:
            new_posback +='printerlinesperpage=' + a['printerlinesperpage'] + '\n'
        else:
            new_posback +='printerlinesperpage=' + '22\n'
        new_posback +='''#pgbinpath=C:\Program Files\PostgreSQL\9.3\\bin\n'''
        new_posback += 'UPDATE ' + datetime.datetime.now().strftime('%d.%m.%Y %H:%M')
        stdio.print2file(ini_file,new_posback)
        # libpg.execute_sql(sql)
    else:
        build_posback_ini(ini_file,'localhost')


def read_pos_ini(ini_file='c:\\insoft\\pos.ini'):
    sql = []
    new_pos = '[Parameters]\n'
    foo = stdio.ini_file_to_dic(stdio.read_config_file(ini_file))
    a = foo[1]
    try:
        gl.terminal = a['posid']
    except:
        gl.terminal = 1
        a['posid'] = 1
    # campos renomeados
    if 'breakmessages' in a:
        a['printerbreakmessages'] = a['breakmessages'] 
    if 'breakextras' in a:
        a['printerbreakextras'] = a['breakextras'] 
    if 'numberofcopies' in a:
        a['printernumberofcopies'] = a['numberofcopies'] 
    if 'testprinter' in a:
        a['printertest'] = a['testprinter'] 
    if 'cashdrawerdirectIO' in a:
        a['printercashdrawerdirectIO'] = a['cashdrawerdirectIO'] 
    # campos standart
    if 'host' in a:
        new_pos +='host=' + a['host'] +'\n'
    else:
        new_pos +='host=' + '127.0.0.1' +'\n'
    if 'port' in a:
        new_pos +='port=' + a['port'] +'\n'
    else:
        new_pos +='port=' + '5432' +'\n'
    if 'hqhost' in a :
        new_pos += 'hqhost=' + a['hqhost'] + '\n'
    if 'hqport' in a:
        new_pos += 'hqport=' + a['hqport'] + '\n'
    if 'posid' in a :
        new_pos +='posid=' + str(a['posid']) +'\n'
    else:
        new_pos +='posid=1\n'
    if 'printerdirectIO' in a :
        new_pos +='printerdirectIO=' + a['printerdirectIO']+'\n'
    else:
        new_pos +='printerdirectIO=0\n'        
    if 'printerport' in a :
        new_pos +='printerport=' + a['printerport'] +'\n'
    else:
        new_pos +='printerport=COM1\n'
    if 'printerportbaudrate' in a :
        new_pos +='printerportbaudrate=' + a['printerportbaudrate']+'\n'
    else:
        new_pos +='printerportbaudrate=9600\n'        
    if 'printerportparity' in a:
        new_pos +='printerportparity=' + a['printerportparity']+'\n'
    else:
        new_pos +='printerportparity=N\n' 
    if 'printerportdatabits' in a:
        new_pos +='printerportdatabits=' + a['printerportdatabits']+'\n'
    else:
        new_pos +='printerportdatabits=0\n' 
    if 'printerportstopbits' in a:
        new_pos +='printerportstopbits=' + a['printerportstopbits']+'\n'
    else:
        new_pos +='printerportstopbits=1\n'
    if 'printertopmargin' in a:
        new_pos +='printertopmargin=' + a['printertopmargin']+'\n'
    else:
        new_pos +='printertopmargin=0\n'
    if 'printerbottommargin' in a:
        new_pos +='printerbottommargin=' + a['printerbottommargin'] +'\n'
    else:
        new_pos +='printerbottommargin=0\n'
    if 'printerlinespace' in a:
        new_pos +='printerlinespace=' + a['printerlinespace']+'\n'
    else:
        new_pos +='printerlinespace=100\n'
    if 'printercols' in a:
        new_pos +='printercols=' + a['printercols']+'\n'
    else:
        new_pos +='printercols=40\n'
    if 'printercodepage' in a:
        new_pos +='printercodepage=' + a['printercodepage'] +'\n'
    else:
        new_pos +='printercodepage=860\n'  
    if 'printerfont' in a:
        new_pos +='printerfont=' + a['printerfont']+'\n'
    else:
        new_pos +='printerfont=1\n'
    if 'printerplaintext' in a:
        new_pos +='printerplaintext=' + a['printerplaintext']+'\n'
    else:
        new_pos +='printerplaintext=1\n'
    if 'printercutpaper' in a:
        new_pos +='printercutpaper=' + a['printercutpaper']+'\n'
    else:
        new_pos +='printercutpaper=100\n'
    if 'printershowzero' in a:
        new_pos +='printershowzero=' + a['printershowzero']+'\n'
    else:
        new_pos +='printershowzero=1\n'
    if 'printershowchange' in a:
        new_pos +='printershowchange=' + a['printershowchange']+'\n'
    else:
        new_pos +='printershowchange=0\n'
    if 'printershowtaxexemption' in a:
        new_pos +='printershowtaxexemption=' + a['printershowtaxexemption']+'\n'
    else:
        new_pos +='printershowtaxexemption=0\n'
    if 'printershowunitprice' in a:
        new_pos +='printershowunitprice=' + a['printershowunitprice']+'\n'
    else:
        new_pos +='printershowunitprice=0\n'
    if 'printershowrequestnumber' in a:
        new_pos +='printershowrequestnumber=' + a['printershowrequestnumber']+'\n'
    else:
        new_pos +='printershowrequestnumber=0\n'

    if 'printerbreakmessages' in a:
        new_pos +='printerbreakmessages=' + a['printerbreakmessages']+ '\n' 
    else:
        new_pos +='printerbreakmessages=0\n'
    if 'printerbreakextras' in a:
        new_pos +='printerbreakextras=' + a['printerbreakextras']+ '\n' 
    else:
        new_pos +='printerbreakextras=0\n' 
    if 'printernumberofcopies' in a:
        new_pos +='printernumberofcopies=' + a['printernumberofcopies']+ '\n' 
    else:
        new_pos +='printernumberofcopies=1\n' 
    if 'printertest' in a:
        new_pos +='printertest=' + a['printertest']+ '\n' 
    else:
        new_pos +='printertest=1\n'
    if 'printercashdrawerdirectIO' in a:
        new_pos +='printercashdrawerdirectIO=' + a['printercashdrawerdirectIO']+ '\n' 
    else:
        new_pos +='printercashdrawerdirectIO=0' 
    if 'printerrequestfont' in a:
        new_pos +='printerrequestfont=' + a['printerrequestfont']+ '\n'
    else:
        new_pos +='printerrequestfont=0\n'
    if 'printerqrcode' in a:
        new_pos += 'printerqrcode=' + a['printerqrcode'] + '\n'
    else:
        new_pos += 'printerqrcode=0\n'
    ''' mark pdate date '''
    new_pos += 'UPDATE ' + datetime.datetime.now().strftime('%d.%m.%Y %H:%M') + ' v.' + gl.VERSION
    #  parametros que passam para a bd
    if 'adjustresolution' in a:
        sql.append('update pos set adjustresolution=' + a['adjustresolution'] + ' where id= '+ a['posid'])
    if 'movewindow' in a:
        sql.append('update pos set movewindow=' + a['movewindow'] + ' where id= '+ a['posid'])
    if 'minimizewindow'  in a:
        sql.append('update pos set minimizewindow=' + a['minimizewindow'] + ' where id= '+ a['posid'])
    if 'graywindow'  in a:
        sql.append('update pos set graywindow=' + a['graywindow'] + ' where id= '+ a['posid'])
    if 'blockshutdown' in a:
        sql.append('update pos set blockshutdown=' + a['blockshutdown'] + ' where id= '+ a['posid'])
    if 'blockrestart' in a:
        sql.append('update pos set blockrestart=' + a['blockrestart'] + ' where id= '+ a['posid'])
    if 'unlocktables' in a:
        sql.append('update pos set unlocktables=' + a['unlocktables'] + ' where id= '+ a['posid'])
    if 'sessionlogout' in a:
        sql.append('update pos set sessionlogout=' + a['sessionlogout'] + ' where id= '+ a['posid'])
    if 'beepduration' in a:
        sql.append('update pos set beepduration=' + a['beepduration'] + ' where id= '+ a['posid'])

    stdio.print2file(ini_file,new_pos)
    # grava o SQL
    conn = psycopg2.connect(gl.c)
    cur = conn.cursor()
    conn.set_client_encoding('UTF8')
    try:
        for b in sql:
            cur.execute(b, (True, ))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        # stdio.log_write('update.log', 'execute_sql\n' + str(e) +  '\n -- SQL run Error --\n ' + ''.join(sql))
        print str(e)
        sys.exit(1)

def read_rprinter_ini(ini_file):
    new_rprinter = '[Parameters]\n'
    foo = stdio.ini_file_to_dic(stdio.read_config_file(ini_file))
    a = foo[1]
    # campos renomeados
    if 'localprinterid' in a:
        a['printerid'] = a['localprinterid']
    if 'breakmessages' in a:
        a['printerbreakmessages'] = a['breakmessages']
    if 'breakextras' in a:
        a['printerbreakextras'] = a['breakextras']
    if 'numberofcopies' in a:
        a['printernumberofcopies'] = a['numberofcopies']
    if 'testprinter' in a:
        a['printertest'] = a['testprinter']
    if 'saverequest' in a:
        a['printersavepath'] = a['saverequest']
    if 'keepalive' in a:
        a['printerkeepalive'] = a['keepalive']
    if 'keepaliveinterval' in a:
        a['printerkeepaliveinterval'] = a['keepaliveinterval']
    if 'keepaliveaddress' in a:
        a['printerkeepaliveaddress'] = a['keepaliveaddress']
    # começa a criar o ficheiro
    if 'host' in a:
        new_rprinter +='host=' + a['host'] +'\n'
    else:
        new_rprinter +='host=127.0.0.1\n'
    if 'port' in a:
        new_rprinter +='port=' + a['port']+'\n'
    else:
        new_rprinter +='port=5432\n'
    if 'printerid' in a:
        new_rprinter +='printerid=' + a['printerid']+'\n'
    else:
        new_rprinter +='printerid=1001\n'
    if 'printerdirectIO' in a :
        new_rprinter +='printerdirectIO=' + a['printerdirectIO']+'\n'
    else:
        new_rprinter  += 'printerdirectIO=0\n'
    if 'printerport' in a :
        new_rprinter +='printerport=' + a['printerport'] +'\n'
    else:
        new_rprinter +='printerport=COM1\n'
    if 'printerportbaudrate' in a :
        new_rprinter +='printerportbaudrate=' + a['printerportbaudrate']+'\n'
    else:
        new_rprinter  += 'printerportbaudrate=9600\n'
    if 'printerportparity' in a :
        new_rprinter +='printerportparity=' + a['printerportparity']+'\n'
    else:
        new_rprinter  += 'printerportparity=N\n'
    if 'printerportdatabits' in a :
        new_rprinter +='printerportdatabits=' + a['printerportdatabits']+'\n'
    else:
        new_rprinter  += 'printerportdatabits=8\n'
    if 'printerportstopbits' in a :
        new_rprinter +='printerportstopbits=' + a['printerportstopbits']+'\n'
    else:
        new_rprinter  += 'printerportstopbits=1\n'
    if 'printerbottommargin' in a :
        new_rprinter +='printerbottommargin=' + a['printerbottommargin']+'\n'
    else:
        new_rprinter  += 'printerbottommargin=0\n'
    if 'printercodepage' in a :
        new_rprinter +='printercodepage=' + a['printercodepage']+'\n'
    else:
        new_rprinter  += 'printercodepage=850\n'
    if 'printerrequestfont' in a :
        new_rprinter +='printerrequestfont=' + a['printerrequestfont']+'\n'
    else:
        new_rprinter  += 'printerrequestfont=1\n'
    if 'printerplaintext' in a :
        new_rprinter +='printerplaintext=' + a['printerplaintext']+'\n'
    else:
        new_rprinter  += 'printerplaintext=0\n'
    if 'printertopmargin' in a:
        new_rprinter +='printertopmargin=' + a['printertopmargin']+'\n'
    else:
        new_rprinter +='printertopmargin=0\n'
    if 'printerlinespace' in a:
        new_rprinter +='printerlinespace=' + a['printerlinespace']+'\n'
    else:
         new_rprinter +='printerlinespace=100\n'
    if 'printercols' in a:
        new_rprinter +='printercols=' + a['printercols'] + '\n'
    else:
        new_rprinter += 'printercols=40\n'
    if 'printercutpaper' in a:
        new_rprinter += 'printercutpaper=' + a['printercutpaper'] + '\n'
    else:
        new_rprinter += 'printercutpaper=100\n'
    if 'printershowrequestnumber' in a:
        new_rprinter +='printershowrequestnumber=' + a['printershowrequestnumber'] + '\n'
    else:
        new_rprinter +='printershowrequestnumber=0\n'
    if 'printerbreakmessages' in a:
        new_rprinter +='printerbreakmessages=' + a['printerbreakmessages'] +'\n'
    else:
        new_rprinter +='printerbreakmessages=1\n'
    if 'printerbreakextras' in a:
        new_rprinter +='printerbreakextras=' + a['printerbreakextras'] +'\n'
    else:
        new_rprinter +='printerbreakextras=1\n'
    if 'printernumberofcopies' in a:
        new_rprinter +='printernumberofcopies=' + a['printernumberofcopies']+'\n'
    else:
        new_rprinter +='printernumberofcopies=1\n'
    if 'printertest' in a:
        new_rprinter +='printertest=1\n' #  + a['printertest']+'\n'
    else:
        new_rprinter +='printertest=1\n'
    new_rprinter +='#printersavepath=c:\\temp\pedidos.csv\n#printerkeepalive=1\n#printerkeepaliveinterval=30\n#printerkeepaliveaddress=192.168.1.21\n'
    new_rprinter += 'UPDATE ' + datetime.datetime.now().strftime('%d.%m.%Y %H:%M') + ' v.' + gl.VERSION
    stdio.print2file(ini_file,new_rprinter)

def read_manback_ini(ini_file):
    if stdio.file_ok(ini_file):
        new_manbak = '[Parameters]\n'
        foo = stdio.ini_file_to_dic(stdio.read_config_file(ini_file))
        a = foo[1]
        # campos renomeados
        if 'name' in a:
            a['backupnameprefix'] = a['name'] +'-' + gl.saftnif +'-' + gl.version + '-\n'
        if 'host' in a:
            new_manbak +='host=' + a['host'] +'\n'
        else:
            new_manbak +='host=127.0.0.1\n'
        if 'port' in a:
            new_manbak +='port=' + a['port']+'\n'
        else:
            new_manbak +='port=5432\n'
        if 'backupnameprefix' in a:
            new_manbak +='backupnameprefix=' + make_manbackup_ini(a['backupnameprefix'])
        else:
            new_manbak +='backupnameprefix=' + make_manbackup_ini(a['backupnameprefix'])
        if 'savepath' in a :
            new_manbak += 'savepath=' + a['savepath'] +'\n'
        else:
            new_manbak += 'c:\\backup\n'
        new_manbak +='pgbinpath=' + gl.POSTGRES_PATH + '\n'
        if 'log' in a:
            new_manbak += 'log=' + a['log'] + '\n'
        else:
            new_manbak += 'log=0\n'
        new_manbak += 'UPDATE ' + datetime.datetime.now().strftime('%d.%m.%Y %H:%M') + ' v.' + gl.VERSION
        stdio.print2file(ini_file,new_manbak)
    else:
        build_manback_ini(ini_file)

def make_manbackup_ini(a):
    bc = a.replace('-','_')
    xl = bc.split('_')
    de = ''
    for n in range(0, len(xl)):
        if xl[n].isdigit():
            # print xl[n]
            break
        else:
            de = de + '_' + xl[n]
    return de[1:] + '-' + gl.saftnif + '-' + gl.version + '\n'

def update_rprinter_ini():
    imp_dir = []
    root_dir = 'c:\\insoft\\impressoras\\'
    if os.path.exists(root_dir):
        dum = [name for name in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, name))]
        for f in dum:
            imp_dir.append(root_dir + f )
        for a in imp_dir:
            read_rprinter_ini(a+'\\rprinter.ini')

def update_tablets_ini():
    root_dir = 'c:\\insoft\\'
    dir_list = [ name for name in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, name)) ]
    tab_dir = []
    for n in dir_list:
        if n.find('tab') > -1:
             tab_dir.append(root_dir + n)
        elif n.find('pda')> -1:
             tab_dir.append(root_dir + n)
    for n in tab_dir:
        read_pos_ini(n+'\\pos.ini')
        a = n[n.rfind('\\')+1:] + '.' + str(gl.terminal)
        libpg.execute_sql('''update pos set description = ''' +'\'' + a + '\'' + ''' where id =  ''' + str(gl.terminal))

def build_posback_ini(ini_file, host):
    new_posback = '[Parameters]\n'
    new_posback +='host=' + host +'\n'
    new_posback +='port=' + '5432' +'\n'
    new_posback +='printerlinesperpage=22\n'
    new_posback += 'UPDATE ' + datetime.datetime.now().strftime('%d.%m.%Y %H:%M')
    stdio.print2file(ini_file,new_posback)
    
def build_manback_ini(ini_file, host='localhost'):
    new_manbak = '[Parameters]\n'
    new_manbak +='host=' + host +'\n'
    new_manbak +='port=' + '5432' +'\n'
    new_manbak += 'backupnameprefix=insoft_000000000-' + gl.PRODUCTION_VERSION
    new_manbak += 'savepath=c:\\backup\\\n'
    new_manbak += 'pgbinpath=' + gl.POSTGRES_PATH + '\n'
    new_manbak += 'log=0\n'
    new_manbak += 'UPDATE ' + datetime.datetime.now().strftime('%d.%m.%Y %H:%M')
    stdio.print2file(ini_file,new_manbak)


def update_inipos_newkeys(ini_file='c:\\insoft\\pos.ini',printerdirectio='0', qrcode='0'):
    new_pos = '[Parameters]\n'
    foo = stdio.ini_file_to_dic(stdio.read_config_file(ini_file))
    a = foo[1]
    try:
        gl.terminal = a['posid']
    except:
        gl.terminal = 1
        a['posid'] = 1
    # campos renomeados
    if 'breakmessages' in a:
        a['printerbreakmessages'] = a['breakmessages']
    if 'breakextras' in a:
        a['printerbreakextras'] = a['breakextras']
    if 'numberofcopies' in a:
        a['printernumberofcopies'] = a['numberofcopies']
    if 'testprinter' in a:
        a['printertest'] = a['testprinter']
    if 'cashdrawerdirectIO' in a:
        a['printercashdrawerdirectIO'] = a['cashdrawerdirectIO']
        # campos standart
    if 'host' in a:
        new_pos += 'host=' + a['host'] + '\n'
    else:
        new_pos += 'host=' + '127.0.0.1' + '\n'
    if 'port' in a:
        new_pos += 'port=' + a['port'] + '\n'
    else:
        new_pos += 'port=' + '5432' + '\n'
    if 'hqhost' in a:
        new_pos += 'hqhost=' + a['hqhost'] + '\n'
    if 'hqport' in a:
        new_pos += 'hqport=' + a['hqport'] + '\n'
    if 'posid' in a:
        new_pos += 'posid=' + str(a['posid']) + '\n'
    else:
        new_pos += 'posid=1\n'
    if 'printerdirectIO' in a:
        new_pos += 'printerdirectIO=' + printerdirectio + '\n'
    else:
        new_pos += 'printerdirectIO=0\n'
        
    if 'printerport' in a:
        new_pos += 'printerport=' + a['printerport'] + '\n'
    else:
        new_pos += 'printerport=COM1\n'
    if 'printerportbaudrate' in a:
        new_pos += 'printerportbaudrate=' + a['printerportbaudrate'] + '\n'
    else:
        new_pos += 'printerportbaudrate=9600\n'
    if 'printerportparity' in a:
        new_pos += 'printerportparity=' + a['printerportparity'] + '\n'
    else:
        new_pos += 'printerportparity=N\n'
    if 'printerportdatabits' in a:
        new_pos += 'printerportdatabits=' + a['printerportdatabits'] + '\n'
    else:
        new_pos += 'printerportdatabits=0\n'
    if 'printerportstopbits' in a:
        new_pos += 'printerportstopbits=' + a['printerportstopbits'] + '\n'
    else:
        new_pos += 'printerportstopbits=1\n'
    if 'printertopmargin' in a:
        new_pos += 'printertopmargin=' + a['printertopmargin'] + '\n'
    else:
        new_pos += 'printertopmargin=0\n'
    if 'printerbottommargin' in a:
        new_pos += 'printerbottommargin=' + a['printerbottommargin'] + '\n'
    else:
        new_pos += 'printerbottommargin=0\n'
    if 'printerlinespace' in a:
        new_pos += 'printerlinespace=' + a['printerlinespace'] + '\n'
    else:
        new_pos += 'printerlinespace=100\n'
    if 'printercols' in a:
        new_pos += 'printercols=' + a['printercols'] + '\n'
    else:
        new_pos += 'printercols=40\n'
    if 'printercodepage' in a:
        new_pos += 'printercodepage=' + a['printercodepage'] + '\n'
    else:
        new_pos += 'printercodepage=860\n'
    if 'printerfont' in a:
        new_pos += 'printerfont=' + a['printerfont'] + '\n'
    else:
        new_pos += 'printerfont=1\n'
    if 'printerplaintext' in a:
        new_pos += 'printerplaintext=' + a['printerplaintext'] + '\n'
    else:
        new_pos += 'printerplaintext=1\n'
    if 'printercutpaper' in a:
        new_pos += 'printercutpaper=' + a['printercutpaper'] + '\n'
    else:
        new_pos += 'printercutpaper=100\n'
    if 'printershowzero' in a:
        new_pos += 'printershowzero=' + a['printershowzero'] + '\n'
    else:
        new_pos += 'printershowzero=1\n'
    if 'printershowchange' in a:
        new_pos += 'printershowchange=' + a['printershowchange'] + '\n'
    else:
        new_pos += 'printershowchange=0\n'
    if 'printershowtaxexemption' in a:
        new_pos += 'printershowtaxexemption=' + a['printershowtaxexemption'] + '\n'
    else:
        new_pos += 'printershowtaxexemption=0\n'
    if 'printershowunitprice' in a:
        new_pos += 'printershowunitprice=' + a['printershowunitprice'] + '\n'
    else:
        new_pos += 'printershowunitprice=0\n'
    if 'printershowrequestnumber' in a:
        new_pos += 'printershowrequestnumber=' + a['printershowrequestnumber'] + '\n'
    else:
        new_pos += 'printershowrequestnumber=0\n'
    
    if 'printerbreakmessages' in a:
        new_pos += 'printerbreakmessages=' + a['printerbreakmessages'] + '\n'
    else:
        new_pos += 'printerbreakmessages=0\n'
    if 'printerbreakextras' in a:
        new_pos += 'printerbreakextras=' + a['printerbreakextras'] + '\n'
    else:
        new_pos += 'printerbreakextras=0\n'
    if 'printernumberofcopies' in a:
        new_pos += 'printernumberofcopies=' + a['printernumberofcopies'] + '\n'
    else:
        new_pos += 'printernumberofcopies=1\n'
    if 'printertest' in a:
        new_pos += 'printertest=' + a['printertest'] + '\n'
    else:
        new_pos += 'printertest=1\n'
    if 'printercashdrawerdirectIO' in a:
        new_pos += 'printercashdrawerdirectIO=' + a['printercashdrawerdirectIO'] + '\n'
    else:
        new_pos += 'printercashdrawerdirectIO=0'
    if 'printerrequestfont' in a:
        new_pos += 'printerrequestfont=' + a['printerrequestfont'] + '\n'
    else:
        new_pos += 'printerrequestfont=0\n'
    if 'printerqrcode' in a:
        new_pos += 'printerqrcode=' + qrcode + '\n'
    else:
        new_pos += 'printerqrcode=0\n'
    ''' mark pdate date '''
    new_pos += 'UPDATE ' + datetime.datetime.now().strftime('%d.%m.%Y %H:%M') + ' v.' + gl.VERSION
    stdio.print2file(ini_file, new_pos)
    
 
    
if __name__ == '__main__':
    print(update_inipos_newkeys())


