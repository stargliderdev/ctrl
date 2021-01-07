#!/usr/bin/python
# -*- coding: utf-8 -*-
import ast
import glob
import os
import subprocess
import hashlib
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import zipfile
import re
from random import randrange
import urllib2
import datetime
from datetime import datetime
import sys
import platform
from operator import itemgetter
from os.path import basename

import libpgf
import psql_check

import parameters as gl
import libpg
import dbmain
import shutil

def table_to_html(title, dataset, css_name='green', header=''):
    if css_name == 'green':
        css = '<style type="text/css">#customers\
            {font-family:"Tahoma", Arial, Helvetica, sans-serif;width:100%;border-collapse:collapse;}\
            #customers td, #customers th {font-size:1em;border:1px solid #98bf21;padding:3px 7px 2px 7px;}\
            #customers th {font-size:14px;font-weight:bold;text-align:center;padding-top:1px;padding-bottom:1px;background-color:#A7C942;color:#000000;}\
            #customers tr.alt td {color:#0000px00;background-color:#EAF2D3;}\
            #right-cell {text-align: right;}</style></head>'
    elif css_name == 'green_small':
        css = '<style type="text/css">#customers\
            {font-family:"Tahoma", Arial, Helvetica, sans-serif;width:100%;border-collapse:collapse;}\
            #customers td, #customers th {font-size:1em;border:1px solid #98bf21;padding:1px 1px 1px 1px;}\
            #customers th {font-size:14px;font-weight:bold;text-align:center;padding-top:1px;padding-bottom:1px;background-color:#A7C942;color:#000000;}\
            #customers tr.alt td {color:#0000px00;background-color:#EAF2D3;}\
            #right-cell {text-align: right;}</style></head>'
    css_table_header = 'customers'
    
    html_header = '<!DOCTYPE html><html lang="pt_pt"><head><meta charset="utf-8"><title>' + title + '</title>'
    
    if header == '':
        row_header = '<table id="' + css_table_header + '"> '
    else:
        print 'create_header'
        row_header = create_header(css_table_header, header)
    listToHtml = create_lines(dataset)
    toto = html_header + css + '<body>' + row_header + listToHtml + '</table></body></html>'
    return toto

def create_header(css_style, header):
    toto = '<table id="' + css_style + '"> <tr>'
    for n in header:
        toto += '<th>' + n + '</th>'
    toto += '</tr>'
    return toto

def create_lines(dataset, stripes=True):
    toto = ''
    odd = True
    col1 = True
    for n in dataset:
        if odd:
            dum = '<tr class="alt">'
        else:
            dum = '<tr>'
        for tr in n:  # dados
            if type(tr) == int:
                dum += '<td id="right-cell">' + str(tr) + '</td>'
            else:
                if col1:
                    dum += '<td align="right">' + str(tr) + '</td>'
                else:
                    dum += '<td>' + str(tr) + '</td>'
                col1 = not (col1)
        if stripes: odd = not (odd)
        toto += dum + '</tr>'
    return toto


def get_params():
    sql = 'Select saftname, saftaddress, saftpostalcode,saftnif,saftcity, commercial_name from params where id=%s;'
    ds = dbmain.output_query_one(sql, (0,))
    if ds is not None:
        if ds[0] is None:
            gl.saftname = 'vazio'
        else:
            gl.saftname = ds[0]
        if ds[1] is None:
            gl.saftaddress = 'Vazio'
        else:
            gl.saftaddress = ds[1]
        if ds[2] is None:
            gl.saftpostalcode = '0000'
        else:
            gl.saftpostalcode = ds[2]
        if ds[3] is None:
            gl.saftnif = '000000000'
        else:
            gl.saftnif = ds[3]
        if ds[4] is None:
            gl.saftcity = 'vazio'
        else:
            gl.saftcity = ds[4]
        if ds[5] is None:
            gl.commercial_name = 'n/d'
        else:
            gl.commercial_name = ds[5]
        sql = ' SELECT version();'
        toto = dbmain.output_query_many(sql, (True,))
        toto = toto[0][0]
        toto = toto.split(',')
        gl.pg_version = toto[0]
        sql = '''SELECT now()::TEXT '''
        gl.pg_date = dbmain.output_query_many(sql, (True,))[0][0]
        gl.last_invoice = dbmain.output_query_one('SELECT max(id) as invoice from mov_ where doctype_id = %s', (2,))[0]
        gl.pass_1 = True
        a = gl.pg_version.split(' ')[1]
        b = a.split('.')
        gl.server_version = b[0] + '.' + b[1]
    else:
        print('erro')
        gl.saftname = 'vazio'
        gl.saftaddress = 'Vazio'
        gl.saftpostalcode = '0000'
        gl.saftnif = '000000000'
        gl.saftcity = 'vazio'
        gl.pg_version = 'Muito antiga'
        gl.pg_date = (1970, 1, 1)
        gl.last_invoice = 0
        gl.pass_1 = False
        gl.server_version = '9.4'



def send_mail_html(to, msg_headers):
    smtpserver = gl.mail_server_internal # 'mail.espiridiao.net'
    smtpuser = gl.mail_user_internal # 'assistencias@espiridiao.net'
    password = gl.mail_pass_internal # 'O9%3NwETT~|[s78'
    a = 'QEF!tp;7!3wh'
    try:
        SUBJECT = msg_headers['sub']
        msg = MIMEMultipart()
        msg['Subject'] = SUBJECT
        msg['From'] = gl.mail_pass_internal  # 'assistencias@espiridiao.net'
        msg['To'] = ','.join(to)
        text = msg_headers['body']
        part1 = MIMEText(text, 'html', 'UTF-8')
        msg.attach(part1)
        session = smtplib.SMTP(smtpserver, 25)
        session.ehlo()
        session.starttls()
        session.ehlo()
        flag = (True, '')
        session.login(smtpuser, a)
        smtpresult = session.sendmail(gl.mail_user_internal, to, msg.as_string())
    except Exception as e:
        flag = False, str(e)
    return flag, 'OK'


