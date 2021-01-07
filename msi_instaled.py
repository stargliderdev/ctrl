#!/usr/bin/python
# -*- coding: utf-8 -*-
try:
    import win32com.client
except ImportError:
    pass

def get_odbc_version():
    strComputer = "."
    objWMIService = win32com.client.Dispatch("WbemScripting.SWbemLocator")
    objSWbemServices = objWMIService.ConnectServer(strComputer,"root\cimv2")
    colItems = objSWbemServices.ExecQuery("Select * from Win32_Product")
    bc = {}
    for objItem in colItems:
        if objItem.Name == 'psqlODBC':
            bc["Name"] = objItem.Name
            bc["version"] = str(objItem.Version)
            bc["Package Cache"] = str(objItem.PackageCache)
            a = objItem.Version.split('.')
            bc["major"] = int(a[0])
            bc['minor'] = int(a[1])
            bc['release'] = int(a[2])
            break
    if bc == {}:
        bc["Name"] = 'None'
        bc["version"] = '0.000.000'
        bc["Package Cache"] = 'None'
        bc["major"] = 0
        bc['minor'] = 0
        bc['release'] = 0
    return bc
    


if __name__ == '__main__':
    pass