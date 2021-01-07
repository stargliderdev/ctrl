#!/usr/bin/python
# -*- coding: utf-8 -*-
#
import os
import sys
import datetime
try:
    from dateutil.relativedelta import relativedelta
except ImportError:
    pass
import calendar
import glob

import shutil
try:
    from unidecode import unidecode
except ImportError:
    pass
import parameters as gl
import libpg
import smtpmail
import stdio

def gera_saft(start, end, mail=''):
    gl.msg = []
    # apaga o ficheiro de sucess em c:\\
    gl.running_path='c:\\tmp\\saft\\var'
    stdio.delete_file('c:\\insoft\\success.log')
    stdio.delete_file('c:\\insoft\\error.log')
    try:
        shutil.rmtree('c:\\tmp\\saft\\var\\')
    except Exception as e:
        pass
    stdio.dir_ok('c:\\tmp\\saft\\var\\')
    lic_file = 'posback.lic'
    if stdio.file_ok('c:\\insoft\\insoft.lic'):
        lic_file = 'insoft.lic'
    saft_str = gl.pos_ini['host'] +  '#' + gl.pos_ini['port'] + '#insoft' + '#c:\\insoft\\' + lic_file + '#' + start.strftime('%Y%m%d') +'#' +\
               end.strftime('%Y%m%d') + '#' + gl.running_path 
    # gera o saft
    os.system('c:\\insoft\\mansaft.exe' + ' ' + saft_str)
    
    if stdio.file_ok('c:\\insoft\\error.log'):
        gl.msg.append('Error generating SAF-T file. #37')
        if not stdio.file_ok('c:\\insoft\\' + lic_file) :
            gl.msg.append('No ' +  lic_file + ' file found. #40')
            return False
        gl.msg.append('error.log file found. #42')
        return False

    else:
        get_saft_file_name()
    
    if mail == '':
        gl.msg.append('Finish creating SAF-t file')
    else:
        gl.msg.append( 'Sending SAF-t file to: ' + gl.saft_config_dict['saft_to'])
        _zip_file = stdio.compress_file(gl.saft_file)
        gl.zip_hash = stdio.get_sha256(_zip_file)
        smtpmail.send_saft_smtp(gl.saft_config_dict['saft_to'], [_zip_file], smtpmail.make_saft_headers())
        gl.msg.append('Finish sending SAF-t file')
    return True

def get_saft_file_name():
    a = gl.running_path
    # print 'gl.running_path',gl.running_path
    fname = glob.glob(a + '\\*.xml')
    gl.saft_file = fname[0]

def saft_time_frame1(month,year=0):
    if year == 0:
        year = datetime.datetime.now().date().year
    gl.saft_config_dict.update(dict({'saft_year': year}))
    if month == 0:
        last_saft = datetime.datetime.now().date() - relativedelta(months=1)
        gl.saft_config_dict.update(dict({'saft_month': last_saft.month}))
        last_saft_day = calendar.monthrange((datetime.datetime.now().date() - relativedelta(months=1)).year,last_saft.month)[1]
        start = datetime.datetime.date(datetime.datetime(year, last_saft.month, 1))
        end =  datetime.datetime.date(datetime.datetime(year, last_saft.month, last_saft_day))
    else:
        last_saft = datetime.datetime.date(datetime.datetime(year,month,1))
        gl.saft_config_dict.update(dict({'saft_month': month}))
        last_saft_day = calendar.monthrange(year,last_saft.month)[1]
        start =  datetime.datetime.date(datetime.datetime(year, last_saft.month, 1))
        end =  datetime.datetime.date(datetime.datetime(year, last_saft.month, last_saft_day))
    return start, end

