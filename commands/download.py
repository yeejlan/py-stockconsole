
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

desc = 'download subcommand  下载数据'

subCommands ={
'stockhisdata' : 'stockhisdata  下载股票的历史数据',
}

def run(subcmd, params):
    if(subcmd == 'stockhisdata'):
        return downloadStockHisData()


    else:
        utils.output('未知命令', 'red')
        return


def downloadStockHisData():

    threadName = 'download_stockhisdata'
    globals.data[threadName+'_threadlist'] = None
    globals.data[threadName+'_running'] = True

    threadCount = 10
    start_time = datetime.datetime.now()    

    stockStartUrl = 'http://money.finance.sina.com.cn/corp/go.php/vMS_FuQuanMarketHistory/stockid/{}.phtml'
    indexStartUrl = 'http://vip.stock.finance.sina.com.cn/corp/go.php/vMS_MarketHistory/stockid/{}/type/S.phtml'
    baseStockUrl = 'http://money.finance.sina.com.cn/corp/go.php/vMS_FuQuanMarketHistory/stockid/{code}.phtml?year={year}&jidu={jidu}'
    baseIndexUrl = 'http://vip.stock.finance.sina.com.cn/corp/go.php/vMS_MarketHistory/stockid/{code}/type/S.phtml?year={year}&jidu={jidu}'

    stocklist = stock.getStockList()
    if((not stocklist) or len(stocklist)<10):
        utils.output('获取股票列表失败', 'red')
        return False

    utils.output('获取股票列表成功, 数目: {}'.format(len(stocklist)))

    #add index 上证50 and 上证综指
    stocklist['sh000001'] = '上证综指'
    stocklist['sh000016'] = '上证50'

    #build fetch list
    in_queue = queue.Queue()
    
    stockcodes = list(stocklist.keys())
    stockcodes.sort()
    for scode in stockcodes:
        stype = 'stock'
        startUrl = stockStartUrl.format(scode[2:])
        if(scode[:3] == 'sh0'): #大盘指数
            startUrl = indexStartUrl.format(scode[2:])
            stype = 'index'

        #check diskcache before put to download queue
        in_queue.put(startUrl)
    
    def downloadData(in_queue):
        out_queue = queue.Queue()
        page = 1
        totalpage = in_queue.qsize()
        #start multi-thread fetching
        threadList = utils.getWebContentMT(in_queue, out_queue, threadCount, threadName)
        globals.data[threadName+'_threadlist'] = threadList        

        #page downloading
        downloadErrorCnt = 0
        while(globals.data[threadName+'_running'] and (page <= totalpage)):
            try:
                err, u, content = out_queue.get(False)
                if(err):
                    utils.output(err, 'red')
                    downloadErrorCnt +=1
                    continue
                
                end_time = datetime.datetime.now()
                diffStr = '{}'.format(end_time - start_time)
                tipstr = '{} 下载'.format(threadName)
                outstr = '{}({}线程) 第{}/{}页 ({})'.format(tipstr, threadCount, page, totalpage, diffStr)
                utils.overwrite(outstr, tipstr)

                page = page +1

            except queue.Empty:
                time.sleep(0.01)
                QCoreApplication.processEvents()

        return downloadErrorCnt

    downloadErrorCnt = downloadData(in_queue)

    if(not globals.data[threadName+'_running']):
        utils.output('下载已被终止', 'red')
        return
    if(downloadErrorCnt != 0):
        utils.output('下载出错的页面数: {}, 请重新运行命令下载出错的页面'.format(downloadErrorCnt))
        return

    utils.output('下载完成')



def checkDiskCacheForHisData(stockcode, year=None, jidu=None):
    if(year ==None):
        year, jidu = getYearAndJidu(datetime.date.today().isoformat())

    filename = 'stockhis_{}_{}.html'.format(year, jidu)
    filepath = globals.cachepath + '/' + filename
    print(filepath)
        


def checkStockHisDiskData(scode, year=None, jidu=None):
    if(not Year):
        year, jidu = getYearAndJidu(datetime.date.today().isoformat())
        

def getYearAndJidu(dateStr):
    dArr = dateStr.split('-')
    year = dArr[0]
    jidu = '1'
    if(int(dArr[1])>3):
        jidu = '2'
    elif(int(dArr[1])>6):
        jidu = '3'
    elif(int(dArr[1])>9):
        jidu = '4'
    return (year, jidu)
    