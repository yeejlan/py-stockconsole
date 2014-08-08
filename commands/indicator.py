
import datetime
import os
import sys
import queue
import threading
import time
import struct
import urllib.request

import indicators
from modules import db
from modules import globals
from modules import stock
from modules import utils

desc = 'indicator subcommand  更换指标'

subCommands ={
'clear' : 'clear  清除主图指标',
'ma' : 'ma  显示MA(60, 120)指标',
'ma250' : 'ma250  显示MA(120, 250)指标',
'ma60' : 'ma60  显示MA(20, 60)指标',
'ma20' : 'ma20  显示MA(10, 20)指标',
'ma10' : 'ma10  显示MA(3, 10)指标',
'boll' : 'boll  显示boll指标',
'di' : 'di  显示di指标',
'macd' : 'macd  显示macd指标',
'kd' : 'kd  显示kd指标',
'madiff' : 'madiff  显示madiff指标',
'amo' : 'amo  显示amo指标',
}

def run(subcmd, params):
    chart = globals.mainwin.chart
    if(subcmd == 'clear'):
        chart.changeMainIndicator(None)

    elif(subcmd == 'ma'):
        chart.changeMainIndicator(indicators.ma.Ma([60, 120]))

    elif(subcmd == 'ma250'):
        chart.changeMainIndicator(indicators.ma.Ma([120, 250]))

    elif(subcmd == 'ma60'):
        chart.changeMainIndicator(indicators.ma.Ma([20, 60]))

    elif(subcmd == 'ma20'):
        chart.changeMainIndicator(indicators.ma.Ma([10, 20]))

    elif(subcmd == 'ma10'):
        chart.changeMainIndicator(indicators.ma.Ma([3, 10]))

    elif(subcmd == 'boll'):
        chart.changeMainIndicator(indicators.boll.Boll(20, 2))

    elif(subcmd == 'di'):
        chart.changeMainIndicator(indicators.di.Di())

    elif(subcmd == 'macd'):
        chart.changeIndicator(indicators.macd.Macd())

    elif(subcmd == 'kd'):
        chart.changeIndicator(indicators.kd.Kd())

    elif(subcmd == 'madiff'):
        chart.changeIndicator(indicators.madiff.MaDiff())

    elif(subcmd == 'amo'):
        chart.changeIndicator(indicators.amo.Amo())