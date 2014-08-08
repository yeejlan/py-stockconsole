
import math
import random

from PyQt5.QtCore import *
from PyQt5.QtGui import *

from modules import globals
from modules import utils

class Amo:
    
    def __init__(self):
        self.chart = None
        self.stockcode = None
        self.data = None

        self.dispdata = None
        self.amodispcolor = None
        self.maxval = 0
        self.minval = 100000000000000
        self.amorange = self.minval

    def calculateData(self, stockdata):
        amodata = {}
        amodata['amount'] = []
        amodata['color'] = []

        cnt = 0
        prev_row = None
        for row in stockdata:
            amodata['amount'].append(row['amount'])
            kcolor = 'black'
            if(row['close'] > row['open']):
                kcolor = 'red'
            elif(row['close'] < row['open']):
                kcolor = 'green'

            amodata['color'].append(kcolor)
            if(prev_row and kcolor == 'black'):
                if(prev_row['close'] > row['close']):
                    amodata['color'][cnt] = 'green'
                else:
                    amodata['color'][cnt] = 'red'

            prev_row = row
            cnt += 1

        return amodata

    def updateDataAndPriceRange(self):
        self.dispdata = self.data['amount'][self.chart.kdispstartindex:self.chart.kdispstartindex+self.chart.kdispcount]
        self.amodispcolor = self.data['color'][self.chart.kdispstartindex:self.chart.kdispstartindex+self.chart.kdispcount]
        
        self.maxval = 0
        self.minval = self.dispdata[0]
        for amoval in self.dispdata:
            if(amoval > self.maxval):
                self.maxval = amoval
        
            if(amoval < self.minval):
                self.minval = amoval

        self.amorange = self.maxval
        

    def displayData(self, painter, base):
        bottom = 2
        bar_range = self.chart.indicatorHeight-self.chart.kmarginh-bottom

        #draw grid
        for p in range(int(self.amorange*1000/3), int(self.amorange*1000)+3, int(self.amorange*1000/3)):
            painter.setPen(Qt.DotLine)
            posy = base + self.chart.kmarginh + (1 - p/1000/self.amorange) * bar_range
            painter.drawLine(0, posy, self.chart.chartwidth, posy)

        painter.setPen(QColor(128, 128, 128))
        for p in range(int(self.amorange*1000/3), int(self.amorange*1000)+3, int(self.amorange*1000/3)):
            posy = base + self.chart.kmarginh + (1 - p/1000/self.amorange) * bar_range
            painter.drawLine(self.chart.chartwidth, posy, self.chart.chartwidth+4, posy)
            painter.drawText(self.chart.chartwidth+8, posy+5, '{:,.0f}'.format((1-(posy-self.chart.kmarginh-base)/bar_range)*self.amorange))
    
        #draw amount
        cnt = 0
        for amoval in self.dispdata:
            posx = self.chart.kleft + cnt*self.chart.kwidth
            posy = base + self.chart.kmarginh + (1.0 - amoval/self.amorange) * bar_range
  
            if(self.amodispcolor[cnt] == 'red'):
                painter.setPen(QColor(255, 0, 0))
            else:
                painter.setPen(QColor(0, 128, 0))

            if(self.chart.zoom>0.3):
                painter.drawRect(QRectF(QPointF(posx-self.chart.kwidth*0.3, posy), QPointF(posx+self.chart.kwidth*0.3, base+self.chart.indicatorHeight-bottom)))
                if(self.amodispcolor[cnt] == 'green'):
                    painter.fillRect(QRectF(QPointF(posx-self.chart.kwidth*0.3, posy), QPointF(posx+self.chart.kwidth*0.3, base+self.chart.indicatorHeight-bottom)), QColor(0, 128, 0))
            else:
                painter.drawLine(QPointF(posx, posy), QPointF(posx, base+self.chart.indicatorHeight-bottom))

            cnt += 1

        #draw title
        painter.setPen(QColor(0, 0, 0))
        painter.drawText(3, base+15, 'AMO {:,.0f}'.format(self.dispdata[self.chart.kindex]))

        #draw value tip
        if(self.chart.mousepos):
            mousey = self.chart.mousepos.y()
            if(mousey > base and mousey< base+self.chart.indicatorHeight-bottom):
                painter.fillRect(QRectF(QPointF(self.chart.chartwidth, mousey-14), QPointF(self.chart.drawingrect.width()-1, mousey)), QColor(255,255,225))
                painter.drawRect(QRectF(QPointF(self.chart.chartwidth, mousey-14), QPointF(self.chart.drawingrect.width()-1, mousey)))

                value = (1-(mousey-base - self.chart.kmarginh)/bar_range)*self.amorange
                painter.drawText(self.chart.chartwidth+8, mousey-2, '{:,.0f}'.format(value))