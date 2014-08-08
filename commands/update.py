
import datetime
import queue
import re
import threading
import time

from PyQt5.QtCore import *

from modules import db
from modules import globals
from modules import stock
from modules import utils

desc = 'update subcommand  更新数据状态'

subCommands = {
'stockinfo' : 'stocklist  更新股票基本信息',
'stocklist'	: 'stocklist  更新股票列表数据',
'stockdata'	: 'stockdata [full]  更新股票日线数据'
}


def run(subcmd, params):
    
    if(subcmd == 'stocklist'):
        return _updateStockList()
    elif(subcmd == 'stockdata'):
        return _updateStockData()

def _updateStockList(): 
    
    threadName = 'update_stocklist'
    threadCount = 10
    start_time = datetime.datetime.now()
    
    #terminal all thread from threadList
    def stopThread(threadList):
        for t in threadList:
            t.stop()

    partUrl = 'http://static.sse.com.cn/sseportal/webapp/datapresent/SSEQueryStockInfoAct?reportName=BizCompStockInfoRpt&PRODUCTID=&PRODUCTJP=&PRODUCTNAME=&keyword=&tab_flg=&CURSOR='
    page = 1

    url = '{}{}'.format(partUrl, ((page-1)*50+1))
    err, u, content = utils.getWebContent(url)
    if(err):
        utils.output(err, 'red')
        return False

    #get basic info
    content = content.decode('gbk')
    totalpagelist = re.findall(r'共<strong>([0-9]+)</strong>页', content)
    if(len(totalpagelist)<1):
        utils.output('取得总页数(totalpage)出错', 'red')
        return False
        
    totalstocklist = re.findall(r'第1条到第50条，共([0-9]+)条', content)
    if(len(totalstocklist)<1):
        err = '取得总股票数(totalstock)出错'
        utils.output(err, 'red')
        return False

    totalpage = int(totalpagelist[0])
    totalstock = int(totalstocklist[0])
    utils.output('共{}页, {}只股票'.format(totalpage, totalstock))
    
    #get real stock list data
    in_queue = queue.Queue()
    out_queue = queue.Queue()
    for i in range(1, totalpage+1):
        url = '{}{}'.format(partUrl, ((i-1)*50+1))
        in_queue.put(url)
    
    #start multi-thread fetching
    threadList = utils.getWebContentMT(in_queue, out_queue, threadCount, threadName)

    pattern = '<tr>(.*?)<td class="table3"(.*?)<a href=(.*?)>([0-9]+)</a></td>(.*?)<td class="table3" bgcolor="(.*?)">(.*?)</td>(.*?)</tr>'
    myre = re.compile(pattern, re.DOTALL)

    stocklist = []
    tipstr = 'update stocklist 下载'
    #page downloading
    while(page <= totalpage):
        try:
            err, u, content = out_queue.get(False)
            if(err):
                utils.output(err, 'red')
                stopThread(threadList)
                return False
            
            outstr = '{}({}线程) 第{}/{}页'.format(tipstr, threadCount, page, totalpage)
            if(utils.getLastCmdeditLine()[0:len(tipstr)] != tipstr):
                utils.output(outstr)
            else:
                utils.overwrite(outstr)

            page = page +1

            text = content.decode('gbk')
            #find stock list
            results = myre.findall(text)
            if(not results):
                err = '无法提取到股票列表数据'
                utils.output(err, 'red')
                stopThread(threadList)
                return False

            for r in results:
                lst = list(r)
                line = '{},{}'.format(lst[3], lst[6])
                stocklist.append(line)

        except queue.Empty:
            time.sleep(0.01)
            QCoreApplication.processEvents()

    #download finish, stock list ready
    if(len(stocklist) != totalstock):
        err = '取得的股票列表数目(stocklist)出错 {}!={}'.format(len(stocklist), totalstock)
        utils.output(err, 'red')
        return False

    stocklist.sort()
    utils.output('获取股票列表完成: {}只'.format(len(stocklist)))
    
    #save data
    filename = globals.datapath + '/stocklist.txt'
    data = "\r\n".join(stocklist)
    if(not utils.file_put_contents(filename, data)):
        utils.output('数据保存失败', 'red')
        return False

    utils.output('数据保存成功')

    end_time = datetime.datetime.now()
    return '{}'.format(end_time - start_time)
       