def seconds_to_hours(bc):
    m, s = divmod(bc, 60)
    h, m = divmod(m, 60)
    return "%d:%02d:%02d" % (h, m, s)


def kill_process():
    # os.system("tasklist ")
    to_kill = ['iwsbk.exe', 'iwsmb.exe', 'inbck.exe','iwsagt.exe', 'pos.exe', 'lprinter.exe', 'rdispatcher.exe', 'rprinter.exe',
               'posback.exe', 'incd.exe']
    hl = subprocess.check_output(['tasklist', '/fo', 'CSV', '/nh']).split('\n')
    for n in hl:
        a = n.split(',')
        if len(a) > 2:
            c = (a[0].replace("\"", ""), a[1].replace("\"", ""))
            if c[0] in to_kill:
                try:
                    subprocess.check_output(['taskkill', '/pid', c[1], '/T', '/F'])
                except:
                    pass


def read_config_file(file_name):
    lines = []
    try:
        f = open(file_name, "r")
        try:
            lines = f.readlines()
        finally:
            f.close()
    except  Exception, e:
        print2file('error_read_config_file.txt', 'erro ao ler ini\n' + str(e))
        print('erro ao ler ini=>' + file_name + str(e))
        
    return lines

def config_to_text(file_name):
    lines = []
    try:
        f = open(file_name, "r")
        try:
            lines = f.readlines()
        finally:
            f.close()
    except  Exception, e:
        print2file('error_read_config_file.txt', 'erro ao ler ini\n' + str(e))
        return False, ''
    text_str = ''
    for n in lines:
        n = n.replace('\r\n','')
        n = n.replace('[','')
        n = n.replace(']','')
        
        a = n.split('=')
        if len(a) >1:
            text_str += '{:>20}'.format(a[0]) + ':' + a[1]
        else:
            text_str += '\n' + a[0].upper()
    return True, text_str

def ini_file_to_dic(lines):
    dic = {}
    flag = True
    if not lines == []:
        for n in lines:
            dum = n.split('=')
            if len(dum) > 1:
                dic[dum[0]] = dum[1].strip('\r\n')
        flag = True
    else:
        flag = False
    return flag, dic

def print2file(name, content):
    f = open(name, 'w')
    print >> f, content

def read_file(file_name, mode=1):
    try:
        f = open(file_name, "r")
        try:
            if mode == 1:
                toto = f.readlines() # lines into a list.
            elif mode == 2:
                toto = f.read() # Read the entire contents of a file at once.
            elif mode == 3:
                toto = f.readline() # OR read one line at a time.
        
        finally:
            f.close()
    except IOError:
        toto = 'error'
    return toto

def log_write(file_name, content):
    with open(file_name, "a") as myfile:
        myfile.write(content)


def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f %s %s" % (num, 'Y', suffix)


from math import log

def pretty_size(n, pow=0, b=1024, u='B', pre=[''] + [p + 'i' for p in 'KMGTPEZY']):
    pow, n = min(int(log(max(n * b ** pow, 1), b)), len(pre) - 1), n * b ** pow
    return "%%.%if %%s%%s" % abs(pow % (-pow - 1)) % (n / b ** float(pow), pre[pow], u)

