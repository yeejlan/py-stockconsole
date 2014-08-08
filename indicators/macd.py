
import math
import random

from PyQt5.QtCore import *
from PyQt5.QtGui import *

from modules import globals
from modules import utils

class Macd:
    
    def __init__(self):
        self.stockcode = None
        self.data = {}
        self.chart = None

        self.dea_param = 9
        self.short_ema = 12
        self.long_ema = 26
        self.dispdata = {}
        self.lines = ['DIF', 'DEA', 'BAR']
        self.valuerange = 100
        self.valuehigh = 0
        self.valuelow = 10000000000000000
      

    def calculateData(self, stockdata):
        closedata = []
        for d in stockdata:
            closedata.append(d['close'])

        macddata = {}
        for line in self.lines:
            macddata[line] = []
            
        #step 1 ema short
        cnt = 0
        emashortvals = []
        for data in closedata:
            if(cnt < self.short_ema - 1):
                emashortvals.append(None)
            elif(cnt == self.short_ema - 1):  #day self.short_ema
                closeval = sum(closedata[:cnt+1])
                dival = closeval/self.short_ema
                emashortvals.append(dival)
            else: #day after self.short_ema
                di = closedata[cnt]
                val = emashortvals[cnt-1]*(self.short_ema-1)/(self.short_ema+1)+di*2/(self.short_ema+1)
                emashortvals.append(val)

            cnt +=1

        #step 2 ema long
        cnt = 0
        emalongvals = []
        for data in closedata:
            if(cnt < self.long_ema - 1):
                emalongvals.append(None)
            elif(cnt == self.long_ema - 1):  #day self.long_ema
                closeval = sum(closedata[:cnt+1])
                dival = closeval/self.long_ema
                emalongvals.append(dival)
            else: #day after self.long_ema
                di = closedata[cnt]
                val = emalongvals[cnt-1]*(self.long_ema-1)/(self.long_ema+1)+di*2/(self.long_ema+1)
                emalongvals.append(val)

            cnt +=1


        #计算dif
        cnt = 0
        for emalong in emalongvals:
            if(emalong == None):
                macddata['DIF'].append(None)
            else:
                dif =  emashortvals[cnt] - emalong
                macddata['DIF'].append(dif)

            cnt +=1

        #计算DEA
        cnt = 0
        difcnt = 0
        for dif in macddata['DIF']:
            if(dif == None):
                macddata['DEA'].append(None)
            elif(difcnt< self.dea_param - 1):
                macddata['DEA'].append(None)
                difcnt += 1
            elif(difcnt == self.dea_param - 1):
                dea = sum(macddata['DIF'][cnt-self.dea_param+1:cnt+1])/self.dea_param
                macddata['DEA'].append(dea)
                difcnt += 1
            else:
                dea = macddata['DEA'][cnt-1]*(self.dea_param-1)/(self.dea_param+1)+macddata['DIF'][cnt]*2/(self.dea_param+1)
                macddata['DEA'].append(dea)

            cnt +=1

        #计算bar
        cnt = 0
        difcnt = 0
        for dea in macddata['DEA']:
            if(dea == None):
                macddata['BAR'].append(None)
            else:
                macd = 2*(macddata['DIF'][cnt] - dea)
                macddata['BAR'].append(macd)

            cnt +=1

        return macddata

    def updateDataAndPriceRange(self):
        self.valuehigh = 0
        self.valuelow = 1000000000000000000000
        for line in self.lines[:3]:
            self.dispdata[line] = self.data[line][self.chart.kdispstartindex:self.chart.kdispstartindex+self.chart.kdispcount]

            for value in self.dispdata[line]:
                if(value == None):
                    continue

                if(value > self.valuehigh):
                    self.valuehigh = value
            
                if(value < self.valuelow):
                    self.valuelow = value
        
            self.valuerange = self.valuehigh - self.valuelow

    def displayData(self, painter, base):
        bottom = 6
        bar_range = self.chart.indicatorHeight-self.chart.kmarginh-bottom
        
        #draw grid
        for value in [self.valuelow, 0, self.valuehigh]:
            painter.setPen(Qt.DotLine)
            posy = base + self.chart.kmarginh + (1 -(value-self.valuelow)/self.valuerange) *bar_range
            painter.drawLine(0, posy, self.chart.chartwidth, posy)
        
        painter.setPen(QColor(128, 128, 128))
        for value in [self.valuelow, 0, self.valuehigh]:
            posy = base + self.chart.kmarginh + (1 -(value-self.valuelow)/self.valuerange) *bar_range
            painter.drawLine(self.chart.chartwidth, posy, self.chart.chartwidth+4, posy)
            painter.drawText(self.chart.chartwidth+8, posy+5, '{:.2f}'.format(value))

        #draw title #1
        all_txt = 'MACD[{}, {}, {}]'.format(self.short_ema, self.long_ema, self.dea_param)
        painter.setPen(QColor(0, 0, 0))
        painter.drawText(3, base+15, all_txt)   
        fm = painter.fontMetrics()

        #draw bar(aka macd)
        cnt = 0
        kposy0 = base + self.chart.kmarginh + (1 -(0-self.valuelow)/self.valuerange) *bar_range
        for value in self.dispdata['BAR']:
            if(value and value != None):
                kposx = self.chart.kleft + cnt*self.chart.kwidth
                kposy = base + self.chart.kmarginh + (1 -(value-self.valuelow)/self.valuerange) *bar_range
                if(value>=0):
                    painter.setPen(QColor(255, 0, 0)) 
                else:
                    painter.setPen(QColor(0, 128, 0)) 
                painter.drawLine(QPointF(kposx, kposy0), QPointF(kposx, kposy))

            cnt += 1

        #draw dif and dea
        linecnt = 0
        for line in self.lines[:2]:
            cnt = 0
            painter.setPen(self.chart.colorlist[linecnt])
            linecnt += 1
            prev_value = None
            for value in self.dispdata[line]:
                if(prev_value and prev_value != None):
                    kposx = self.chart.kleft + cnt*self.chart.kwidth
                    kposxprev = self.chart.kleft + (cnt-1)*self.chart.kwidth
                    kposy = base + self.chart.kmarginh + (1 -(value-self.valuelow)/self.valuerange) *bar_range
                    kposyprev = base + self.chart.kmarginh +(1 - (prev_value-self.valuelow) /self.valuerange) * bar_range
                    painter.drawLine(QPointF(kposxprev, kposyprev), QPointF(kposx, kposy))
                
                prev_value = value
                cnt += 1

            #draw title #2
            if(self.dispdata[line][self.chart.kindex]):
                txt_posx = 3 + fm.width(all_txt)
                txt = ' {} {:.2f}'.format(line, self.dispdata[line][self.chart.kindex])
                painter.drawText(txt_posx, base+15, txt)
                all_txt += txt

        #draw title #3
        if(self.dispdata['BAR'][self.chart.kindex]):
            painter.setPen(QColor(0, 0, 0))
            txt_posx = 3 + fm.width(all_txt)
            txt = ' {} {:.2f}'.format('BAR', self.dispdata['BAR'][self.chart.kindex])
            painter.drawText(txt_posx, base+15, txt)

        #draw value tip
        if(self.chart.mousepos):
            mousey = self.chart.mousepos.y()
            if(mousey > base and mousey< base+self.chart.indicatorHeight-bottom):
                painter.fillRect(QRectF(QPointF(self.chart.chartwidth, mousey-14), QPointF(self.chart.drawingrect.width()-1, mousey)), QColor(255,255,225))
                painter.drawRect(QRectF(QPointF(self.chart.chartwidth, mousey-14), QPointF(self.chart.drawingrect.width()-1, mousey)))

                value = (1-(mousey-base - self.chart.kmarginh)/bar_range)*self.valuerange + self.valuelow
                painter.drawText(self.chart.chartwidth+8, mousey-2, '{:.2f}'.format(value))