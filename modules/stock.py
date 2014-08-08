

import datetime
import random
import re
import struct
import time

from modules import db
from modules import globals
from modules import utils

def getHq(stock_code):
    url = 'http://hq.sinajs.cn/rn={}&list={}'.format(random.randint(1,1000000), stock_code)
    err, u, content = utils.getWebContent(url)
    if(err):
        utils.output(err, 'red')
        return False

    content = content.decode('gbk')
    dataArr = re.findall(r'"(.*)"', content)[0].split(',')
    if(len(dataArr)<31):
        utils.output('no data')
        return False

    info = {}
    info['name'] = dataArr[0]
    info['code'] = stock_code
    info['open'] = float(dataArr[1])
    info['close_yesterday'] = float(dataArr[2])
    info['price'] = float(dataArr[3])
    info['close'] = info['price']
    info['high'] = float(dataArr[4])
    info['low'] = float(dataArr[5])
    info['amount'] = float(dataArr[9])/1000
    info['date2'] = dataArr[30]
    info['date'] = info['date2'].replace('-', '')
    info['time'] = dataArr[31]
    if info['close_yesterday'] > 0:
        info['price_chg'] = (info['price']-info['close_yesterday'])*100/info['close_yesterday']

    if(info['open'] == 0):
        info['open'] = info['price']

    return info


def normalizeStockCode(code_text):
    stock_code = code_text
    trade_code = ''
    if(stock_code[:2] == 'sh' or stock_code[:2] == 'sz'):
        trade_code = stock_code[:2]
        stock_code = stock_code[2:]

    if(len(stock_code) < 6):
        padlen = 6 - len(stock_code)
        padlist = []
        for i in range(0, padlen):
           padlist.append('0');
        padstr = ''.join(padlist)
        stock_code = stock_code[:1] + padstr + stock_code[1:]

    try:
        code_int = int(stock_code)
    except ValueError:
        return ''

    if(not trade_code):
        if(code_int < 600000):
            trade_code = 'sz'
        else:
            trade_code = 'sh'

    return trade_code + stock_code

def getStockList():
    stocklistfile = globals.datapath + '/stocklist.txt'
    stocklistdata = utils.file_get_contents(stocklistfile)
    if(not stocklistdata):
        utils.output('股票列表载入失败, 请先运行update stocklist', 'red')
        return False

    stocklist = {}
    lines = stocklistdata.split("\n")
    for line in lines:
        if(line):
            stockArr = line.split(',')
            if(len(stockArr)==2):
                scode = normalizeStockCode(stockArr[0])
                stocklist[scode] = stockArr[1]

    return stocklist

def getStockDayData(stockcode):
    daydata = []
    dayfilename = globals.tdxdaybase + '/{}.day'.format(stockcode)

    content = utils.file_get_contents(dayfilename, 'rb')
    if(not content):
        return False

    for i in range(0, len(content), 32):
        d = content[i:i+32]
        data = struct.unpack('iiiiifii', d)
        row ={}
        row['date'] = '{}'.format(data[0])
        row['open'] = data[1]/100
        row['high'] = data[2]/100
        row['low'] = data[3]/100
        row['close'] = data[4]/100
        row['amount'] = data[5]/1000
        row['volume'] = data[6]
        daydata.append(row) 
        
    return daydata

def getStockDayDataQL(stockcode):
    daydata = []
    dayfilename = globals.qldaybase + '/{}.day'.format(stockcode[2:])

    content = utils.file_get_contents(dayfilename, 'rb')
    if(not content):
        return False

    for i in range(0, len(content), 40):
        d = content[i:i+40]
        data = struct.unpack('iiiiiiiiii', d)
        row ={}
        row['date'] = '{}'.format(data[0])
        row['open'] = data[1]/1000
        row['high'] = data[2]/1000
        row['low'] = data[3]/1000
        row['close'] = data[4]/1000
        row['amount'] = data[5]
        row['volume'] = data[6]
        daydata.append(row) 
        
    return daydata