def alfa(st):
    b = """OISN94_3?cXI1Y3CdnZ1ZKyV8hgVmd+HtRiqiss+Bvl225hF7CJ0QNnwhWo121mt+sCud
0b7rOl9XnK2PTMtODaw$+!4MsTR[kJ6ne6xyyZToZQGHWK2KmipFPkmm9fkfrO7eC9lQDVJTb6Ps
ri1Zq1kZLW9uVwR+wL6/kA65OZNQyR/jVzU2yPLPwe8ARwFsmLGm+)kiJIJuVC5%F5mFA*S8aV6D
rhnIemLyQYA3jkBODp4ePw1mz4xbkB90JXnOW67zPFWsPmzJD1RWCv79gPaslNsIf15ZmZ1Q3Di6
6ZUmD4zQmlctK8mJ6+MgLTM7wY4qK5kqJDfBMciywvdJQ59zlJp7qck92ZGffpwRcmMFEF5I1sAn
Q3czIzvxUh/N2sw76Wb/4z25Jq8HppdNnH3FMKMFrZVzG/+5DTPluOzLwIrgrF62BFezfJnTPm5J
Qv56pX5O4AP8BvtdYAs33JLmicpDo3eDEPQF63ZG1ngcDAX/+Td7NEogixp6DdRUUjALqSEPiTj4
DHcbEtqWpGGawk4qWw1ib.GtccS3hEAdqBmyp+rosn9LatFW+GmzJSyrbkmaXB/waNfXVjnQdyLP
KXTrt3Rmd6cBx7InWvfmvFR5anLlyReOBwrC8ZyaQi7aBMkgmvb3o37cGyLLjULoBzVa1HNltOsg
99M5LcThZkka2uQbhQ2kU1k1a5FIbcjP5GZBDm+hFur0xsfDZkkvTR+ZytGckDWxEG/8naf1L2x9
wTeQ7xrK6gmK2OaiIjP/eI7gQC5VkiT7t+BOrVnWHRktwf8u+t1TcGjQyr0kux1JPpozqiTWathp
urdn/RNJbr+0yWz3XtGKub3N5wup9a5VvWREHxn85YqItj7DH0Zadqo5/H9g+sRYa4WYzAJacuAS
Ms8dIlRpE_QKEtTXbHHzRoHuJPnSfkbht+RKgSpgeVODXGHFQ6jUt1/wIb5NrUpbsgaBm6ltQOzM
HsFZnFWCN1EvqRl9AgX7uoZy02opaiKgd4X0RAuwR6h2sBg7EL1MFdRtaba13Qd6PjQY3iaTGMaf
mj6wGq3yBmtdW6okImG1Yi8wvR3PEfO9UqJhpBTFUCSPqCY2Elp7Z0MXcWRtoiP2UPld5Nga5XUp
ODHZfMuOB+x7w4YmoFRHi+/aW9q9J/vaENliKLYQEjaOXpD49WgLQ2Uac3N5yZWClPSxnBrfxOG2
lOJLYGTu7LEeTAOcdbwWvtrYh28Ka0s6j2j7fnF3u/T/nTKyrz0kWnnrFoKjQmhYMuxudhWqnKlF"""
    
    d = """iBXNB94a7kx1Ndc29u6nVWD9pV3b+jxI3AzA9nNXArhuq7cWU6sY4i7A3hHXvgF0CRh6Acb2ypzM
gntbzy3Eh1AEPNDjnswaGWuow/MKSixwM8KeO8gGLOqw2mwBvkLn8Y/oIGjUJ5AC/pOSFbo+G1Fo
i6OD1YiHgCO.0VZs7na7hP7A40F9sgVck1+hE8SuDYgyq5CXrMICl/mXs+L8FWz70mkH71kXhBYe
FagWWXMmN0QqoK53vKqYLpRoAG0MtrljwNAnvQNUln/6P@ffyTpqHSxnYoNSU2yXa3xPdECIiCEL
jycqbjABQHTz5ib754f3b7NXb3+8+eH6/XVEasaT6xTihlCyNnLDS4EmVE2PBZhBiar0++4iRJL9
/Pb2u3fRKtVNJdo4ubu8WnkIABB1G4+AXiFUtDJCbdXR0wRbVLxuAdCQvDN4FuzSoDVxCYJRyR8p
2kyBRpFRQ6imJbsDEyR1wy+GCvRNsuiBq8aJIeSt925lNeDRjfn2a1md7zmCPRCxB6RgxQcqoMeA
r9Xdl396sDHun8CazBGtqYK4FM9bnqEZZ+ZlnIz4dqdyBnGC2ZMEIAhGEFNYAeHyikVgp00UYgK7
A9sZIJxGypZLC+7R06mOYBWPYDOXyZNkIaRh6iggM6CmbIpgmCI0Sber7VsWauYZRnqAiJwZrd/a
TQqvVasfRLuLo0WUDLn1xHuDcFdVoPgtkko+9JJ3FzKKLDtbeyLXxXTQTNbVcfledfyEA3soBEnv"""
    
    f = """+TFktyoSOo1bc05tXQhccoxqcKgUg35dxg7BkP9zpAuBS1G+Qa0bBfTgc7ZBFazz4h5TxijIDiW5
8YBjtkJZPbMNr0ZhbMHNyWg9NK4JP0KFWQe8O7GSVaA8FwNegs5jeEhRe/CbodbqbZzMcUta52qr
xzy448CWodOnxj9Tgz5DI8/gnNMq2hAJ9B/2YtnXb+m7Dzc3t9fv3mXfX/9ws5oFHgQRH0oUJjvI
yYofhOw0OA/51UbwPgQwKgvy@w4lCeaqU0dGWDwrRcBHG96jZZRAwKJjPQ4szIfp1Uh8KL3HOTsk
BGdv+2xLYfHRmWxPdjVxJLsf0qqL9aJuunaS4H1PEO9OyN2H3mNxJZ6i1RoasYcbGiFaAQiOV2xp
N7hA7tk2TsVAaN4roGrbiWIHufXXTpBDbfWpe1h8lxNe68mCTQLiwQbjEP0WY5G80sO4vpMPptix
qcPxhXHHVJ01L7jWkBzDYPpElMRqZXJpFEGdLYnQ7knUgvXcuLWtkl2jVyMELlCNPSiZIhZLQ6C1
ejRJQ1JwaYPIgFdYLLwkPk+93TOLqCbdNRCY+OtOaxQXsSj9RYo6vnv0DhZyhX4yabiJOfwg6FFF
PFUUXAV1Q3b/AFL6rWck6nS+5RHk+4/1BXZd7B+W+jfszhrKKpr7/XlZZnjMzCwC5OscDC7YsXFN
E6w921RBNPVQGImRjW0l13kVUkSuYMW1hQ7qj5NyaNzTxZ9/3h86CTankEEwAkJaBi4gTsLLMkO/
jK2FQPuSNfdbyNbKVMBN3u4ATCGX8VPP+Vrjb5xlWINnWZIMqLruB9wYe7MLG5DhNzbNO9wmEbtg
cX/2oPeZD7iak+rt4t3V31aWcQhBpemhtrzmCsqqMMrDOxfgfXOW7vN7noVeGAeLFo1ZmNujDI6F
BjGAdlSSUEEpBaAlwzIHY5IkJslfenth97V80O4gxpJd1qbCELsqKhe46Z9coeGyeV/SA6GTEp/2
BXAYl6JoxV7Cz8Xiq79rED7JXszZL9bv4Y4y3in21cCWBjjBi6xLB++tIExzZeGsu9IDCiumiuJq
aNKTFb4Vz0+yhXLZbsVyWbNnzHruJK64Bj80fanQBGgRwhPkLMr6tNOOGChfYU8np8yKrTmIiuPS
uPXA/zjYKBg3ag7zUmp3QQyA/ifHcvHKviJCV6COxaIVew7VzPLraM4iV73D7WKBDTDevfnpzXsp
Kx25Ts0xlrncPUAEmFYhmYxyJGz5K8hPM.89Bhx0GCugHyNrUxpaaouF9VHXf50gcy4ctH7g17ot
gev0QYmWx8PokTy9EcJQJWqueTPcRAmi5whDz++/0w953+Ibk4woqFs/AT6xOPPnxCKuf8JysO/w
SMkVr/1ygouXQSngRHRKZZo/Ggh5G8IAa3x83/fCISd9+2XAsSlBDGS0mDKxKB6i7LHRHoPtzo0w
7OtU8b088HiKkiWFBZJjyTVfNm37o287KKtcMDqZBcYOPKhK9npLgamrMRT2GNnZhT7D6ORAfJmE
JoVEhpUX4HF1U7TPj2vOjrJje55DAe1wEVhAW+UCNB0OeKE+WbgKBTAmwzjmeJn3UrMxDcNVbKMH
vV/i8MIaBPWCfgmjDq569gerSzIQuD3QlMlM5AYzv9nEQGnEmPNTCrQhgSQcxLhptsfELQOwAYLq
RuKwa3XqgFwp64Bn17e3b2+vIJOcgXz5yFX9zmdd1TWwE51rr3/rQk4VtsskybtDu4pwLWUL9Wze
BANS+v2XW2gor3Z1QUkMAj3YS2FGH1Sh2CC5wKFuc7Szy+GwEsoSKvWxsrFhc6AT9+0BJ70txtbB"""
    
    c = """BIwWT2SPGHsb9nDR4OB04NMo3mxVXnLK7cTWy4ERgVjO/48LgNnPoEMSmeL8E6eBK9p+UeXg7K+V
/MTrW9Ps7Tm2Z+tfeNGC8G0NssGxPhhhlsWaV5s5M8YK/eGc8VK0mMPnpFOA1kuIOEF2AIDUhsE+
NPYLgALew9/ha4cU1tztcIOjZU0Nbw2zGfbmihNS3NXAUWMVLVT8sXyZfGaVkZVYpUxsi7/68mPp
/xEAQXxLstpziM9lLxW0NZqPxUUFWRbv4C9HC+B1cYSer76H9xsBtVibQ1ihxiMQDk7TbB3mSvIa
akscLI5qdJp7OYDEe2EgimDoN/UlCm7tRx5VZMrrOwzNsId6SpyTcTtuinuqw5gdaAmL5MHawJfc
ZbQ9wUFsROfoBCIbtsz9APrkM9+YFH98NhJ6BeAnv/QhVzUEQ0RlxgvAPn2nksgtCzilOvvfr94h
7pZjL2QGi7jbzRa7upeM6RQouD6Op29GHjQoD1+DGnBllGimmI5eya4yM+IS0ovaQ5AG6EZq0Up1
9BYG9bPpF3pljvA6S+qDGESOFy/YX6QQPXU+MtxcD/Q93hsYE3mJT2mD4dCzW/8Xmjhs1Cb2pHQ/
WAVf5/hFGMpEWjQlIpWO9AzVlSsqlycTLt809ztPDA92QIfUFjuMXpVObcxKNc9VsYtHdTNepWmr
AiAbwp6FQofuiWEb2mMZW5U+1M7rgcRJHICEdpjSMH7B8HDTM3DcEAS6YH88uR+vhIg7qHg6sk6y
g3YaUpzmKXShJ5mIfoZlcOwrqC1qxItRCZF7r8JoYNwK7Gh6vD7lVa/f/OfHa0Dbe1aP+cPtD1iY
nx7VfgKGkNCA6PItv5pQxthTnubBxV.CMW7n2LoUNRxNb46DqHehr549ZGho0yzgBXaOpuU2pmb6
cjmN8unTeFTRbxf6D2TMG/afIH0mZXnUGEGiC/3thT7n2+3SzllCq8Li5zAnR4QdJkvSVx5P1lW6
lTapu1ESq6rs2drJVRugm1YUJ+XGkJKXja2uiEq/xzPiooaPFVDoNEeob9KP5WeRqeb8drFhE2oM
Kri7KyNomvLGwScJe2Kq8oLKESp2WzgGPBshuxowJD4oAId_WM0suPe5U+J+nIXjt3hQLCY4OwNu
YjTjFT7hbqiDBbKJbOP/sAEEMjPAyuzXYOxxgC6V7v24AV8OZyDUCuGfZPZfUEsDBBQAAAAIAAwT
XkPcScJdWAAA=HQAA@APAeAAcGlwL19fbWFpbl9fLnB5JYwxDsAgDAP3vCJbYeEBlXhLxABShkAV
qNT+vknxYMlnyyzX0IXzndB0CCa9e6+KvLklAG5I1ItUIswZDyIp3ImOE9BUH16YfRriD2zvbLcu
e09OgluED1BLAwQUA.AACABheztEZ1gc0SAIAACyGQAAEgA.AHBpcC9iYXNlY29tbWFuZC5wed0Y
a2/jNvK7fwXhxUJS6hW6wOE+BAgOm8RpjfbsIE72CmwDgpYoh11J1JGUE9+h//1mSOppJShwPRQ9
f0ik4bxnOA/N5/NLpjm5kkXBypQkOdN6QfBR8ZwZDv9lbUTJ9Xw+n81EUUlliNTNkz62j4YXVSZy
3r4rlvAdS762AFG0h7IyFVOaz2aZkgWpREX8SVKkcChkqdujOJcJs6AGSdVlKco9rcuUK3oQytQs
5+WhT7JvkOFxz1V3lMrnMpcsbc5vRbXlWgP/Doe/JLwaiAwvWerdtCCrUhuW51appVJSLcgDKDQG
zsgbP8/Mk98qfhCy1pe1yNNroSw46hRCRz4zlSayqJhplNoaBW5Ybfp4mlvPqgbnSpaZ2G+sNbf2"""
    
    g = """BJStUlCz3F/zjNW50d/zvLqRqmDG9D0F9pha00SmvPPD9uHqarndLsjy7m5zB7zWP6w3/1hT//p5
dXf/8OnH5fozXW/u6c3mYX39tiMIub1bfl5tHrb08mH14zW9Xt05_j37IQnzRoU9N7RScj+bzSgF
j1NKLsiXwDs0eAS4TeTGxaHc/cITE51bNUpWcMBfy5Lb91qz/QDwJNKUlwC5YTlmKMJSnhFKRSkM
paHmeeaZ4c+5m359BpJ/DywNLO/gnCBFbF+GrgjQDDgP3mvyXgfkPQkb48Jo4chQ32hEljWxAto3
YxmOKVma0ifAoO6SAb21coSFMhu18Xl0DOmQKNEwsFiUpjKhtEP8ddY+WgSflBcT+RienbU+jDqy
d038.NFPss5TAsoTXxyIkcQ8Ce3fyR7qVNWSAtACqA82+tdJtE5u7YoTVgm4tOJfPIyG+kIdQh9p
oG6KVexYfIecw55Ri6G8gQmfQGXzxCFnS65Y3qjfYgC8EdNVvrhgX7mPELWMw96hZ+UOFn3vRlMu
jzHkA16NzKiX2zusO1S7OmiNWzS69lLdn4OyXdEMB/Z+D/HKOUlqbeDmJuzDrkaAJvYmoydq0Kkl
EFkjJU64MueDP.PS4gNXIju6QLSoE0KxwUC30lPc/dm0AH/Yk+AhU5bZ9K0VtEa4pi+CT4rDo+O0
ME91UizwN38yp=qfD9mcVk+Lpt/G+7Wv+zWHWlBAG0cdn8EIVqL2RWXakBCoKYTV8Foa4dotAUgp
zTj6MWLFjhzqDhgCSK0qpYQyWfVdp7ipVdlQdzmnAV5R7M7A5bSoat2h2kymTO21T0187GG/IxlL
jMSgYBzRFMOhe+1ELszxVJPucvQ4W56dzIKJclqaN9XBwfyO3wkj/OX8wHNA+4h6rqWBXB6dfdMl
HuT6Tmo+QvjQIfyzFtyc8HYzTmxfKZgPMTAcIOFfyAeH1NUGHCFySAh0PTbOx46b44IFA9Jc1wVX
OhxkVWh5LXDug+kgBWePGkzoeVwvLx++WwxkxayqeJn2CKKpqwOYlL9UuUig2VpxeniRvIQRDlhy
r2o+6jrDHOtXqvvN9eYchtQjdhJoungRYBLGvMOkxiGxq1mJa0R/6yWc/T0L84QJp7iGwQTpgJnU"""
    
    e = """MYyiQsEFgrcnmaeOdzybMre5L0MbOx5fgtvVLYxSdLW+fbgPHrGbfQwmWfEXoY2mcBPg9W1+y59W
2/st/XR1v9qsHVMSxL9ISPlJbtGkQMUhGxWnB+A9lPeOrDLC.B4QaNIeERaMJ558RRbC2CKkOMxv
R7LjcGehUQx4ABYWlt_m/TAaiuylRsagp4cwEOLQgDwyARsNiENjDnat6fiQsNEuioPohCVmOrjC
hFOD7bRbQIuTjKVZZdsLtF54wz0p7KEvYDAbyZ68i6Pb5f@GHSHcA/6KaDvedohgEQD9LN/dGayh
vi646bc5gYsyamd2N2iqHwQpHJTFaJQON6uf/r48JxDt5jK1U52vyhAeq5VjPCLHjfQZWhPmDeRT
CsYs4MGuXGXCEYZxLjlPOUb6WIAh42zq8EMnBFiUZiKNvHdGmridcHpTG/LAkdPlTQKXO5Nh9OXj
41R0XaJqo0IeTYbfUgfLZhsl+I6jPV7wn0u3MjgI1MwkHDHph9MWxwkjX9u9xmaHv23njf68npg0
u9v6/88M639+=K9MCyz7c7+/8v+BjW+Z8QM/7iRT6QrmHaXqykzOCl7TTQWLk1UgwSqQ51Ardkc7
/k5X3z8mNm+Z0OryO8kffL3pN7OWeK.fQPeiWdlblxroANXwF5QQ/Fz6yaI/DA41PekuQ1EnrbOn
BbTO52CcLzY1VpuJ5HaKFcix+WAZr2FpT+85flxi6niDAlKOil7YHng6EwydgHzs14Tfz4JhzLcQ
CjuT8l29xzO74GRM5LCGQk76q9djecKtUSN+VsLwEEPzOk6SwwYSDoZzP0b4NouzxNSYcULpWzvm
2mw2w62ql61Nf@lAdr5vgKgGjMKGgtqTcX2yGG6Bb76IemD7ERr2Vej1tP2uG5415AtydpaKxIRo
rgVuNI7U6w6AGNaDA8trtMxZMQgl/rEfyUghU36Bk5zTeT6fQ8Up7QaBCKmLHaBj0Nw2ZGn8ZgAj
M6JaBJbDaJweiZvCYaYi9rsug1SArQOmKMhMiXOztQtYG+kMbhjA6uEp7FJj3OwL27DbapJaKdj0
8d_@?kOaaWkvBM%|»TASde4Rly$rQrj%tP(0qV)]@!o&wVffLsaqR6c654g61j37-df72a9H40e00"""
    a = b + d + f + c + g + e
    toto = ''
    for n in st:
        toto += a[n - 5]
    # for n in range(0,len(a)):
    #     print a[n-5], n
    return toto


