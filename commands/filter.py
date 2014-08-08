
import datetime
import os
import sys
import queue
import threading
import time
import struct
import urllib.request
import pickle

from PyQt5.QtCore import *

import indicators
from modules import db
from modules import globals
from modules import stock
from modules import utils
from modules import stockfilterresultdlg

desc = 'filter subcommand  过滤股票'

subCommands ={
'di' : 'di  使用di条件',
}

def run(subcmd, params):
    chart = globals.mainwin.chart
    stocklist = stock.getStockList()

    if(subcmd == 'di'):
        filterResults = []
        di = indicators.di.Di()

        utils.output('开始di条件过滤')
        prefixstr = 'filter di条件过滤:'
        totalstock = len(stocklist)
        cnt = 0
        start_time = datetime.datetime.now()
        for stockcode in stocklist:
            cnt +=1
            stockcode = stock.normalizeStockCode(stockcode)
            end_time = datetime.datetime.now()
            diffStr = '{}'.format(end_time - start_time)
            outstr = '{} {}/{} 当前代码:{} 符合条件:{} ({})'.format(prefixstr, cnt, totalstock, stockcode, len(filterResults), diffStr)
            utils.overwrite(outstr, prefixstr)
            stockdata = stock.getStockDayDataQianFuQuan(stockcode)
            stockdata = stockdata[-500:]
            didata = di.calculateData(stockdata)
            QCoreApplication.processEvents()
            if(didata[-1] and didata[-1].get('tip')):
                filterResults.append({'code':stockcode, 'date':didata[-1]['date']})

        
        dataArr = []

        for row in filterResults:
            scode = row['code']
            sdate = row['date']
            row=[]
            row.append(scode)
            row.append(stock.getStockName(scode))
            row.append(sdate)
            dataArr.append(row)
    
        #write to file begin
        filename = globals.datapath + '/lastFilterResult.dat'
        try:
            f = open(filename, 'wb')
        except IOError:
            exc_type, exc_value = sys.exc_info()[:2]
            errmsg = '{}: {}'.format(exc_type.__name__, exc_value)
            output(errmsg, 'red')
            return False
        
        pickle.dump(dataArr, f)
        f.close() 
        #write to file end
        
        tablemodel = stockfilterresultdlg.FilterResultModel(dataArr, None)
        tbResults = globals.mainwin.stockfilterresultdlg.tbResults
        tbResults.setModel(tablemodel)
        globals.mainwin.windowStockFilterResult()