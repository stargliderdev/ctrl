#!/usr/bin/python
# -*- coding: utf-8 -*-
import subprocess
import ftplib
import sys
import datetime

try:
    import uptime
    import wmi
    import win32com.client
except ImportError:
    pass

import time
import stdio
import parameters as gl

def kill_all_process(kpos=False):
    if kpos == True:
        to_kill = ['pos.exe', 'lprinter.exe', 'rdispatcher.exe', 'rprinter.exe', 'posback.exe', 'incd.exe', 'iwsbk.exe',
                   'iwsmb.exe', 'iwsagt.exe', 'rmonitor.exe']
    hl = subprocess.check_output(['tasklist', '/fo', 'CSV', '/nh']).split('\n')
    gl.kill_count = 0
    for n in hl:
        a = n.split(',')
        if len(a) > 2:
            c = (a[0].replace("\"", ""), a[1].replace("\"", ""))
            if c[0] in to_kill:
                try:
                    subprocess.check_output(['taskkill', '/pid', c[1], '/T', '/F'])
                    gl.kill_count += 1
                except:
                    pass

def kill_boot():
    to_kill = ['boot.exe']
    hl = subprocess.check_output(['tasklist', '/fo', 'CSV', '/nh']).split('\n')
    gl.kill_count = 0
    for n in hl:
        a = n.split(',')
        if len(a) > 2:
            c = (a[0].replace("\"", ""), a[1].replace("\"", ""))
            if c[0] in to_kill:
                try:
                    subprocess.check_output(['taskkill', '/pid', c[1], '/T', '/F'])
                    gl.kill_count += 1
                except:
                    pass

def get_9():
    t0 = time.time()
    root = '/bin/'
    directory = root
    ftp = ftplib.FTP(gl.ftp1[2])
    ftp.login(gl.ftp1[0], gl.ftp1[1])
    stdio.dir_ok('c:\\tmp\\', create=True)
    ftp.cwd(directory)
    try:
        for n in ['psqlODBC_9_x86.msi']:
            file_name = n
            fhandle = open('c:\\tmp\\' + file_name, 'wb')
            ftp.retrbinary('RETR ' + file_name, fhandle.write)
            fhandle.close()
            ftp.sendcmd("MDTM %s" % file_name)
            t1 = time.time()
        return True, str(stdio.seconds_to_hours(t1 - t0))
    except:
        return False, str(sys.exc_info()[0])


def system_stats():
    hl = ''
    a = uptime.uptime()
    day = a // (24 * 3600)
    a = a % (24 * 3600)
    hour = a // 3600
    a %= 3600
    minutes = a // 60
    a %= 60
    seconds = a
    hl += 'uptime ' + "%d dias %d:%d:%d" % (day, hour, minutes, seconds) + '\n'
    hl += 'boot ' + str(uptime.boottime()) + '\n'
    hl += 'now ' + datetime.datetime.now().strftime('%d.%m.%Y %H:%M') + '\n'
    return hl


def pc_info():
    xl = ''
    c = wmi.WMI()
    systeminfo = c.Win32_ComputerSystem()[0]
    
    xl += "Caption " + systeminfo.Caption + '\n'
    xl += "CreationClassName " + systeminfo.CreationClassName + '\n'
    xl += "CurrentTimeZone " + str(systeminfo.CurrentTimeZone) + '\n'
    xl += "DaylightInEffect " + str(systeminfo.DaylightInEffect) + '\n'
    xl += "Domain " + systeminfo.Domain + '\n'
    xl += "EnableDaylightSavings " + str(systeminfo.EnableDaylightSavingsTime) + '\n'
    xl += "Manufacturer " + systeminfo.Manufacturer + '\n'
    xl += "Model " + systeminfo.Model + '\n'
    xl += "Name " + systeminfo.Name + '\n'
    xl += "NetworkServerModeEnab " + str(systeminfo.NetworkServerModeEnabled) + '\n'
    xl += "NumberOfProcessors " + str(systeminfo.NumberOfProcessors) + '\n'
    xl += "NumberOfLogicalProces " + str(systeminfo.NumberOfLogicalProcessors) + '\n'
    xl += "PowerState " + str(systeminfo.PowerState) + '\n'
    xl += "PowerSupplyState " + str(systeminfo.PowerSupplyState) + '\n'
    xl += "PrimaryOwnerName " + systeminfo.PrimaryOwnerName + '\n'
    xl += "SystemStartupOptions " + str(systeminfo.SystemStartupOptions) + '\n'
    xl += "SystemType " + systeminfo.SystemType + '\n'
    xl += "TotalPhysicalMemory " + systeminfo.TotalPhysicalMemory + '\n'
    xl += "UserName " + systeminfo.UserName + '\n'
    return xl


def df():
    xl = ''
    import wmi
    c = wmi.WMI()
    for d in c.Win32_LogicalDisk():
        if d.FreeSpace is not None:
            xl += 'drive ' + d.Caption + "{0:.2f}".format(float(d.FreeSpace) / 1024 / 1024 / 1024) + ' livres de  ' + "{0:.2f}".format(float(d.Size) / 1024 / 1024 / 1024)
    return xl


def get_install_software():
    strComputer = "."
    objWMIService = win32com.client.Dispatch("WbemScripting.SWbemLocator")
    objSWbemServices = objWMIService.ConnectServer(strComputer, "root\cimv2")
    colItems = objSWbemServices.ExecQuery("Select * from Win32_Product")
    data_list = []
    for objItem in colItems:
        data_tuple = (objItem.Version, objItem.Name, objItem.InstallDate, objItem.Vendor)
        data_list.append(data_tuple)
    return data_list