def _updateStockData():

    threadName = 'update_stockdata'
    threadCount = 10
    start_time = datetime.datetime.now()
    
    #terminal all thread from threadList
    def stopThread(threadList):
        for t in threadList:
            t.stop()
    
    stocklist = stock.getStockList()
    if((not stocklist) or len(stocklist)<10):
        utils.output('获取股票列表失败', 'red')
        return False

    utils.output('获取股票列表成功, 数目: {}'.format(len(stocklist)))

    stockStartUrl = 'http://money.finance.sina.com.cn/corp/go.php/vMS_FuQuanMarketHistory/stockid/{}.phtml'
    indexStartUrl = 'http://vip.stock.finance.sina.com.cn/corp/go.php/vMS_MarketHistory/stockid/{}/type/S.phtml'
    baseStockUrl = 'http://money.finance.sina.com.cn/corp/go.php/vMS_FuQuanMarketHistory/stockid/{code}.phtml?year={year}&jidu={jidu}'
    baseIndexUrl = 'http://vip.stock.finance.sina.com.cn/corp/go.php/vMS_MarketHistory/stockid/{code}/type/S.phtml?year={year}&jidu={jidu}'

    #add index 上证50 and 上证综指
    stocklist['sh000001'] = '上证综指'
    stocklist['sh000016'] = '上证50'

    #re for match stock history data
    reStockHisMatch = re.compile("<a target='_blank' href='http://vip.stock.finance.sina.com.cn/quotes_service/view/vMS_tradehistory.php\?symbol=(.+?)&date=(.+?)'>(.+?)</tr>", re.S)    
    
    skeys = list(stocklist.keys())
    skeys.sort()
    scnt = 1
    stotal = len(skeys)
    for scode in skeys:
        sname = stocklist[scode]
        stype = 'stock'
        startUrl = stockStartUrl.format(scode[2:])
        if(scode[:3] == 'sh0'): #大盘指数
            startUrl = indexStartUrl.format(scode[2:])
            stype = 'index'

        err, u, content = utils.getWebContent(startUrl)
        if(err):
            utils.output(err, 'red')
            return False

        content = content.decode('gbk')
        utils.output('开始更新数据: {}/{} {} {}'.format(scnt, stotal, scode, sname))
        scnt +=1
        stocksection = re.findall(r'<!--历史交易begin-->(.+?)<!--历史交易end-->', content, re.S)
        if(len(stocksection) != 1):
            utils.output('截取股票历史数据失败 {}'.format(u), 'red')
            return False

        stockyearsecton = re.findall(r'<select name="year">(.+?)</select>', stocksection[0], re.S)
        if(len(stockyearsecton) != 1):
            utils.output('截取股票历史数据:年份数据失败 {}'.format(u), 'red')
            return False

        yearsdata = re.findall(r'<option value="(\d+?)"(.+?)</option>', stockyearsecton[0], re.S)
        if(len(yearsdata) < 1):
            utils.output('截取股票历史数据:提取年份失败 {}'.format(u), 'red')
            return False     

        yearlist=[]
        for y in yearsdata:
            yearlist.append(list(y)[0])

        #check last update for this stock
        lastupdate = None
        lite3db = db.Sqlite3()
        if(not lite3db.connect()):
            utils.output('截取股票历史数据:数据库连接失败', 'red')
            return False
            
        row = lite3db.selectOne('select * from stockhistory where code =? order by date desc limit 1', (scode, ))
        if(row):
            lastupdate = row['date']
        else:
            lastupdate = '2000-01-01'
            lastupdate = '2011-01-01' #for TEST~~

        hisDataResults = reStockHisMatch.findall(stocksection[0])
        if(len(hisDataResults)< 1):
            utils.output('截取股票历史数据:匹配具体数据失败', 'red')
            return False
        
        #webLastStockDate = hisDataResults[0][1]
        #if(lastupdate == webLastStockDate):
        #    utils.output('数据库内数据已是最新: {}'.format(lastupdate))
        #    continue
        
        #start download history data
        if(getYearAndJidu(lastupdate) == getYearAndJidu(datetime.date.today().isoformat())):
            for res in hisDataResults:
                sdata = re.findall(r'<div align="center">(.+?)</div></td>', res[2])
                if(stype == 'stock' and len(sdata)!=7):
                    utils.output('截取股票历史数据:数据格式错误1', 'red')
                    return False
                elif(stype == 'index' and len(sdata)!=6):
                    utils.output('截取股票历史数据:数据格式错误2', 'red')
                    return False
                qdate = res[1]
                qopen = sdata[0]
                qhigh = sdata[1]
                qclose = sdata[2]
                qlow = sdata[3]
                qvolume = sdata[4]
                qamount = sdata[5]
                qweight = '1.0'
                if(stype == 'stock'):
                   qweight =  sdata[6]

                qid = scode + qdate
                
                lite3db.query('replace into stockhistory(id,code,date,open,high,close,low,volume,amount,weight)values \
                (?,?,?,?,?,?,?,?,?,?)',
                (qid,scode,qdate,qopen,qhigh,qclose,qlow,qvolume,qamount,qweight))
                lite3db.commit()

                    
        end_time = datetime.datetime.now()
        return '{}'.format(end_time - start_time)
        


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