def wipe(path):
    with open(path, 'wb') as fout:
        fout.write(os.urandom(randrange(1309, 7483)))


def run_silent(command):
    try:
        toto = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        result = toto.stdout.readlines()
        return True
    except Exception, err:
        print str(err)
        return False


def delete_file(path):
    if os.path.isfile(path):
        os.remove(path)

def check_bin_dates():
    import os.path, datetime
    gl.bin_report = []
    gl.bin_report_table = []
    dir = 'c://insoft/'
    bin_files = ['pos', 'lprinter', 'rdispatcher', 'posback', 'mansaft', 'rprinter']
    # self.PRINT('<font color="magenta">   *** datas dos executaveis ***')
    # self.PRINT(base64.b64decode('ICAgKioqIGRhdGFzIGRvcyBleGVjdXRhdmVpcyAqKio='))
    gl.bin_report.append('  *** datas dos executaveis ***')
    
    for n in bin_files:
        f = dir + n + '.exe'
        if file_ok(f):
            t = os.path.getmtime(f)
            datetime.datetime.fromtimestamp(t)
            gl.bin_report.append(datetime.datetime.fromtimestamp(t).strftime('%d.%m.%Y %H:%M') + ' = ' + n + '.exe')
            gl.bin_report_table.append([datetime.datetime.fromtimestamp(t).strftime('%d.%m.%Y %H:%M'), n + '.exe'])
    gl.bin_report.append('</font>')


