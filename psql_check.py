#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    pass
import stdio
import parameters as gl
import libpg

def get_saft_data():
    dum = get_record_dic('''SELECT saftname,
              saftaddress, saftpostalcode,
              saftcity, saftnif,
              dbversion, commercial_name
              from params where id = %s''',(0,))
    try:
        gl.saft_config_dict.update(dict(dum))
    except Exception, e:
        init_table()
        print str(e)
        sys.exit(201)
    try:
        dum = get_record_dic('''SELECT saft_to, saft_last_send, saft_day
            FROM saft_config where  id = %s''', (1,))
    except Exception, e:
        init_table()
        print str(e)
        sys.exit(26)
    try:
        gl.saft_config_dict.update(dict(dum))
    except Exception, e:
        init_table()
        print str(e)
        sys.exit(200)
    if validate_field('series', 'id'):
        foo = get_record_dic("""select id from series where inactive = 0 and seriestype_id = %s""",(0,))
        gl.serie_number = foo[0]
    else:
        gl.serie_number = -1
    
def check_field(t, f):
    try:
        sql = 'SELECT attname FROM pg_attribute WHERE attrelid =(SELECT oid FROM pg_class WHERE relname = %s) AND attname = %s;'
        data = (t, f)
        conn = psycopg2.connect(gl.c)
        cur = conn.cursor()
        conn.set_client_encoding('UTF8')
        cur.execute(sql, data)
        output = cur.fetchall()
        cur.close()
        conn.close()
        if len(output) >0:
            return True
        else:
            return False
    except Exception,e:
        print str(e) +  'SQL output #1 Error --\n in :' + sql
        sys.exit(1)

def check_table():
    try:
        sql = '''SELECT
            EXISTS(SELECT * FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name = 'saft_config');'''
        a = libpg.query_one_flag(sql, )[1]
        return a[0]
    except Exception, e:
        return False

    
def get_params():
    try:
        conn = psycopg2.connect(gl.c)
        dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        sql = '''SELECT saftname,dbversion, saftnif, saftaddress,saftpostalcode,saftcity,saftnif,validuntil,commercial_name
                 from params;'''
        dict_cur.execute(sql)
        rec = dict_cur.fetchone()
        dict_cur.close()
        conn.close()
    except Exception as err:
        print(str(err))
        sys.exit(85)
    return rec

def get_record_dic(sql, id):
    # get a connection, if a connect cannot be made an exception will be raised here
    try:
        conn = psycopg2.connect(gl.c)
        dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        dict_cur.execute(sql, id)
        rec = dict_cur.fetchone()
        dict_cur.close()
        conn.close()
    except Exception, e:
        print str(e)
        sys.exit(98)
    return rec

def output_query_many(sql, data):
    try:
        conn = psycopg2.connect(gl.c)
        cur = conn.cursor()
        conn.set_client_encoding('UTF8')
        cur.execute(sql, data)
        output =  cur.fetchall()
        if len(output) == 0:
            output = -1
        cur.close()
        conn.close()
        return output
    except Exception as e:
        print('-' * 40)
        print(str(e) +  '\n -- SQL Error --\n in :\n'  + sql)
        print('-' * 40)
        sys.exit(116)

def psql_listen():
    try:
        conn = psycopg2.connect(gl.c)
        conn.close()
        return True, 'OK'
    except psycopg2.OperationalError as ex:
        return False,"Connection failed: {0}".format(ex)

def check_alive():
    try:
        conn = psycopg2.connect(gl.c)
        cur = conn.cursor()
        conn.set_client_encoding('UTF8')
        cur.mogrify('Select * from articles')
        cur.close()
        conn.close()
        return True,

    except psycopg2.DatabaseError:
        return False

def print_to_txt(dataset):
    for n in dataset:
        for f in n:
            print(f)
        print()

