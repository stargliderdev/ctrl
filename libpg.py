#!/usr/bin/env python
# -*- coding: utf-8 -*-
import psycopg2
import psycopg2.extras
import re

import libpgf
import stdio
import parameters as gl

def query_one_flag(sql, data=(True,)):
    try:
        conn = psycopg2.connect(gl.c)
        cur = conn.cursor()
        conn.set_client_encoding('UTF8')
        cur.execute(sql, data)
        return True, cur.fetchone()
    
    except Exception as e:
        return False, (str(e) + '\n -- SQL Error --\n in :' + '\n' + sql)


def query_many_flag(sql, data=(True,)):
    # type: (object, object) -> object
    try:
        conn = psycopg2.connect(gl.c)
        cur = conn.cursor()
        conn.set_client_encoding('UTF8')
        cur.execute(sql, data)
        return True, cur.fetchall()
    except Exception as e:
        return False, (str(e) + '\n -- SQL Error --\n in :' + '\n' + sql)


def execute_query_flag(sql, data=(True,)):
    try:
        conn = psycopg2.connect(gl.c)
        cur = conn.cursor()
        conn.set_client_encoding('UTF8')
        cur.execute(sql, data)
        conn.commit()
        cur.close()
        conn.close()
        return True, ''
    
    except Exception as e:
        return False, str(e) + '\n -- SQL Error --\n in :' + '\n' + sql + '\n', data


def query_one(sql, data=(True,)):
    try:
        conn = psycopg2.connect(gl.c)
        cur = conn.cursor()
        conn.set_client_encoding('UTF8')
        cur.execute(sql, data)      
        xl = cur.fetchone()
        cur.close()
        conn.close()
        return xl
    except Exception as e:
         return str(e) +  '\n -- SQL Error --\n in :'  + '\n' + sql
        

def query_many(sql, data=(True,)):
    try:
        conn = psycopg2.connect(gl.c)
        cur = conn.cursor()
        # conn.set_client_encoding('UTF8')
        cur.execute(sql, data)
        xl = cur.fetchall()
        cur.close()
        conn.close()
        return xl
    except Exception as e:
        return str(e) + '---------\b\n' + sql

def execute_query(sql, data=(True,)):
    try:
        conn = psycopg2.connect(gl.c)
        cur = conn.cursor()
        conn.set_client_encoding('UTF8')
        cur.execute(sql, data)      
        conn.commit()
        cur.close()
        conn.close()
        return ''
    except Exception as e:
        print str(e) +  '\n -- SQL Error --\n in :'  + '\n' + sql + '\n', str(data)
        return str(e) +  '\n -- SQL Error --\n in :'  + '\n' + sql + '\n', str(data)


def execute_sql(sql):
    if sql.lower().find('select')> -1 :
        out = True
    else:
        out = False
    try:
        conn = psycopg2.connect(gl.c)
        cur = conn.cursor()
        conn.set_client_encoding('UTF8')
        cur.execute(sql )
        if out:
            toto = cur.fetchall()
        else:
            toto = sql + ' O.K. '
        conn.commit()
        cur.close()
        conn.close()
        return True, toto
    except Exception as e:
        return False, str(e)


def check_field(t, f):
    try:
        sql = 'SELECT attname FROM pg_attribute WHERE attrelid =(SELECT oid FROM pg_class WHERE relname = %s) AND attname = %s;'
        data = (t, f)
        conn = psycopg2.connect(gl.c)
        cur = conn.cursor()
        conn.set_client_encoding('UTF8')
        cur.execute(sql, data)
        output =  cur.fetchall()
        cur.close()
        conn.close()

        if len(output) >0:
            return True
        else:
            return False

    except Exception as e:
        # print(str(e) +  'SQL output #1 Error --\n in :' + sql)
        return False