def internet_on():
    try:
        response = urllib2.urlopen('https://www.google.com', timeout=3)
        return True
    except urllib2.URLError as err:
        return False


def file_ok(f_name):
    if os.path.exists(f_name):
        return True
    else:
        return False

def remove_file(f_name):
    if os.path.exists(f_name):
        os.remove(f_name)

def print_dict(bc):
    xl = ''
    for key, value in bc.items():
        if type(value) == int:
            value = str(value)
        elif type(value) == float:
            value = str(value)
        elif type(value) is None:
            value = 'None'
        elif type(value) == datetime.datetime:
            # print 'datetime'
            value = value.strftime('%d.%b.%Y')
        
        else:
            value = str(value)
        xl += "{:>16}".format(key) + ':' + value + '\n'
    return xl

def search_by_value(dic, tx):
    return [key for key, value in dic.iteritems() if value == tx][0]


def dir_ok(path, create=True):
    if os.path.isdir(path):
        return True
    else:
        if create:
            os.makedirs(path)
            return True
        return False

def delete_dir(p):
    try:
        shutil.rmtree(p)
    except Exception:
        pass

def delete_files(path, mask='.txt'):
    for hl in os.listdir(path):
        if hl.endswith(mask):
            os.remove(path + '\\' + hl)

def zip_file(filename):
    import gzip
    dum = filename + '.gz'
    dum = dum[:dum.rfind('.xml')]
    f_in = open(filename, 'rb')
    f_out = gzip.open(filename + '.gz', 'wb')
    f_out.writelines(f_in)
    f_out.close()
    f_in.close()
    
    if not file_ok(dum + '.gz'):
        os.rename(filename + '.gz', dum + '.gz', )
    return dum + '.gz'

