#!/usr/bin/python
# -*- coding: utf-8 -*-
import parameters as pa
try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    pass
import liberror

def output_query(sql):
    try:
        conn = psycopg2.connect(pa.c)
        cur = conn.cursor()
        conn.set_client_encoding('UTF8')
        cur.execute(sql)
        xl = cur.fetchall()
        cur.close()
        conn.close()
        return xl
    except Exception as e:
        f = liberror.SQLErrorDialog('SQL Execute SQL Error', str(e), sql, '')
        f.exec_()

def output_query_one(sql, data):
    try:
        conn = psycopg2.connect(pa.c)
        cur = conn.cursor()
        conn.set_client_encoding('UTF8')
        cur.execute(sql, data)
        xl = cur.fetchone()
        cur.close()
        conn.close()
        return xl

    except Exception as e:
        f = liberror.SQLErrorDialog('SQL Execute SQL Error', str(e), sql, data)
        f.exec_()

def output_query_many(sql,  data = (True, )):
    try:
        conn = psycopg2.connect(pa.c)
        cur = conn.cursor()
        conn.set_client_encoding('UTF8')
        cur.execute(sql, data)
        xl = cur.fetchall()
        cur.close()
        conn.close()
        return xl
    except Exception as e:
        f = liberror.SQLErrorDialog('SQL Execute SQL Error', str(e), sql, data)
        f.exec_()


def execute_query(sql, data):
    try:
        conn = psycopg2.connect(pa.c)
        cur = conn.cursor()
        conn.set_client_encoding('UTF8')
        cur.execute(sql, data)
        conn.commit()
        cur.close()
        conn.close()

    except Exception as e:
        f = liberror.SQLErrorDialog('SQL Execute SQL Error', str(e), sql, data)
        f.exec_()


def get_table_data(sql,  data = (True, )):
    try:
        conn = psycopg2.connect(pa.c)
        cur = conn.cursor()
        conn.set_client_encoding('UTF8')
        cur.execute(sql, data)
        xl = cur.fetchall()
        cur.close()
        conn.close()
        return True, xl
    except Exception as e:
        return False, str(e), sql, data


            
if __name__ == '__main__': 
    pass