def get_info():
    data_dict = {}
    sql = ' SELECT version();'
    toto = output_query_many(sql, (True,))
    toto = toto[0]
    data_dict['postgres'] = toto [0]
    sql = """SELECT current_timestamp,current_timestamp - pg_postmaster_start_time(), pg_postmaster_start_time(),pg_database_size(%s);"""
    a = output_query_many(sql, ('insoft',))
    data_dict['server_date'] = a[0][0].strftime('%d.%b.%Y %H:%M:%S %Z')
    data_dict['server uptime'] = a[0][1]
    data_dict['server start'] = a[0][2].strftime('%d.%b.%Y %H:%M:%S')
    data_dict['file size'] = stdio.pretty_size(a[0][3]) + '/' + stdio.pretty_size((a[0][3]/100*10))
    sql = """SELECT max(date_time_stamp) as a, doctype.description
           from mov_, doctype
           where mov_.doctype_id = doctype.id and mov_.doctype_id in (2,12)
         group by doctype.description
           order by a desc
           limit 1"""
    try:
        xl = output_query_many(sql, (True,))[0][0]
        data_dict['last_mov_'] = xl.strftime('%d.%b.%Y %H:%M:%S')
    except Exception as e:
        data_dict['last_mov_'] = 'N/D'
    return data_dict

def init_table():   
    CREATE = False
    IS_SAFT_CONFIG = check_table()
    saft_to_stack = ''
    last_send = '1970-01-01'
    # se nao existe a saft o nome coomercial cria
    if not check_field('params', 'commercial_name'):
        libpg.execute_query('''ALTER TABLE params ADD COLUMN commercial_name varchar;''')
        libpg.execute_query('''ALTER TABLE params ALTER COLUMN commercial_name SET STORAGE EXTENDED;''')
        libpg.execute_query('''UPDATE params SET commercial_name='';''')
    if IS_SAFT_CONFIG: # ha saft_config
        if not check_field('saft_config', 'version'): # nao ha versao
            xl = libpg.query_one('select saft_to,saft_last_send from saft_config')
            last_send = xl[1]
            saft_to_stack = xl[0]
            if xl[0] is None:
                saft_to_stack = ''
                # saft_to_stack = ','.join(xl[0])  # copia os dados do mail
            libpg.execute_sql('drop table saft_config') # apaga a tabela
            CREATE = True
        else:
            pass  # tem version nao faz nada so na proxima versao do saft_config
    else:
        CREATE = True # nao tem tabela
        saft_to_stack = ''
    if CREATE: # cria a base de dados do principio
        libpg.execute_query('''create table if not exists saft_config
                    (id smallint not null constraint saft_config_pkey primary key,
                        saft_enable boolean default True NOT NULL,
                        saft_to varchar(512) default '',
                        saft_last_send date default '1970-01-01'::date,
                        saft_day smallint default 1 NOT NULL,
                        status varchar(16) default 0 NOT NULL,
                        lock_count smallint DEFAULT 0 NOT NULL,
                        update_count smallint default 0 NOT NULL,
                        bin_count smallint default 0 NOT NULL,
                        version smallint default 1 NOT NULL,
                        saft smallint default 0 NOT NULL,
                        unique_id uuid );''', (True,))
        libpg.execute_query('ALTER TABLE saft_config OWNER TO insoft')
        libpg.execute_query('insert into saft_config (id,saft_enable,saft_day) values(1,True,1)')
        libpg.execute_query('update saft_config set saft_to=%s, saft_last_send=%s', (saft_to_stack,last_send))
    return True

def validate_field(table, field):
    try:
        sql = 'SELECT ' + field + ' FROM ' + table
        conn = psycopg2.connect(gl.c)
        cur = conn.cursor()
        conn.set_client_encoding('UTF8')
        cur.execute(sql, (True,))
        output = cur.fetchone()
        if len(output) > 0:
            return True
        else:
            return False
    except Exception as e:
        return False

def get_series_info():
    hl = ''
    foo = libpg.query_many("""select id, description, (case  when seriestype_id=0 then 'NORMAL'
    when seriestype_id=1 then 'RDUPLI'
    else 'RMANUA' end) as tp,
      (case when inactive =0 then 'YES' else 'FALSE' end) as inactive from series  order by id""", (0,))
    hl += '-' * 50 + '\n'
    hl += '       ID DESC    TYPE     ACTIVE  DATE' + '\n'
    for n in foo:
        hl += "SERIE " + "{:>3}".format(n[0]) + " " + "{:<8}".format(n[1]) + "{:>3}".format(n[2]) + "{:^9}".format(n[3])
        hl += '  ' + str(libpg.query_one('''select to_char(min(date_time_stamp), 'YYYY-MM-DD') as first_date from mov_ where series_id = %s ''', (n[0],))[0])
        hl += '\n'
    return hl


if __name__ == '__main__':
    pass