# def unrar(text):
#     dum2 = Fernet(b'y6E2FGsFHov1FcTKnXReUwTEm0P_sbOHFniE90tXtO0=')
#     return dum2.decrypt(text)

def compress_file(file_name):
    compression = zipfile.ZIP_DEFLATED
    dum = file_name  # file_name[:file_name.rfind('.xml')]
    zf = zipfile.ZipFile(dum[:-4] + '.zip', mode='w')
    try:
        zf.write(dum, arcname=basename(dum), compress_type=compression)
    except Exception, err:
        print (str(err))
        sys.exit(496)
    finally:
        zf.close()
    return dum[:-4] + ".zip"

def get_sha256(file_name, b=128):
    return hash_bytestr_iter(file_as_blockiter(open(file_name, 'rb')), hashlib.sha256())[:b]

def hash_bytestr_iter(bytesiter, hasher, ashexstr=False):
    for block in bytesiter:
        hasher.update(block)
    return (hasher.hexdigest() if ashexstr else hasher.hexdigest())

def file_as_blockiter(afile, blocksize=65536):
    with afile:
        block = afile.read(blocksize)
        while len(block) > 0:
            yield block
            block = afile.read(blocksize)

def check_ini():
    a = platform.platform().split('-')
    gl.system_info['os'] = a[0]
    gl.system_info['os_version'] = a[1]
    gl.system_info['arch'] = platform.architecture()[0]
    libpgf.to_pdf()
    
    if file_ok('c:\insoft\pos.ini'):
        c = ini_file_to_dic(read_config_file('c:\insoft\pos.ini'))
        if c[0]:
            gl.pos_ini = c[1]
            gl.pos_ini['u'] = 'root'
        return True
    else:
        if file_ok('c:\insoft\posback.ini'):
            c = ini_file_to_dic(read_config_file('c:\insoft\posback.ini'))
            if c[0]:
                gl.pos_ini = c[1]
                gl.pos_ini['u'] = 'root'
            return True
        else:
            gl.msg.append('No pos.ini/posbak.ini file found. Loading Defaults ')
            gl.pos_ini['host'] = 'localhost'
            gl.pos_ini['port'] = '5432'
            gl.pos_ini['db'] = 'postgres'
            gl.pos_ini['posid'] = '1'
            return False


def is_server():
    flag_convert = {'S':True,'N':False}
    saft_enable = dbmain.output_query('''select TO_CHAR(saft_last_send, 'YYYY-MM-DD') as l from saft_config''')
    if saft_enable[0][0] == '1970-01-01':
        gl.server_data['saft'] = False
    else:
        gl.server_data['saft'] = True
    if gl.pos_ini['host'] in ('localhost','127.0.0.1'):
        # é um servidor
        gl.server_data['server'] = True
        return True
    else:
        return False

def get_server_data():
    flag_convert = {'S': True, 'N': False}
    saft_enable = dbmain.output_query('''select TO_CHAR(saft_last_send, 'YYYY-MM-DD') as l from saft_config''')
    # lic_dict = get_lic_file('c:\\insoft\\pos.lic')
    if file_ok('c:\\insoft\\insoft.lic'):
        flag, lic_dict = get_lic_file('c:\\insoft\\insoft.lic')
    else:
        flag, lic_dict = get_lic_file('c:\\insoft\\pos.lic')
    try:
        a = lic_dict['NomeSoftware'].split()
    except KeyError:
        a = ['Erro','Erro']
    gl.server_data['software'] = a[0]
    if saft_enable[0][0] == '1970-01-01':
        gl.server_data['saft'] = False
    else:
        gl.server_data['saft'] = True
    if gl.pos_ini['host'] in ('localhost', '127.0.0.1'):
        # é um servidor
        gl.server_data['server'] = True
        gl.server_data['terminals'] = int(
            dbmain.output_query('select count(id) as postos from pos where id <11')[0][0])
        xl = dbmain.output_query('select id from pos where id=11')
        if not xl:
            gl.server_data['iws'] = False
        else:
            gl.server_data['iws'] = True
        gl.server_data['host'] = gl.pos_ini['host']
        xl = dbmain.output_query_many('select description from printers where ttype=0;')
        gl.server_data['printers_names'] = ''
        for n in xl:
            gl.server_data['printers_names'] = gl.server_data['printers_names'] + n[0] + ','
        gl.server_data['printers'] = len(xl)
        xl = dbmain.output_query_many('select description from printers where ttype=1;')
        gl.server_data['monitors_names'] = ''
        for n in xl:
            gl.server_data['monitors_names'] = gl.server_data['monitors_names'] + n[0] + ','
        gl.server_data['monitors'] = len(xl)
        gl.server_data['serie'] = dbmain.output_query(
            """select concat(id,'-', description) as serie from series where inactive = 0 and seriestype_id = 0""")[0][0]
        try:
            gl.server_data['agd'] = flag_convert[lic_dict['AnaliseGestaoDiaria']]
        except KeyError:
            gl.server_data['agd'] = ''
        try:
            gl.server_data['contract'] = lic_dict['DataContrato']
        except KeyError:
            pass
        try:
            gl.server_data['valid_until'] = lic_dict['Validade']
        except KeyError:
            pass
        return True
    else:
        # não é um servidor
        return False

