
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

desc = 'test  临时测试命令'

subCommands = {}


def run(subcmd, params):

    stockcode = 'sh600603'
    wd = stock.getStockWeightData(stockcode)
    print(wd)
    #stockdata = stock.getStockDayDataQianFuQuan(stockcode)
            


