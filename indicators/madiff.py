
import math
import random

from PyQt5.QtCore import *
from PyQt5.QtGui import *

from modules import globals
from modules import utils
from indicators import ma

class MaDiff:
    
    def __init__(self, mashort = 60, malong = 120):
        self.stockcode = None
        self.data = []
        self.chart = None

        self.mashort = mashort
        self.malong = malong
        self.dispdata = []
        self.valuerange = 100
        self.valuehigh = -100000000000000000000
        self.valuelow = 1000000000000000000000
        

    def calculateData(self, stockdata):
        closedata = []
        for d in stockdata:
            closedata.append(d['close'])

        madiffdata = []
            
        #step 1 计算ma
        myma = ma.Ma([self.mashort, self.malong])
        madata = myma.calculateData(stockdata)
        
        #step 2 计算madiff
        cnt = 0
        for malongval in madata.get(self.malong):
            if(malongval == None):
                madiffdata.append(None)
            else:
                mashortval = madata.get(self.mashort)[cnt]
                madiff = (mashortval - malongval)/closedata[cnt]
                madiffdata.append(madiff)

            cnt += 1

        return madiffdata
        

    def updateDataAndPriceRange(self):
        self.dispdata = self.data[self.chart.kdispstartindex:self.chart.kdispstartindex+self.chart.kdispcount]
      
        self.valuehigh = -100000000000000000000
        self.valuelow = 1000000000000000000000
        for value in self.dispdata:
            if(value == None):
                continue

            if(value > self.valuehigh):
                self.valuehigh = value
        
            if(value < self.valuelow):
                self.valuelow = value
    
        self.valuerange = self.valuehigh - self.valuelow
        if(self.valuerange == 0):
            self.valuerange = 20

        

    def displayData(self, painter, base):
        bottom = 6
        bar_range = self.chart.indicatorHeight-self.chart.kmarginh-bottom
        
        #draw grid
        vals = [0, self.valuelow, self.valuehigh]
        for v in vals:
            painter.setPen(Qt.DotLine)
            posy = base + self.chart.kmarginh + (1 -(v-self.valuelow)/self.valuerange) *bar_range
            painter.drawLine(0, posy, self.chart.chartwidth, posy)
        
        painter.setPen(QColor(128, 128, 128))
        for v in vals:
            posy = base + self.chart.kmarginh + (1 -(v-self.valuelow)/self.valuerange) *bar_range
            painter.drawLine(self.chart.chartwidth, posy, self.chart.chartwidth+4, posy)
            painter.drawText(self.chart.chartwidth+8, posy+5, '{:.2f}'.format(v))

        #draw title #1
        all_txt = 'MADIFF[{}, {}] '.format(self.mashort, self.malong)
        painter.setPen(QColor(0, 0, 0))
        painter.drawText(3, base+15, all_txt)   
        fm = painter.fontMetrics()

        #draw title #2
        if(self.dispdata[self.chart.kindex]):
            txt_posx = 3 + fm.width(all_txt)
            txt = ' {:.2f}'.format(self.dispdata[self.chart.kindex])
            painter.drawText(txt_posx, base+15, txt)
            all_txt += txt

        #draw madiff
        cnt = 0
        kposy0 = base + self.chart.kmarginh + (1 -(0-self.valuelow)/self.valuerange) *bar_range
        for value in self.dispdata:
            if(value and value != None):
                kposx = self.chart.kleft + cnt*self.chart.kwidth
                kposy = base + self.chart.kmarginh + (1 -(value-self.valuelow)/self.valuerange) *bar_range
                if(value>=0):
                    painter.setPen(QColor(255, 0, 0)) 
                else:
                    painter.setPen(QColor(0, 128, 0)) 
                painter.drawLine(QPointF(kposx, kposy0), QPointF(kposx, kposy))

            cnt += 1



        #draw value tip
        painter.setPen(QColor(0, 0, 0))
        if(self.chart.mousepos):
            mousey = self.chart.mousepos.y()
            if(mousey > base and mousey< base+self.chart.indicatorHeight-bottom):
                painter.fillRect(QRectF(QPointF(self.chart.chartwidth, mousey-14), QPointF(self.chart.drawingrect.width()-1, mousey)), QColor(255,255,225))
                painter.drawRect(QRectF(QPointF(self.chart.chartwidth, mousey-14), QPointF(self.chart.drawingrect.width()-1, mousey)))

                value = (1-(mousey-base - self.chart.kmarginh)/bar_range)*self.valuerange + self.valuelow
                painter.drawText(self.chart.chartwidth+8, mousey-2, '{:.2f}'.format(value))