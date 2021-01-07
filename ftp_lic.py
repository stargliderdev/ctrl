#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ftplib
import parameters as gl


def get_lic(nif='*'):
    directory = '/lic'
    try:
        ftp = ftplib.FTP(gl.ftp1[2],timeout=15)
        ftp.login(gl.ftp1[0], gl.ftp1[1])
    except Exception as err:
        return False, 'Erro ao ligar ao FTP:' + str(err)
    ftp.cwd(directory)
    # print('dir',directory)
    all_files = []
    files = []
    try:
        all_files = ftp.nlst()
        ftp.quit()
        for n in all_files:
            f = n.find(nif)
            if f > -1:
                files.append(n)
        return True,ftp_to_list(files)
    except Exception as resp:
        print(str(resp))
        return False, str(resp)


def ftp_to_list(mask):
    f = []
    dx = {}
    for n in mask:
        dx = {}
        d = n.rfind('.rar')
        a = n[:d]
        d = a.find('-')
        name = a[:d].replace('_',' ').title()
        g = a[d+1:].split('-')
        nif = g[0]
        version = g[1]
        f.append((name,nif,version,n))
    hl = sorted(f, key=lambda student: student[2], reverse=True)
    return hl

def get_lic_ftp(filename, t_file):
    try:
        session = ftplib.FTP(gl.ftp1[2], gl.ftp1[0], gl.ftp1[1], timeout=5)
        session.cwd('/lic/')
        lic_file = open('c:\\tmp\\' + t_file, 'wb')
        session.retrbinary('RETR %s' % filename, lic_file.write)
        session.quit()
        return True, filename + ' OK!'
    except Exception as resp:
        return False, str(resp)

def make_file_name(f, v='2015.03'):
    k = f.rfind('_')
    f =  f[:k]+'-'+f[k+1:]
    return f.replace('.rar','-' + v + '.rar')

def ftp_get_list(mask):
    f = []
    dx = {}
    for n in mask:
        dx = {}
        d = n.rfind('.rar')
        a = n[:d]
        d = a.find('-')
        name = a[:d].replace('_',' ').title()
        g = a[d+1:].split('-')
        nif = g[0]
        version = g[1]
        f.append((name,nif,version,n))
    hl = sorted(f, key=lambda student: student[2], reverse=True)
    return hl

def driver_list(drv_type):
    directory = '/drivers'
    try:
        ftp = ftplib.FTP(gl.ftp1[2], timeout=15)
        ftp.login(gl.ftp1[0], gl.ftp1[1])
    except Exception as err:
        return False, 'Erro ao ligar ao FTP:' + str(err)
    ftp.cwd(directory)
    dataset = []
    try:
        all_files = ftp.nlst()
        ftp.quit()
        for n in all_files:
            f = n.find(drv_type)
            if f > -1:
                display_name = n.replace(drv_type+'_', '')
                display_name =  display_name.replace('_',' ')
                rp = display_name.rfind('.')
                display_name = display_name[:rp]
                dataset.append((display_name, n))
        
        return True, dataset
    except Exception as resp:
        print(str(resp))
        return False, str(resp)


if __name__ == '__main__':
    pass
