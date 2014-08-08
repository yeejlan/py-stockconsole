
import math
import random

from PyQt5.QtCore import *
from PyQt5.QtGui import *

from modules import globals
from modules import utils

class Kd:
    
    def __init__(self, rsv_param = 9):
        self.chart = None
        self.stockcode = None
        self.data = {}

        self.rsv_param = rsv_param
        self.dispdata = {}
        self.lines = ['K', 'D']
        self.valuerange = 100
      

    def calculateData(self, stockdata):
        closedata = []
        highdata = []
        lowdata = []
        for d in stockdata:
            closedata.append(d['close'])
            highdata.append(d['high'])
            lowdata.append(d['low'])

        kddata = {}
        for line in self.lines:
            kddata[line] = []
            
        #step 1 计算rsv
        cnt = 0
        rsvvals = []
        for data in closedata:
            if(cnt < self.rsv_param - 1):
                rsvvals.append(None)
            else: #can calculate
                highvals = highdata[cnt+1-self.rsv_param:cnt+1]
                lowvals = lowdata[cnt+1-self.rsv_param:cnt+1]
                lowval = min(lowvals)
                highval = max(highvals)
                rev = 100
                if(highval-lowval != 0):
                    rsv = 100*(data-lowval)/(highval-lowval)
                rsvvals.append(rsv)

            cnt +=1

        #计算k&d
        cnt = 0
        prev_k = 50
        prev_d = 50
        for rsv in rsvvals:
            if(rsv == None):
                kddata['K'].append(None)
                kddata['D'].append(None)
            else:
                k = prev_k*2/3 + rsv/3
                d = prev_d*2/3 + k/3
                kddata['K'].append(k)
                kddata['D'].append(d)
                prev_k = k
                prev_d = d

            cnt +=1        

        return kddata
        

    def updateDataAndPriceRange(self):
        for line in self.lines:
            self.dispdata[line] = self.data[line][self.chart.kdispstartindex:self.chart.kdispstartindex+self.chart.kdispcount]
        

    def displayData(self, painter, base):
        bottom = 0
        bar_range = self.chart.indicatorHeight-self.chart.kmarginh-bottom
        
        #draw grid
        vals = [20, 50, 80]
        for v in vals:
            painter.setPen(Qt.DotLine)
            posy = base + self.chart.kmarginh + (1 - v/self.valuerange) * bar_range
            painter.drawLine(0, posy, self.chart.chartwidth, posy)
        
        painter.setPen(QColor(128, 128, 128))
        for v in vals:
            posy = base + self.chart.kmarginh + (1 - v/self.valuerange) * bar_range
            painter.drawLine(self.chart.chartwidth, posy, self.chart.chartwidth+4, posy)
            painter.drawText(self.chart.chartwidth+8, posy+5, '{:.2f}'.format(v))

        #draw title #1
        all_txt = 'KD[{}, 3, 3]'.format(self.rsv_param)
        painter.setPen(QColor(0, 0, 0))
        painter.drawText(3, base+15, all_txt)   
        fm = painter.fontMetrics()

        #draw kd
        linecnt = 0
        for line in self.lines:
            cnt = 0
            painter.setPen(self.chart.colorlist[linecnt])
            linecnt += 1
            prev_value = None
            for value in self.dispdata[line]:
                if(prev_value and prev_value != None):
                    kposx = self.chart.kleft + cnt*self.chart.kwidth
                    kposxprev = self.chart.kleft + (cnt-1)*self.chart.kwidth
                    kposy = base + self.chart.kmarginh + (1 - value/self.valuerange) *bar_range
                    kposyprev = base + self.chart.kmarginh +(1 - prev_value /self.valuerange) * bar_range
                    painter.drawLine(QPointF(kposxprev, kposyprev), QPointF(kposx, kposy))
                
                prev_value = value
                cnt += 1

            #draw title #2
            if(self.dispdata[line][self.chart.kindex]):
                txt_posx = 3 + fm.width(all_txt)
                txt = ' {} {:.2f}'.format(line, self.dispdata[line][self.chart.kindex])
                painter.drawText(txt_posx, base+15, txt)
                all_txt += txt

        #draw value tip
        painter.setPen(QColor(0, 0, 0))
        if(self.chart.mousepos):
            mousey = self.chart.mousepos.y()
            if(mousey > base and mousey< base+self.chart.indicatorHeight-bottom):
                painter.fillRect(QRectF(QPointF(self.chart.chartwidth, mousey-14), QPointF(self.chart.drawingrect.width()-1, mousey)), QColor(255,255,225))
                painter.drawRect(QRectF(QPointF(self.chart.chartwidth, mousey-14), QPointF(self.chart.drawingrect.width()-1, mousey)))

                value = (1-(mousey-base - self.chart.kmarginh)/bar_range)*self.valuerange
                painter.drawText(self.chart.chartwidth+8, mousey-2, '{:.2f}'.format(value))