def get_lic_file(lic_file):
    lic_dict = {}
    try:
        if file_ok(lic_file):
            if run_silent('c:\\insoft\\checklic.exe ' + lic_file.replace('\\',os.sep)):
                lic_dict = ini_file_to_dic(read_config_file(lic_file.replace('\\',os.sep) + '.txt'))[1]
    except Exception as err:
        False, str(err)
    return True, lic_dict

def lic_string_to_dict(lic_txt):
    print lic_txt
    lic_dict = {}
    for n in lic_txt:
        print n
        a = n.find('[')
        if a >-1:
            pass
        else:
            b = n.split('=')
            lic_dict[b[0]] = lic_dict[b[1]]
    import pprint
    pprint.pprint(lic_dict)

def touch(fname):
    remove_file(fname)
    if os.path.exists(fname):
        os.utime(fname, None)
    else:
        open(fname, 'a').close()

def get_backup_data(file_name):
    b_data = {}
    xl = os.path.basename(file_name)
    b = xl.replace(' ', '')
    b = b.replace('T', '')
    b = b.replace('_', '')
    b = b.replace('-', '')
    c = re.sub(r'[^0-9]+', '', b, re.I)
    p1 = c.rfind('.')
    c = c[:p1]
    c = c[-14:]
    if is_date(c):
        dt = datetime.strptime(c, '%Y%m%d%H%M%S')
        old = datetime.now()- dt
        b_data['data'] = dt.strftime("%d-%m-%Y %H:%M")
        b_data['old'] = str(old).replace('day','dia')[:-10]
    else:
        b_data['data'] = 'Não disponivel mas podes continuar!'
        b_data['old'] = 'n/d'
    b = xl.replace('-', '_')
    b = b.split('_')
    if len(b) >0:
        dum = ''
        for n in b:
            try:
                dum =  str(int(n))
                break
            except (ValueError, IndexError, TypeError):
                pass
        if dum == '':
            b_data['nif'] = 'n/d'
        else:
            b_data['nif'] = dum
    return b_data
    
def get_file_name_data(file_name):
    s0 = file_name.find('-')
    unit_name = file_name[:s0].replace('_',' ')
    dum = file_name[s0+1:]
    # print dum
    nif = dum[:dum.find('-')]
    dum = dum[dum.find('-')+1: -7]
    dum_l = dum.split('_')
    try:
        version = dum_l[0]
    except IndexError:
        version = ''
    try:
        date = dum_l[1]
    except IndexError:
        date = ''
    try:
        time = dum_l[2]
    except IndexError:
        time = ''
    return unit_name, nif, version,date,time

def is_date(date_text):
    try:
        if date_text == datetime.strptime(date_text, "%Y%m%d%H%M%S").strftime('"%Y%m%d%H%M%S"'):
            pass
        return True
    except ValueError:
        return False

def make_backup():
    file_name = ''
    try:
        run_silent('c:\\insoft\\manback.exe')
        if file_ok('manback.success'):
            pass
        else:
            return False, 'manbackup.error'
        file_paths = glob.glob('c:\\backup\\*.backup')
        sorted_files = sort_files_by_last_modified(file_paths)
        file_ftp = sorted_files[-1][0]
        file_name = file_ftp[file_ftp.rfind('\\') + 1:]
    except Exception as err:
        return False,str(err)
    return True,file_name

def get_last_backup():
    try:
        file_paths = glob.glob('c:\\backup\\*.backup')
        sorted_files = sort_files_by_last_modified(file_paths)
        file_ftp = sorted_files[-1][0]
        file_name = file_ftp[file_ftp.rfind('\\') + 1:]
        a = file_name.replace('-','_')
        a = a.replace('.backup','')
        a = a.split('_')
        nome = ''
        b_data = {}
        for n in a:
            if n.isdigit():
                if int(n) > 100000000:
                    b_data['nif'] = n
                else:
                    if len(n) == 8:
                        b_data['data'] = datetime.strptime(n, '%Y%m%d').date()
                    elif len(n) == 6:
                        b_data['hora'] = datetime.strptime(n, '%H%M%S').time()
                    else:
                        print n, 'e outra coisa '
            else:
                if n.find('.') > -1:
                    b_data['version'] = n
                else:
                    nome = nome + ' ' + n
        b_data['nome'] = nome
        b_data['file_name'] = file_name
        b_data['file_size'] = os.path.getsize('c:\\backup\\' + file_name) / 1024
    
        return True, b_data
    except Exception as err:
        return False, str(err)

def sort_files_by_last_modified(files):
    file_data = {}
    for fname in files:
        file_data[fname] = os.stat(fname).st_mtime
    file_data = sorted(list(file_data.items()), key = itemgetter(1))
    return file_data

def spool_clean():
    a = libpg.query_one('''select count(id) from request_print ''', (True,))[0]
    b = libpg.query_one('''select count(id) from print_spool ''', (True,))[0]
    libpg.execute_query("delete from print_spool", (True,))
    libpg.execute_query("delete from print_jobs", (True,))
    libpg.execute_query("delete from request_print", (True,))
    return {'request_print':a, 'print_spool': b}


