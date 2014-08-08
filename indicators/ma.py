
import random

from PyQt5.QtCore import *
from PyQt5.QtGui import *

from modules import globals

class Ma:
    
    def __init__(self, paramlist):
        self.chart = None
        self.stockcode = None
        self.data = {}

        self.paramlist = paramlist
        self.dispdata = {}
        

    def calculateData(self, stockdata):
        closedata = []
        for d in stockdata:
            closedata.append(d['close'])

        madata = {}
        for param in self.paramlist:
            madata[param] = []
            cnt = 0
            totalvalue = None
            for data in closedata:
                if(cnt < param - 1):
                    madata[param].append(None)
                else: #can calculate
                    if(not totalvalue):
                        totalvalue = sum(closedata[:param])
                    else:
                        totalvalue = totalvalue + closedata[cnt] - closedata[cnt-param]
                
                    madata[param].append(totalvalue/param)

                cnt +=1

        return madata

    def updateDataAndPriceRange(self):
        for param in self.paramlist:
            self.dispdata[param] = self.data[param][self.chart.kdispstartindex:self.chart.kdispstartindex+self.chart.kdispcount]
        
            for ma_price in self.dispdata[param]:
                if(ma_price == None):
                    continue

                if(ma_price > self.chart.pricehigh):
                    self.chart.pricehigh = ma_price
            
                if(ma_price < self.chart.pricelow):
                    self.chart.pricelow = ma_price

        self.chart.pricerange = self.chart.pricehigh - self.chart.pricelow
        

    def displayData(self, painter):
        paramcnt = 0
        all_txt = self.chart.maintitle[0]['text'] + ' MA{}'.format(self.paramlist)
        self.chart.maintitle[0]['text'] = all_txt
        txt_posy = self.chart.maintitle[0]['y']
        fm = painter.fontMetrics()

        for param in self.paramlist:
            cnt = 0
            painter.setPen(self.chart.colorlist[paramcnt])
            prev_ma_price = None
            for ma_price in self.dispdata[param]:
                if(prev_ma_price and prev_ma_price != None):
                    kposx = self.chart.kleft + cnt*self.chart.kwidth
                    kposxprev = self.chart.kleft + (cnt-1)*self.chart.kwidth
                    kposy = self.chart.kmarginh + (1 - (ma_price - self.chart.pricelow)/self.chart.pricerange) * self.chart.krange
                    kposyprev = self.chart.kmarginh + (1 - (prev_ma_price - self.chart.pricelow)/self.chart.pricerange) * self.chart.krange
                    painter.drawLine(QPointF(kposxprev, kposyprev), QPointF(kposx, kposy))
                
                prev_ma_price = ma_price
                cnt += 1

            #update title
            if(self.dispdata[param][self.chart.kindex]):
                txt_posx = self.chart.maintitle[0]['x'] + fm.width(all_txt)
                ma_txt = ' MA{} {:.2f}'.format(param, self.dispdata[param][self.chart.kindex])
                all_txt += ma_txt
                self.chart.maintitle.append({'x':txt_posx, 'y':txt_posy, 'text':ma_txt, 'color':self.chart.colorlist[paramcnt]})

            paramcnt += 1