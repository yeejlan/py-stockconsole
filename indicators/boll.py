
import math
import random

from PyQt5.QtCore import *
from PyQt5.QtGui import *

from modules import globals
from modules import utils

class Boll:
    
    def __init__(self, ma_param = 20, std_param = 2):
        self.data = {}
        self.stockcode = None
        self.chart = None

        self.ma_param = ma_param
        self.std_param = std_param
        self.dispdata = {}
        self.chart = None
        self.lines = ['upper', 'mid', 'lower']
      

    def calculateData(self, stockdata):
        closedata = []
        for d in stockdata:
            closedata.append(d['close'])

        bolldata = {}
        for line in self.lines:
            bolldata[line] = []
            
        #step 1 计算均线&标准差
        cnt = 0
        totalvalue = None
        stdvals = []
        for data in closedata:
            if(cnt < self.ma_param - 1):
                bolldata['mid'].append(None)
                stdvals.append(None)
            else: #can calculate
                if(not totalvalue):
                    totalvalue = sum(closedata[:self.ma_param])
                else:
                    totalvalue = totalvalue + closedata[cnt] - closedata[cnt-self.ma_param]
            
                bolldata['mid'].append(totalvalue/self.ma_param)
                stdvals.append(math.sqrt(utils.variance(closedata[cnt+1-self.ma_param:cnt+1])))

            cnt +=1

        #计算upper&lower
        cnt = 0
        for midvalue in bolldata['mid']:
            if(midvalue == None):
                bolldata['upper'].append(None)
                bolldata['lower'].append(None)
            else:
                bolldata['upper'].append(midvalue + stdvals[cnt]*self.std_param)
                bolldata['lower'].append(midvalue - stdvals[cnt]*self.std_param)
                
            cnt +=1

        return bolldata

    def updateDataAndPriceRange(self):
        for line in self.lines:
            self.dispdata[line] = self.data[line][self.chart.kdispstartindex:self.chart.kdispstartindex+self.chart.kdispcount]
        
            for price in self.dispdata[line]:
                if(price == None):
                    continue

                if(price > self.chart.pricehigh):
                    self.chart.pricehigh = price
            
                if(price < self.chart.pricelow):
                    self.chart.pricelow = price

        self.chart.pricerange = self.chart.pricehigh - self.chart.pricelow
        

    def displayData(self, painter):
        linecnt = 0
        for line in self.lines:
            cnt = 0
            painter.setPen(self.chart.colorlist[linecnt])
            linecnt += 1
            prev_price = None
            for price in self.dispdata[line]:
                if(prev_price and prev_price != None):
                    kposx = self.chart.kleft + cnt*self.chart.kwidth
                    kposxprev = self.chart.kleft + (cnt-1)*self.chart.kwidth
                    kposy = self.chart.kmarginh + (1 - (price - self.chart.pricelow)/self.chart.pricerange) * self.chart.krange
                    kposyprev = self.chart.kmarginh + (1 - (prev_price - self.chart.pricelow)/self.chart.pricerange) * self.chart.krange
                    painter.drawLine(QPointF(kposxprev, kposyprev), QPointF(kposx, kposy))
                
                prev_price = price
                cnt += 1

        #update title
        if(self.dispdata['mid'][self.chart.kindex]):
            upper_val = self.dispdata['upper'][self.chart.kindex]
            mid_val = self.dispdata['mid'][self.chart.kindex]
            lower_val = self.dispdata['lower'][self.chart.kindex]
            upper_txt = ' UPPER {:.2f}'.format(upper_val)
            mid_txt = ' MID {:.2f}'.format(mid_val)
            lower_txt = ' LOWER {:.2f}'.format(lower_val)

            all_txt = self.chart.maintitle[0]['text'] + ' BOLL[{}, {}]'.format(self.ma_param, self.std_param)
            self.chart.maintitle[0]['text']  = all_txt

            posy = self.chart.maintitle[0]['y']
            fm = painter.fontMetrics()
            upper_x = self.chart.maintitle[0]['x'] + fm.width(all_txt)
            all_txt +=upper_txt
            mid_x = self.chart.maintitle[0]['x'] + fm.width(all_txt)
            all_txt +=mid_txt
            lower_x = self.chart.maintitle[0]['x'] + fm.width(all_txt)
            
            self.chart.maintitle.append({'x':upper_x, 'y':posy, 'text':upper_txt, 'color':self.chart.colorlist[0]})
            self.chart.maintitle.append({'x':mid_x, 'y':posy, 'text':mid_txt, 'color':self.chart.colorlist[1]})
            self.chart.maintitle.append({'x':lower_x, 'y':posy, 'text':lower_txt, 'color':self.chart.colorlist[2]})