
import datetime
import os
import sys
import queue
import threading
import time
import struct
import urllib.request

from modules import db
from modules import globals
from modules import stock
from modules import utils

desc = 'viewport subcommand  更新股票视图'

subCommands ={
'clear' : 'clear  清除图形',
'show' : 'show stock_code  显示股票K线图',
}

def run(subcmd, params):
    if(subcmd == 'show'):
        if(len(params) == 1):
            return showStockChart(params[0])
        else:
            utils.output('请给出股票代码', 'red')
            utils.output(subCommands['go'])
            return
    
    elif(subcmd == 'clear'):
        globals.viewportclear = True
        utils.update()


def showStockChart(stockcode):
    
    stockcode = stock.normalizeStockCode(stockcode)
    kdata = stock.getStockDayDataQianFuQuan(stockcode)
    if(not kdata):
        utils.output('股票数据不存在', 'red')
        return False

    if(stockcode[:3] != 'sh0'):
        weightdata = stock.getStockWeightData(stockcode)
        if(not weightdata):
            utils.output('复权数据不存在', 'red')
            return False
        #print(weightdata)

    #set data
    globals.mainwin.chart.kdata = kdata
    globals.mainwin.chart.stockcode = stockcode
    globals.mainwin.scrollbar.setMinimum(0)
    ktotalcount = len(kdata)
    globals.mainwin.scrollbar.setMaximum(ktotalcount)
    globals.mainwin.scrollbar.setValue(ktotalcount)
    globals.mainwin.scrollbar.setSingleStep(1)
    if(stockcode[:3] != 'sh0'):
        globals.mainwin.chart.weightdata = weightdata

    #draw
    globals.viewportclear = False
    utils.update()