def info_psql():
    sql = 'SELECT version();'
    a = libpg.query_many(sql, (True,))
    a = str(a[0])
    a = a.replace('(', '')
    a = a.replace('\'', '')
    a = a.split(',')
    tx = ''
    tx += 'Server Version: ' + str(a[0]) + ' ' + str(a[2]) + '\n'
    sql = """SELECT current_timestamp,current_timestamp - pg_postmaster_start_time(), pg_postmaster_start_time(),pg_database_size(%s);"""
    a = libpg.query_one(sql, ('insoft',))
    tx += '   Server date: ' + a[0].strftime("%Y-%m-%d %H:%M") + '\n'
    tx += ' Server uptime: ' + str(a[1]) + '\n'
    tx += '  Server start: ' + a[2].strftime("%Y-%m-%d %H:%M") + '\n'
    b = str(a[3]) + '/' + pretty_size((a[3] / 100 * 10))
    b = pretty_size((a[3] / 100 * 10))
    tx += '     File size: ' + b + '\n'
    return tx

def info_restware_long():
    hl = ''
    sql = '''select  id, description from doctype  ORDER BY doctype.id; '''
    xl = libpg.query_many(sql, True)
    hl += '-' * 50 + '\n'
    hl += '      NUM    DOC      DATA             VALOR' + '\n'
    for n in xl:
        sql = '''SELECT id, date_time_stamp, total_value/100
                from mov_
                where doctype_id = %s
                order by date_time_stamp desc
                limit 1'''
        b = libpg.query_one(sql, (n[0],))
        if b is None:
            pass
        else:
            hl += "{:>12}".format(b[0]) + "{:>4}".format(n[1]) + "{:>20}".format(str(b[1])) + "{:10.2f}".format(
                b[2]) + '\n'

    return hl + '\n'

def info_restware_short():
    hl = ''
    sql = '''SELECT saftname,commercial_name, saftnif,saftaddress, saftcity,saftpostalcode,dbversion,validuntil,lic,  clockchangeinterval,
    commercial_name, manager_name, manager_phone, manager_email, accountant_name, accountant_email, psql_version, to_ftp, last_backup,
    runafterexpired, softwareedition, notifydiscountinvalue, discountandmenu, requestresend, requestprintsummary
     from params;'''
    d = libpg.query_many(sql)[0]

    hl += "{:>14}".format('D. Social: ') + d[0].decode('utf-8') + '\n'
    try:
        hl += "{:>14}".format('D. Comercial:') + d[1].decode('utf-8') + '\n'
    except IndexError:
        hl += "{:>14}".format('D. Comercial:') + 'Erro de chave\n'
    try:
        hl += "{:>14}".format('NIF:') + d[2] + '\n'
    except IndexError:
        hl += "{:>14}".format('NIF:') + 'Erro de indice\n'
    try:
        hl += "{:>14}".format('Endereco:') + d[3].decode('utf-8') + '\n'
    except IndexError:
        hl += "{:>14}".format('Endereco:') + 'Erro de indice\n'
    try:
        hl += "{:>14}".format('Localidade:') + d[4].decode('utf-8') + '\n'
    except IndexError:
        hl += "{:>14}".format('Localidade:') + 'Erro de indice\n'
    try:
        hl += "{:>14}".format('C.P.:') + d[5].decode('utf-8') + '\n'
    except IndexError:
        hl += "{:>14}".format('C.P.:') + 'Erro de indice\n'
    try:
        hl += "{:>14}".format('dbversion:') + d[6] + '\n'
    except IndexError:
        hl += "{:>14}".format('dbversion:') + 'Erro de indice\n'
    try:
        hl += "{:>14}".format('Validade:') + str(d[7]) + '\n'
    except IndexError:
        hl += "{:>14}".format('Validade:') + 'Erro de indice\n'
    try:
        hl += "{:>14}".format('lic:') + d[8] + '\n'
    except (TypeError, IndexError):
        hl += "{:>14}".format('lic:') + 'NULL\n'
    if psql_check.validate_field('series', 'id'):
        hl += psql_check.get_series_info()
    else:
        gl.serie_number = -1
    low = '\n'
    low += "{:>26}".format('CLOCKCHANGEINTERVAL: ') + str(d[9]) + '\n'
    low += "{:>26}".format('COMMERCIAL_NAME: ') + d[1].decode('utf-8') + '\n'
    low += "{:>26}".format('MANAGER_NAME: ') + str(d[11]) + '\n'
    low += "{:>26}".format('MANAGER_PHONE: ') + str(d[12]) + '\n'
    low += "{:>26}".format('MANAGER_EMAIL: ') + str(d[13]) + '\n'
    low += "{:>26}".format('ACCOUNTANT_NAME: ') + str(d[14]) + '\n'
    low += "{:>26}".format('ACCOUNTANT_EMAIL: ') + str(d[15]) + '\n'
    low += "{:>26}".format('PSQL_VERSION: ') + str(d[16]) + '\n'
    low += "{:>26}".format('TO_FTP: ') + str(d[17]) + '\n'
    low += "{:>26}".format('LAST_BACKUP: ') + str(d[18]) + '\n'
    low += "{:>26}".format('RUNAFTEREXPIRED: ') + str(d[19]) + '\n'
    low += "{:>26}".format('SOFTWAREEDITION: ') + str(d[20]) + '\n'
    low += "{:>26}".format('NOTIFYDISCOUNTINVALUE: ') + str(d[21]) + '\n'
    low += "{:>26}".format('DISCOUNTANDMENU: ') + str(d[22]) + '\n'
    low += "{:>26}".format('REQUESTRESEND: ') + str(d[23]) + '\n'
    return hl, low

def info_restware_detail():
    sql = '''select  id,description, price_1/100 as pvp1 ,price_2/100 as pvp2 from articles where id < 999900 order by id desc limit 1'''
    a = libpg.query_one(sql)
    hl = "{:>6}".format(a[0]) + ' ' + "{:<40}".format(a[1]) + "{:6.2f}".format(a[2]) + "{:6.2f}".format(a[3]) + '\n'
    sql = '''select  id, clients.name, nif
from clients
order by id desc
limit 1'''
    c = libpg.query_one(sql)
    hl = "{:>6}".format(b[0]) + ' ' + "{:<40}".format(b[1])  + '\n'
    


    return hl


if __name__ == '__main__':
    pass