def make_default(db): # = 1, cmd = '2013'):
    if db == 1:
        gl.pos_ini['db'] = 'insoft'
        gl.pos_ini['u'] = 'root'
    elif db == 0:
        gl.pos_ini['db'] = 'insoft'
        gl.pos_ini['u'] = 'root'
        libpgf.to_pdf()
    elif db == 2:
        gl.pos_ini['db'] = 'postgres'
        gl.pos_ini['u'] = 'postgres'
        gl.file1 = '1'
    elif db == 3:
        gl.pos_ini['db'] = 'postgres'
        gl.pos_ini['u'] = 'postgres'
    elif db == 4:
        gl.pos_ini['db'] = 'postgres'
        gl.pos_ini['u'] = 'root'
        db = 0
    gl.c = 'host=' + gl.pos_ini['host'] + ' port='+ gl.pos_ini['port'] + ' dbname=' + gl.pos_ini['db'] + ' user= ' + gl.pos_ini['u'] +' password='
    gl.c += gl.file1 #cc(db)
    gl.POSTGRES_PATH = get_data_dir()[1].replace('data', 'bin')

def cc(cmd):
        if cmd == 1:
            return stdio.alfa([6320, 7180, 4356, 5466,
                                             7611, 4253, 6699, 5064,
                                             5036, 7407, 3787, 2707,
                                             1206, 2669, 734, 6274])
        elif cmd == 0 or cmd == 3:
            # retorna a password nova 1
            return stdio.alfa([7278, 5635, 5047, 3516,
                                             2227, 7610, 2867, 7061,
                                             6783, 2916, 7815, 2534,
                                             1326, 3613, 5844, 1808,
                                             7825, 6847, 2120, 5047,
                                             2370, 3834, 734, 4699,
                                             3517, 6257, 1306, 5660,
                                             7125])
        elif cmd == 2:
            gl.file1 = '1'
            return '1'


def get_psql_version():
    toto = execute_sql('select version()')
    foo = toto[1][0][0]
    d = foo[foo.lower().find('.')-1:]
    return d[:3]

def check_alive():
    sql = '''SELECT 1 AS result FROM pg_database
          WHERE datname=\'insoft\''''
    toto = execute_sql(sql)
    if toto[0]:
        return True, 'OK'
    else:
        p = re.compile('password')
        if p.search(toto[1]):
            # chk_io()
            # make_default(2)
            return False, 'password'
        else:
            return False, toto[1]
    
def output_query_one_dict(sql):
    try:
        conn = psycopg2.connect(gl.c)
        dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)      
        dict_cur.execute(sql)
        ans1 = []
        rec = dict_cur.fetchone()
        d = {}
        for key, value in list(rec.items()) :
            d[key] = value
    except Exception as err:
        return {'erro':str(err)}
    return d

def get_record_dic(sql, id):
    # get a connection, if a connect cannot be made an exception will be raised here
    try:
        conn = psycopg2.connect(gl.c)
        dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        dict_cur.execute(sql, id)
        rec = dict_cur.fetchone()
        dict_cur.close()
        conn.close()
        return True, rec
    except Exception, e:
        conn.close()
        return False, str(e)
        


def get_data_dir():
    sql = '''SHOW data_directory;'''
    toto = query_one_flag(sql, (True,))
    if toto:
        return True,toto[1][0]
    else:
        return False, toto[1]
        

def create_saft_table():
    create_table('''CREATE TABLE public.saft_config (
              id SMALLINT NOT NULL,
              unidade_nome VARCHAR(50),
              unit_uuid uuid,
              backup_enable BOOLEAN DEFAULT true NOT NULL,
              backup_last TIMESTAMP(0) WITHOUT TIME ZONE,
              backup_error VARCHAR(50),
              saft_to VARCHAR(512),
              saft_last_send DATE DEFAULT '1970-01-01'::date,
              saft_day SMALLINT DEFAULT 0 NOT NULL,
              CONSTRAINT saft_config_pkey PRIMARY KEY(id)) WITHOUT OIDS;''')
    execute_query('ALTER TABLE saft_config OWNER TO insoft',(1,))
    execute_query('INSERT into saft_config (id,saft_day) VALUES (%s, %s)', (1, 32))


def create_table(sql):
    try:
        conn = psycopg2.connect(gl.c)
        cur = conn.cursor()
        conn.set_client_encoding('UTF8')
        cur.execute(sql, (True,))
        conn.commit()
        cur.close()
        conn.close()
    
    except Exception, e:
        print '-------------------------------------------------------'
        print (str(e) + '\n -- SQL Error --\n in :' + '\n' + sql)
        exit(1)

       
if __name__ == "__main__":
    pass