def getStockWeightData(stockcode):
    weightdata = []
    if(stockcode[:3] == 'sh0'): #index
        return weightdata

    weightfilename = globals.qlweightbase + '/{}.wgt'.format(stockcode[2:])

    content = utils.file_get_contents(weightfilename, 'rb')
    if(not content):
        return False

    for i in range(0, len(content), 36):
        d = content[i:i+36]
        data = struct.unpack('iiiiiiiii', d)
        y= data[0] >>20
        m=(data[0]&0xf0000)>>16
        d=(data[0]&0xffff)>>11
        
        row = {}
        row['date'] = '{}{:02d}{:02d}'.format(y,m,d)
        row['songgu'] = data[1]/100000
        row['peigu'] = data[2]/100000
        row['peigu_price'] = data[3]/10000
        row['fenhong'] = data[4]/10000
        row['zhuanzeng'] = data[5]/100000
        weightdata.append(row) 
        
    return weightdata

def getStockDayDataHouFuQuan(stockcode):
    houfuquan = []
    daydata = getStockDayData(stockcode)
    if(not daydata):
        return False

    if(stockcode[:3] == 'sh0'): #index
        return daydata

    wgtdata = getStockWeightData(stockcode)
    if(not wgtdata):
        for row in daydata:
            row['weight'] = 1.0
            houfuquan.append(row)

        return houfuquan

    wgt_idx = 0
    wval = 1.0
    prev_wval = wval
    prev_row = None
    prev_date = daydata[0]['date']
    wgt_row = wgtdata[wgt_idx]
    while(wgt_row['date']<prev_date):
            if(wgt_idx < len(wgtdata)-1):
                wgt_idx += 1
                wgt_row = wgtdata[wgt_idx]
            else:
                break

    for row in daydata:
        if(prev_row and prev_date !=wgt_row['date'] and row['date'] >= wgt_row['date']):  #match weight date
            prev_date = wgt_row['date']
            if(wgt_row['fenhong']>0 or wgt_row['songgu']>0 or wgt_row['zhuanzeng']>0 or (wgt_row['peigu']>0 and wgt_row['peigu_price']>0)):
                newprice = (prev_row['close'] - wgt_row['fenhong'] + wgt_row['peigu'] * wgt_row['peigu_price'])/(1+wgt_row['songgu']+wgt_row['zhuanzeng']+wgt_row['peigu'])
                wval = wval*prev_row['close']/newprice

            if(prev_wval != wval):
                row['weightdata'] = wgt_row

            if(wgt_idx < len(wgtdata)-1):
                wgt_idx += 1
                wgt_row = wgtdata[wgt_idx]

        prev_row = row  
        prev_wval = wval
        row['open'] *= wval
        row['high'] *= wval
        row['low'] *= wval
        row['close'] *= wval
        row['weight'] = wval
        houfuquan.append(row)

    return houfuquan

def getStockDayDataQianFuQuan(stockcode):
    fuquan = []
    daydata = getStockDayDataHouFuQuan(stockcode)
    if(not daydata):
        return False

    if(stockcode[:3] == 'sh0'): #index
        return daydata
    
    lastrow = daydata[len(daydata)-1]
    weight =  lastrow['weight']
    for row in daydata:
        row['open'] /= weight
        row['high'] /= weight
        row['low'] /= weight
        row['close'] /= weight
        fuquan.append(row)

    return fuquan

#取得最新的股票开盘日期
def getLastUpdateDate():
    info = getHq('sh000001')
    return info['date']

def getStockName(stockcode):

    if(stockcode == 'sh000001'):
        return '上证指数'
    elif(stockcode == 'sh000016'):
        return '上证５０'

    stocklist = {}
    if(not globals.data.get('stock.stocklist')):
        stocklist = getStockList()
        globals.data['stock.stocklist'] = stocklist
    else:
        stocklist = globals.data['stock.stocklist']

    return stocklist.get(stockcode)