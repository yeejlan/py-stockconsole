
import datetime
import os
import sys
import queue
import threading
import time
import urllib.request

from PyQt5.QtCore import *

from modules import db
from modules import globals
from modules import stock
from modules import utils

desc = 'abort subcommand  终止数据下载'

subCommands ={
'stockhisdata' : 'stockhisdata  终止股票历史数据的下载',
}

def run(subcmd, params):
    if(subcmd == 'stockhisdata'):
        while(True):
            if(cancelDownload('download_stockhisdata')):
                break

            time.sleep(0.01)
            QCoreApplication.processEvents()
        
        return

    else:
        utils.output('未知命令', 'red')
        return


#cancel download
def cancelDownload(threadName):

        def stopThread(threadName):
            threadList = []
            try:
                threadList = globals.data[threadName+'_threadlist']
                globals.data[threadName+'_threadlist'] = None
                globals.data[threadName+'_running'] = False
            except:
                pass

            if(threadList):
                for t in threadList:
                    t.stop()


        threadLeft = 0
        stopThread(threadName)
        for t in threading.enumerate():
            if(t.getName() == threadName):
                threadLeft +=1

        if(threadLeft > 0):
            tipstr = '终止下载中, 目前剩余'
            outstr = '{} {} 线程'.format(tipstr, threadLeft)
            utils.overwrite(outstr, tipstr)
            return False
        else:
            utils.output('所有下载线程已终止')
        return True