def saft_time_frame(month,year=0):
    if month == 0: # mes e ano a partir da data current
        # é o saft do mes anterior ao que estamos
        dum = datetime.datetime.now().date() + relativedelta(months=-1)
        ld = calendar.monthrange(dum.year,dum.month)[1]
        start = datetime.datetime(dum.year,dum.month,1).date()
        end = datetime.datetime(dum.year,dum.month,ld).date()
    else:
        dum = datetime.datetime(year,month, 1)
        ld = calendar.monthrange(dum.year,dum.month)[1]
        start = datetime.datetime(dum.year,dum.month,1).date()
        end = datetime.datetime(dum.year,dum.month,ld).date()
    gl.saft_config_dict.update(dict({'saft_month': start.month}))
    gl.saft_config_dict.update(dict({'saft_year': end.year}))
    return start, end

def get_unit_data():
    gl.POSTGRES_PATH = libpg.get_data_dir()[1].replace('data', 'bin')
    dum = libpg.output_query_one_dict('''SELECT saftname,
              saftaddress,
              saftpostalcode,
              saftcity,
              saftnif
              from params where id = 0''')
    try:
        gl.saft_config_dict.update(dict(dum))
    except Exception as e:
         gl.msg.append('error 201\n' + str(e))

def authorize():
    toto = False
    current = datetime.datetime.now().strftime('%Y%m')
    dum = datetime.datetime.strptime(gl.saft_config_dict['valid_until'], '%Y-%m-%d')
    valid =  dum.strftime('%Y%m')
    last_saft = gl.saft_config_dict['saft_last_send'].strftime('%Y%m')
    if int(current)  <= int(valid) : # é sempre mais um mês depois da validade se a val marca MAIO em JUNHO ainda funciona
        if int(current) -1 > int(last_saft) -1 :
            toto = True
            if  datetime.datetime.now().day >= gl.saft_config_dict['saft_day']:
                toto = True
            else:
                toto =  False
                print('no SAF-t day!')
        else:
            print('Already extracted!.')
            toto = False
    else:
        pass
    return toto

def check_files():
    d = 'c:\\insoft\\'
    a = ['checklic.exe', 'pos.exe', 'posback.lic', 'mansaft.exe']
    for n in a:
        if not stdio.file_ok(d + n):
            return False, d + n
    return True, ''

def get_lic_data(app='fo',path='c:\\insoft\\'):
    import stdio
    stdio.delete_file(path + 'success.log')
    dict = {}
    fl = ''
    if stdio.file_ok(path + 'pos_1.lic'):
        fl = 'pos_1.lic'
    else:
        if stdio.file_ok(path + 'pos.lic'):
            fl = 'pos.lic'
        else:
            if stdio.file_ok(path + 'posback.lic'):
                fl = 'posback.lic'
            else:
                if fl == '':
                    print('error: lic files not found!')
        print 'get_lic_date'
        sys.exit(154)
    os.system('c:\\insoft\\checklic.exe' + ' ' + path + fl)
    if stdio.file_ok(path + 'success.log'):
        try:
            print('file',path + fl + '.txt')
            f = open(path + fl + '.txt', "r")
            try:
                lines = f.readlines()
            finally:
                f.close()
                dict['dc'] = unidecode(lines[1].strip(' \n'))
                dict['ds'] = unidecode(lines[2].strip(' \n')) #.decode('latin-1').encode('utf-8')
                dict['morada'] = unidecode(lines[3].strip(' \n'))
                dict['cp'] =unidecode( lines[9].strip(' \n'))
                dict['localidade'] = unidecode(lines[11].strip(' \n'))
                dict['nif'] = lines[10].strip(' \n')
                dict['software'] = lines[13].split(':')[1].strip(' \n')
                dict['valid_until'] = lines[17].split(':')[1].strip(' \n')
                dict['sn'] = lines[14].split(':')[1].strip(' \n')
                if dict['valid_until'] == '':
                    dict['valid_until'] = '2050-12-31'
        except Exception as e:
            print('erro ao ler lic')
            print(str(e))
            dict['error'] = True
            sys.exit(100)
        return dict


if __name__ == '__main__':
    pass