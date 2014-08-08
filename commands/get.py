
from datetime import datetime
import queue
import random
import re
import threading
import time


from modules import stock
from modules import utils

subCommands = {
    'hq' : 'hq stock_code  取得当前的股票行情',
    'shanghai_a_count' : 'shanghai_a_count  得到沪A的股票总数'
}


desc = 'get subcommand  获取数据'

def run(subcmd, params):

    if(subcmd == 'shanghai_a_count'):
        return _getShanghaiACount()


    if(subcmd == 'hq'):
        if(len(params) != 1):
            utils.output('请给出股票代码', 'red')
            utils.output(subCommands['hq'])
            return
        
        stock_code = stock.normalizeStockCode(params[0])
        if(not stock_code):
            utils.output('股票代码错误', 'red')
            utils.output(subCommands['hq'])
            return
        
        return _getHq(stock_code)



def _getShanghaiACount():

    url = 'http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeStockCount?node=sh_a'
    
    err, u, content = utils.getWebContent(url)

    if(err):
        utils.output(err, 'red')
        return False

    content = content.decode('gbk')
    cnt = re.findall(r'"([0-9]+)"', content)
    utils.output(cnt)


def _getHq(stock_code):
    info = stock.getHq(stock_code)
    if(info):
        str = '{} {} {} {:-.2f}%'.format(info['code'], info['name'], info['price'], info['price_chg'])
        color = ''
        if info['price_chg'] >0 :
            color = 'red'
        elif info['price_chg'] < 0 :
            color = 'green'
  
        utils.output(str, color)