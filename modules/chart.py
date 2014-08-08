
import datetime
import math
import random

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import indicators
from modules import globals
from modules import stock
from modules import utils

class Chart(QWidget): 

    def __init__(self):
        super().__init__()
        self.rightMarkwidth = 60
        self.bottomMarkHeight = 20
        self.indicatorHeight = 120
        self.indicatorCount = 3
        self.mainChartHeight = 500
        self.drawingrect = self.rect()
        self.chartwidth = self.drawingrect.width()
        self.base1 = self.mainChartHeight
        self.base2 = self.base1 + self.indicatorHeight
        self.base3 = self.base2 + self.indicatorHeight
        self.kmarginw = 10
        self.kmarginh = 20
        self.kwidth = 10
        self.fontsize = 10
        self.font = 'Tahoma'

        self.stockcode = None
        self.kdata = None
        self.kdispdata = None
        self.weightdata = None
        self.kdispcount = 0
        self.ktotalcount = 0
        self.mainIndicator = indicators.ma.Ma([60, 120])
        self.indicators = [indicators.amo.Amo(), indicators.macd.Macd(), indicators.kd.Kd()]
        self.indicatorpos = 0
        self.crossline = False
        self.helperlinepos = None
        self.helperlinekindex = None
        self.zoombase = 0.75
        self.zoom = self.zoombase
        self.lastzoom = self.zoom
        self.zoominmax = 3
        self.canzoomout = True
        self.mousepos = None
        self.mouseglobalpos = None
        self.daylist = ['一','二','三','四','五','六','日']

        self.pricehigh = 0
        self.pricelow = 100000
        self.pricerange = self.pricehigh - self.pricelow
        self.kdispstartindex = 0
        self.krange = self.mainChartHeight
        self.kleft = 0
        self.kindex = 0
        self.maintitle = []
        self.colorlist = []
        self.colorlist.append(QColor(8, 8, 225)) #blue
        self.colorlist.append(QColor(225, 8, 225))   #pink
        self.colorlist.append(QColor(188, 88, 8))  #yellow
        self.colorlist.append(QColor(88, 8, 188))  #purple
        self.colorlist.append(QColor(102, 102, 123))   #gray
        for i in range(0, 10):
            self.colorlist.append(QColor(random.randint(1, 255), random.randint(1, 255), random.randint(1, 255)))
        
        #realtime stockdata update
        self.rt_timer = QTimer()
        self.rt_timer.setInterval(3000)
        self.rt_data = {}
        self.rt_timer.timeout.connect(self.rtStockdataUpdate)
        self.rt_timer.start()
    
    def rtStockdataUpdate(self):
        if(not self.stockcode):
            return

        if(globals.realtime):
            if(self.rt_data.get('working')):
                return

            self.rt_data['working'] = True
            hqinfo = stock.getHq(self.stockcode)
            
            self.rt_data['data'] = hqinfo
            if(hqinfo['code'] != self.stockcode):
                return

            if(self.kdata[-1]['date'] == hqinfo['date']):
                self.kdata[-1] = hqinfo
            else:
                self.kdata.append(hqinfo)

            self.rt_data['working'] = False

            globals.mainwin.scrollbar.setMaximum(len(self.kdata))
            if(self.rt_data.get('status') != 'realtime' or self.rt_data.get('stockcode') != self.stockcode):
                globals.mainwin.scrollbar.triggerAction(QAbstractSlider.SliderToMaximum)
                self.rt_data['stockcode'] = self.stockcode
                self.rt_data['status'] = 'realtime'

            self.update()
            


    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        
        key = event.key()
        if(key == Qt.Key_Escape):
            globals.mainwin.removeDockWidget(globals.mainwin.dockOne)
            self.crossline = False
            self.helperlinepos = None
            self.update()
        elif(key == Qt.Key_Left):
            globals.mainwin.scrollbar.triggerAction(QAbstractSlider.SliderSingleStepSub)
        elif(key == Qt.Key_Right):
            globals.mainwin.scrollbar.triggerAction(QAbstractSlider.SliderSingleStepAdd)
        elif(key == Qt.Key_PageUp):
            globals.mainwin.scrollbar.triggerAction(QAbstractSlider.SliderPageStepSub)
        elif(key == Qt.Key_PageDown):
            globals.mainwin.scrollbar.triggerAction(QAbstractSlider.SliderPageStepAdd)
        elif(self.zoom < self.zoominmax and key == Qt.Key_Up):
            self.zoom *=1.1
            self.update()
        elif(self.canzoomout and key == Qt.Key_Down):
            self.zoom /=1.1
            self.update()
        elif(key == Qt.Key_Backspace):
            self.zoom = self.zoombase
            self.update()
        elif(key == Qt.Key_Space):
            if(not self.crossline):
                self.crossline = True
            else:
                self.crossline = False
            self.update()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if(event.button() == Qt.LeftButton):
            pass
        elif(event.button() == Qt.RightButton):
            if(not self.helperlinepos):
                self.helperlinepos = event.posF()
            else:
                self.helperlinepos = None

        self.mousepos = event.localPos()
        self.mouseglobalpos = event.globalPos()

        if(self.mousepos.y()>self.mainChartHeight and self.mousepos.y()<(self.mainChartHeight+self.indicatorHeight)):
            self.indicatorpos = 0
        elif(self.mousepos.y()>(self.mainChartHeight+self.indicatorHeight) and self.mousepos.y()<(self.mainChartHeight+self.indicatorHeight*2)):
            self.indicatorpos = 1
        elif(self.mousepos.y()>(self.mainChartHeight+self.indicatorHeight*2) and self.mousepos.y()<(self.mainChartHeight+self.indicatorHeight*3)):
            self.indicatorpos = 2

        self.update()
        globals.mainwin.removeDockWidget(globals.mainwin.dockOne)

    def mouseDoubleClickEvent(self, event):
        super().mouseMoveEvent(event)
        globals.mainwin.showStockInfoDlg()

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        self.mousepos = event.localPos()
        self.mouseglobalpos = event.globalPos()
        self.update()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        rect = self.rect()
        self.chartwidth = rect.width() - self.rightMarkwidth
        globals.mainwin.scrollbar.setPageStep(int(self.chartwidth/10)-1)

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.crossline = False

    def wheelEvent(self, event):
        super().wheelEvent(event)
        if(event.delta() >0 ): #up
            if(self.zoom < self.zoominmax):
                self.zoom *=1.1
                self.update()
        else:   #down
            if(self.canzoomout):
                self.zoom /=1.1
                self.update()            

    def paintEvent(self, event):
        painter = QPainter(self)
        
        if(not self.initAndDrawFrame(painter)):
            return
        #draw nothing when there is no data
        if(self.stockcode and self.kdata):
            pass
        else:
            return
        
        #update data for display
        self.handleDataUpdate()
        #calculate pricehigh, pricelow and pricerange
        self.calculatePriceRangeBasedOnKData()
        #update mainIndicator
        if(self.mainIndicator):
            utils.feedstockdata(self.mainIndicator)
            self.mainIndicator.updateDataAndPriceRange()

        #draw price and date grid
        self.drawPriceAndDateGrid(painter)
        #draw candle sticks
        self.drawCandleSticks(painter)
        #draw weight mark
        self.drawWeightMark(painter)

        #draw mainIndicator
        if(self.mainIndicator):
            self.mainIndicator.displayData(painter)

        #draw helper line
        self.drawHelperline(painter)

        #draw main chart title
        self.drawMainChartTitle(painter)
        
        #draw indicators
        cnt = 0
        for indicator in self.indicators[:self.indicatorCount]:
            base = self.base1 + cnt*self.indicatorHeight
            utils.feedstockdata(indicator)
            indicator.updateDataAndPriceRange()
            indicator.displayData(painter, base)
            cnt += 1

        #draw cross line
        self.drawCrossline(painter)
        #draw price and date tips
        self.drawPriceAndDateTips(painter)
        self.updateStockInfoDlg()


    def calculatePriceRangeBasedOnKData(self):
        #calculate pricehigh, pricelow and pricerange
        self.pricehigh = 0
        self.pricelow = self.kdispdata[0]['low']
        for row in self.kdispdata:
            if(row['high'] > self.pricehigh):
                self.pricehigh = row['high']
        
            if(row['low'] < self.pricelow):
                self.pricelow = row['low']

        self.pricerange = self.pricehigh - self.pricelow

    
    def initAndDrawFrame(self, painter):

        #resize viewport rect when dockOne(output panel) is visible
        self.drawingrect = self.rect()
        if(globals.mainwin.dockOne.isVisible()):
            docksize = globals.mainwin.dockOne.frameSize()
            self.drawingrect.setHeight(self.drawingrect.height() + docksize.height() + 6)

        self.mainChartHeight = int(self.drawingrect.height() / 2)
        self.indicatorHeight  = int((self.mainChartHeight - self.bottomMarkHeight)/3)
        if(self.indicatorHeight > 125):
            self.indicatorHeight = 150
            self.mainChartHeight = self.drawingrect.height() - self.indicatorHeight*3 - self.bottomMarkHeight

        if(self.indicatorCount == 2):
            self.mainChartHeight += self.indicatorHeight + 1
        elif(self.indicatorCount == 3):
            self.mainChartHeight += 1

        self.chartwidth = self.drawingrect.width() - self.rightMarkwidth
        self.base1 = self.mainChartHeight
        self.base2 = self.base1 + self.indicatorHeight
        self.base3 = self.base2 + self.indicatorHeight

        #set pen & font
        painter.setPen(QColor(128, 128, 128))
        painter.setFont(QFont(self.font, self.fontsize))
        QToolTip.setFont(QFont(self.font, self.fontsize))

        #fill background
        painter.fillRect(self.drawingrect, QColor(255,255,255))
        painter.drawRect(QRect(0, 0, self.drawingrect.width()-1, self.drawingrect.height()-1))
        #clear viewport
        if(globals.viewportclear):
            painter.setPen(QColor(255, 255, 255))
            painter.drawLine(1, self.drawingrect.height()-1, self.drawingrect.width()-1, self.drawingrect.height()-1)
            return False

        #draw frame
        painter.drawLine(0, self.base1, self.drawingrect.width(), self.base1)
        painter.drawLine(0, self.base2, self.drawingrect.width(), self.base2)
        painter.drawLine(0, self.base3, self.drawingrect.width(), self.base3)
        if(self.indicatorCount == 3):
            self.base3 = self.base3 + self.indicatorHeight
            painter.drawLine(0, self.base3, self.drawingrect.width(), self.base3)
        painter.setPen(QColor(255, 255, 255))
        painter.drawLine(1, self.drawingrect.height()-1, self.drawingrect.width()-1, self.drawingrect.height()-1)
        
        painter.setPen(QColor(128, 128, 128))
        painter.drawLine(self.chartwidth, 0, self.chartwidth, self.drawingrect.height())

        #draw active indicator:
        pen = QPen(QColor(0, 160, 216))
        pen.setStyle(Qt.SolidLine)
        pen.setWidth(2)
        painter.setPen(pen)  
        painter.drawLine(self.chartwidth, self.mainChartHeight+self.indicatorHeight*self.indicatorpos, self.chartwidth, self.mainChartHeight+self.indicatorHeight*(self.indicatorpos+1))
        
        return True

    def handleDataUpdate(self):
        self.ktotalcount = len(self.kdata)
        #calculate kwidth and kdispcount
        self.kwidth = 10
        self.kwidth = self.kwidth*self.zoom
        self.kdispcount = int((self.chartwidth - self.kmarginw*2)/self.kwidth) 

        self.kleft = self.chartwidth - self.kmarginw/2 -  self.kdispcount * self.kwidth
        #self.krange is the area for drawing candle sticks
        self.krange = self.mainChartHeight - self.kmarginh - 6 #6 is main chart bottom margin

        #normal zoom
        self.kdispstartindex = globals.mainwin.scrollbar.value() - self.kdispcount

        self.canzoomout = True
        if(self.kdispstartindex<0):
            self.kdispstartindex = 0
            self.canzoomout = False

        #zoom and move candle sticks based on helperline
        if(self.helperlinepos and self.helperlinekindex and self.lastzoom != self.zoom): #zoom
            if(self.kdispstartindex != 0):  #can zoom
                idxdiff = math.floor((self.helperlinepos.x()-self.kleft)/self.kwidth+0.5)
                self.kdispstartindex = self.helperlinekindex - idxdiff

                if(self.kdispstartindex + self.kdispcount > self.ktotalcount):
                    self.kdispstartindex = self.ktotalcount - self.kdispcount
                    globals.mainwin.scrollbar.setValue(self.ktotalcount)
                else:
                    if(self.kdispstartindex<0):
                        self.kdispstartindex = 0
                    globals.mainwin.scrollbar.setValue(self.kdispstartindex + self.kdispcount)

        if(self.helperlinepos and self.helperlinekindex): #move
            if(self.helperlinekindex < self.kdispstartindex): #left border
                self.kdispstartindex = self.helperlinekindex
                globals.mainwin.scrollbar.setValue(self.helperlinekindex+self.kdispcount)
            if((self.helperlinekindex + 1)>(self.kdispstartindex + self.kdispcount)):   #right border
                self.kdispstartindex = self.helperlinekindex + 1 - self.kdispcount
                globals.mainwin.scrollbar.setValue(self.helperlinekindex+1)
        
            #update helperlinepos
            idx = self.helperlinekindex - self.kdispstartindex
            posx = self.kleft + idx*self.kwidth
            self.helperlinepos.setX(posx)

        self.lastzoom = self.zoom

        self.kdispdata = self.kdata[self.kdispstartindex:self.kdispstartindex+self.kdispcount]

        #calculate helperlinekindex based on helperline pos
        if(self.helperlinepos):
            if(not self.helperlinekindex):
                kcnt = len(self.kdispdata)
                self.helperlinekindex = math.floor((self.helperlinepos.x()-self.kleft)/self.kwidth+0.5)
                if(self.helperlinekindex < 0):
                    self.helperlinekindex = 0
                if(self.helperlinekindex >= kcnt):
                    self.helperlinekindex = kcnt - 1
                
                #update self.helperlinepos, move it to the center of the candle stick
                kposx = self.kleft + self.helperlinekindex*self.kwidth
                self.helperlinepos.setX(kposx)
                self.helperlinekindex += self.kdispstartindex

        if(not self.helperlinepos):
            self.helperlinekindex = None

        #calculate index of self.kdispdata
        self.kindex = 0
        if(self.mousepos):
            kcnt = len(self.kdispdata)
            self.kindex = math.floor((self.mousepos.x()-self.kleft)/self.kwidth+0.5)
            if(self.kindex < 0):
                self.kindex = 0
            if(self.kindex >= kcnt):
                self.kindex = kcnt - 1

        #update scrollbar status
        if(self.ktotalcount>= self.kdispcount):
            globals.mainwin.scrollbar.setMinimum(self.kdispcount)
        else:
            globals.mainwin.scrollbar.setMinimum(self.ktotalcount)



        
    def drawPriceAndDateGrid(self, painter):
        #draw price grid
        painter.setPen(Qt.DotLine)
        for p in range(0, int(self.pricerange*1000)+8, int(self.pricerange*1000/8)):
            kposy_y = self.kmarginh + (1 - p/1000/self.pricerange) * self.krange
            painter.drawLine(0, kposy_y, self.chartwidth, kposy_y)
        
        painter.setPen(QColor(128, 128, 128))
        for p in range(0, int(self.pricerange*1000)+8, int(self.pricerange*1000/8)):
            kposy_y = self.kmarginh + (1 - p/1000/self.pricerange) * self.krange
            painter.drawLine(self.chartwidth, kposy_y, self.chartwidth+4, kposy_y)
            painter.drawText(self.chartwidth+8, kposy_y+5, '{:.2f}'.format((1-(kposy_y-self.kmarginh)/self.krange)*self.pricerange + self.pricelow))

        #draw date grid
        kcnt = len(self.kdispdata)
        for i in range(self.chartwidth, -200, -200):
            painter.drawLine(i, self.base3, i, self.drawingrect.height())
            idx = math.floor((i-self.kleft)/self.kwidth+0.5)
            if(idx < 0):
                idx = 0
            if(idx >= kcnt):
                idx = kcnt - 1

            date = self.kdispdata[idx]['date']
            if(i == self.chartwidth):
                date = '{}/{}'.format(date[4:6],date[6:])
            else:
                date = '{}/{}/{}'.format(date[:4],date[4:6],date[6:])
            painter.drawText(i+4, self.base3+16, date)


    def drawHelperline(self, painter):
        if(self.helperlinepos):
            pen = QPen(QColor(128, 128, 255))
            pen.setStyle(Qt.DashLine)
            painter.setPen(pen)
            if(self.zoom>0.3):
                painter.drawLine(QPointF(self.helperlinepos.x()-self.kwidth*0.45, 0), QPointF(self.helperlinepos.x()-self.kwidth*0.45, self.drawingrect.height()))
                painter.drawLine(QPointF(self.helperlinepos.x()+self.kwidth*0.45, 0), QPointF(self.helperlinepos.x()+self.kwidth*0.45, self.drawingrect.height()))
            else:
                painter.drawLine(QPointF(self.helperlinepos.x(), 0), QPointF(self.helperlinepos.x(), self.drawingrect.height()))
            painter.setPen(Qt.SolidLine)

            #draw date tips
            tipwidth = 72
            tipleft = self.helperlinepos.x()+self.kwidth*0.45
            if(tipleft + tipwidth>self.chartwidth):
                tipleft = self.helperlinepos.x() - self.kwidth*0.45 - tipwidth
            painter.fillRect(QRectF(QPointF(tipleft, self.base3+2), QPointF(tipleft+tipwidth, self.base3+19)), QColor(225,255,255))
            painter.drawRect(QRectF(QPointF(tipleft, self.base3+2), QPointF(tipleft+tipwidth, self.base3+19)))

            date = self.kdata[self.helperlinekindex]['date']
            date = '{}/{}/{}'.format(date[:4],date[4:6],date[6:])
            painter.drawText(tipleft+4, self.base3+16, date)


    def drawCandleSticks(self, painter):
        cnt = 0
        for row in self.kdispdata:
            kposx = self.kleft + cnt*self.kwidth
            kposy_open = self.kmarginh + (1 - (row['open'] - self.pricelow)/self.pricerange) * self.krange
            kposy_high = self.kmarginh + (1 - (row['high'] - self.pricelow)/self.pricerange) * self.krange
            kposy_low = self.kmarginh + (1 - (row['low'] - self.pricelow)/self.pricerange) * self.krange
            kposy_close = self.kmarginh + (1 - (row['close'] - self.pricelow)/self.pricerange) * self.krange
    
            kcolor = 'black'
            painter.setPen(QColor(0, 0, 0))
            if(row['close'] > row['open']):
                kcolor = 'red'
                painter.setPen(QColor(255, 0, 0))
            elif(row['close'] < row['open']):
                kcolor = 'green'
                painter.setPen(QColor(0, 128, 0))


            painter.drawLine(QPointF(kposx, kposy_high), QPointF(kposx, kposy_low))
            if(self.zoom>0.3):
                if(kcolor == 'black'):
                    painter.drawLine(QPointF(kposx-self.kwidth*0.3, kposy_open), QPointF(kposx+self.kwidth*0.3, kposy_close))
                elif(kcolor == 'green'):
                    painter.fillRect(QRectF(QPointF(kposx-self.kwidth*0.3, kposy_open), QPointF(kposx+self.kwidth*0.3, kposy_close)), QColor(0,128,0))
                    painter.drawRect(QRectF(QPointF(kposx-self.kwidth*0.3, kposy_open), QPointF(kposx+self.kwidth*0.3, kposy_close)))
                elif(kcolor == 'red'):
                    painter.fillRect(QRectF(QPointF(kposx-self.kwidth*0.3, kposy_close), QPointF(kposx+self.kwidth*0.3, kposy_open)), QColor(255,255,255))
                    painter.drawRect(QRectF(QPointF(kposx-self.kwidth*0.3, kposy_close), QPointF(kposx+self.kwidth*0.3, kposy_open)))
            
            cnt += 1

        #update title
        maintitle = '{}'.format(self.stockcode)
        stockname = stock.getStockName(self.stockcode)
        if(stockname):
            maintitle = '{} {}'.format(stockname, self.stockcode)
        
        self.maintitle = []
        self.maintitle.append({'x' : 3, 'y':15, 'text':maintitle, 'color':QColor(0, 0, 0)})


    def drawMainChartTitle(self, painter):
        for txtinfo in self.maintitle:
            painter.setPen(txtinfo['color'])
            painter.drawText(txtinfo['x'], txtinfo['y'], txtinfo['text'])

    def drawCrossline(self, painter):
        if(self.crossline and self.mousepos):
            painter.setPen(Qt.DashLine)
            painter.drawLine(QPointF(self.mousepos.x(), 0), QPointF(self.mousepos.x(), self.drawingrect.height()))
            painter.drawLine(QPointF(0, self.mousepos.y()), QPointF(self.drawingrect.width(), self.mousepos.y()))

    def drawPriceAndDateTips(self, painter):
        if(self.mousepos):
            painter.setPen(QColor(0, 0, 0))
            mousex = self.mousepos.x()
            mousey = self.mousepos.y()
            if(mousey < self.base1):
            #draw price tip
                painter.fillRect(QRectF(QPointF(self.chartwidth, mousey-14), QPointF(self.drawingrect.width()-1, mousey)), QColor(255,255,225))
                painter.drawRect(QRectF(QPointF(self.chartwidth, mousey-14), QPointF(self.drawingrect.width()-1, mousey)))
                painter.drawText(self.chartwidth+8, mousey-2, '{:.2f}'.format((1-(mousey-self.kmarginh)/self.krange)*self.pricerange + self.pricelow))

            #draw date tip
            if(mousex < self.chartwidth):
                tipwidth = 96
                tipleft = mousex
                if(mousex + tipwidth>self.chartwidth):
                    tipleft = mousex - tipwidth
                    
                painter.fillRect(QRectF(QPointF(tipleft, self.base3+2), QPointF(tipleft+tipwidth, self.base3+19)), QColor(255,255,225))
                painter.drawRect(QRectF(QPointF(tipleft, self.base3+2), QPointF(tipleft+tipwidth, self.base3+19)))
                date = self.kdispdata[self.kindex]['date']
                d = datetime.date(int(date[:4]),int(date[4:6]),int(date[6:]))
                day = self.daylist[d.weekday()]
                date = '{}/{}/{}({})'.format(date[:4],date[4:6],date[6:],day)
                painter.drawText(tipleft+4, self.base3+16, date)

    def updateStockInfoDlg(self):
        if(self.mousepos):
            labels=globals.mainwin.stockinfodlg.labels
            mousex = self.mousepos.x()
            mousey = self.mousepos.y()

            date = self.kdispdata[self.kindex]['date']
            d = datetime.date(int(date[:4]),int(date[4:6]),int(date[6:]))
            day = self.daylist[d.weekday()]
            date = '{}/{}/{}({})'.format(date[:4],date[4:6],date[6:],day)
            labels[0].setText(date)   #日期
            idx = self.kdispstartindex + self.kindex - 1
            if(idx < 0):
                idx = 0
            prev_row = self.kdata[idx]
            row = self.kdispdata[self.kindex]
            labels[1].setText('{:.2f}'.format((1-(mousey-self.kmarginh)/self.krange)*self.pricerange + self.pricelow))  #数值
            if(row['open']>prev_row['close']):
                labels[2].setStyleSheet('color: red')
            elif(row['open']<prev_row['close']):
                labels[2].setStyleSheet('color: green')
            else:
                labels[2].setStyleSheet('color: black')
            labels[2].setText('{:.2f}'.format(row['open']))  #开盘
            if(row['high']>prev_row['close']):
                labels[3].setStyleSheet('color: red')
            elif(row['high']<prev_row['close']):
                labels[3].setStyleSheet('color: green')
            else:
                labels[3].setStyleSheet('color: black')
            labels[3].setText('{:.2f}'.format(row['high']))  #最高
            if(row['low']>prev_row['close']):
                labels[4].setStyleSheet('color: red')
            elif(row['low']<prev_row['close']):
                labels[4].setStyleSheet('color: green')
            else:
                labels[4].setStyleSheet('color: black')
            labels[4].setText('{:.2f}'.format(row['low']))  #最低
            if(row['close']>prev_row['close']):
                labels[5].setStyleSheet('color: red')
                labels[7].setStyleSheet('color: red')
            elif(row['close']<prev_row['close']):
                labels[5].setStyleSheet('color: green')
                labels[7].setStyleSheet('color: green')
            else:
                labels[5].setStyleSheet('color: black')
                labels[7].setStyleSheet('color: black')
            labels[5].setText('{:.2f}'.format(row['close']))  #收盘
            labels[6].setText('{:,.0f}'.format(row['amount']))  #成交额
            zd = row['close'] - prev_row['close']
            zd_p = zd/prev_row['close']
            labels[7].setText('{:-.2f} {:-.2%}'.format(zd, zd_p))  #涨跌
            zhenf = (row['high'] - row['low'])/prev_row['close']
            labels[8].setText('{:.2%}'.format(zhenf))  #振幅                

    def drawWeightMark(self, painter):
        #draw weight mark
        if(self.weightdata and self.stockcode and self.stockcode[:3] != 'sh0'):
                painter.setPen(QColor(255, 0, 0))
                fm = painter.fontMetrics()
                txt = '●'
                txt_x = fm.width(txt)/2
                cnt = 0
                for row in self.kdispdata:
                    weight_row = row.get('weightdata')
                    if(weight_row):
                        posx = self.kleft + cnt*self.kwidth - txt_x
                        if(weight_row['date'] == row['date']):
                            posx = self.kleft + (cnt+1)*self.kwidth - txt_x

                        posy = self.base1 + 1
                        painter.drawText(posx, posy, txt)
                        
                        if(self.mousepos):
                            tips = []
                            tiptxt = ''
                            tips.append( '时间: ' + weight_row['date'])
                            if(weight_row['fenhong']>0):
                                tips.append("分红: 每10股分红{}元".format(weight_row['fenhong']*10))
                            if(weight_row['songgu']>0):
                                tips.append("送股: 每10股送{}股".format(weight_row['songgu']*10))
                            if(weight_row['zhuanzeng']>0):
                                tips.append("转赠: 每10股转赠{}股".format(weight_row['zhuanzeng']*10))
                            if(weight_row['peigu']>0 and weight_row['peigu_price']>0):
                                tips.append("配股: 每10股配{}股, 配股价{:.2f}元".format(weight_row['peigu']*10, weight_row['peigu_price']))

                            tiptxt = "\r\n".join(tips)
                            if(self.mousepos.x()>posx and self.mousepos.x()<(posx+2*txt_x) and self.mousepos.y()>(posy-10) and self.mousepos.y()<posy):
                                QToolTip.showText(self.mouseglobalpos, tiptxt, self, QRect(posx, posy-10, 2*txt_x, 10))

                    cnt += 1


    #helper function : draw marks
    def drawMarks(self, painter, markdispdata, marktext = 'M', markpos = 'above', markcolor = QColor(255, 0, 0)):

        fm = painter.fontMetrics()
        #draw marks
        painter.setPen(markcolor)
        txt = marktext
        txt_x = fm.width(txt)/2
        cnt = 0
        for row in self.kdispdata:
            mark_row = markdispdata[cnt]
            if(mark_row and mark_row.get('tip')):
                posx = self.kleft + cnt*self.kwidth - txt_x
                posy = self.base1 - 1
                if(markpos == 'above'):
                    posy = self.kmarginh + (1 - (row['high'] - self.pricelow)/self.pricerange) * self.krange - 11
                elif(markpos == 'below'):
                    posy = self.kmarginh + (1 - (row['low'] - self.pricelow)/self.pricerange) * self.krange + 26

                painter.drawText(posx, posy, txt)

                #mouse over tip:
                tiptxt = mark_row['tip']
                if(tiptxt and self.mousepos):
                    if(self.mousepos.x()>posx and self.mousepos.x()<(posx+2*txt_x) and self.mousepos.y()>(posy-10) and self.mousepos.y()<posy):
                        QToolTip.showText(self.mouseglobalpos, tiptxt, self, QRect(posx, posy-10, 2*txt_x, 10))


            cnt += 1

    #helper function
    def changeMainIndicator(self, newIndicator):
        self.mainIndicator = newIndicator
        self.update()
        
    #helper function
    def changeIndicator(self, newIndicator):
        pos = self.indicatorpos
        if(pos == 2):
            if(len(self.indicators)>2):
                self.indicators[2] = newIndicator
            else:
                self.indicators.append(newIndicator)
        elif(pos == 1):
            if(len(self.indicators)>1):
                self.indicators[1] = newIndicator
            else:
                self.indicators.append(newIndicator)
        else:
            self.indicators[0] = newIndicator

        self.update()