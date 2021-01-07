#!/usr/bin/python
# -*- coding: utf-8 -*-
import fileinput


def read_file(file_name, mode=1):
    try:
        f = open(file_name, "r")
        try:
            if mode == 1:
                # lines into a list.
                toto = f.readlines()
            elif mode == 2:
                # Read the entire contents of a file at once.
                toto = f.read()
            elif mode == 3:
                # OR read one line at a time.
                toto = f.readline()
        
        finally:
            f.close()
    except IOError:
        toto = 'error'
    
    return toto

def write_version():
    with fileinput.FileInput('parameters.py', inplace=True, backup='.bak') as f_name:
        for line in f_name:
            print(line.replace("""# autologin-user = User to log in with by default (overrides autologin-guest)""", 'autologin-user= zorze'))

def get_version():
    xl = read_file('parameters.py')
    for n in xl:
        a = n.find("""VERSION""")
        if a > -1:
            bc = n
            break
    version = bc.split('=')
    version = version[1].replace('\'','')
    return version.strip()
    
    
print(get_version())
