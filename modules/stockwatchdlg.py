
import pickle

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from modules import globals
from modules import utils
from modules import stock
from commands import viewport

class StockWatchDlg(QDialog):

    def __init__(self, parent):
        super().__init__(parent)
        self.resize(396, 518)
        self.setWindowTitle('Stock Watch List')
        self.setWindowFlags(Qt.MSWindowsFixedSizeDialogHint)
        self.setStyleSheet('selection-background-color: #6688dd; selection-color: black; font: "Tahoma"; font-size: 10pt')
      
        vbox = QVBoxLayout()
        vbox.setSpacing(0)
        vbox.setContentsMargins(0, 0, 0, 0)

        self.tbWatchList = QTableWidget()      #QTableWidget
        self.tbWatchList.setRowCount(50)
        self.tbWatchList.setColumnCount(3)
        vbox.addWidget(self.tbWatchList)

        self.setLayout(vbox)
        self.setWindowIcon(QIcon('./images/console.png'))

        hview = QHeaderView(Qt.Horizontal)
        hview.setDefaultSectionSize(100)
        self.tbWatchList.setHorizontalHeader(hview)
        self.tbWatchList.setColumnWidth(2, 150)
        vview = QHeaderView(Qt.Vertical)
        vview.setDefaultSectionSize(25)
        self.tbWatchList.setVerticalHeader(vview)      

        for i in range(0, 50):
            item = QTableWidgetItem('')
            item.setFlags(Qt.ItemIsSelectable|Qt.ItemIsEnabled)
            self.tbWatchList.setItem(i, 1, item)

        #load form file
        self.loadAllItems()

        self.tbWatchList.cellDoubleClicked.connect(self.handleCellDoubleClicked)
        self.tbWatchList.cellChanged.connect(self.handleCellChanged)

    def handleCellDoubleClicked(self, row, column):
        if(column == 1 and self.tbWatchList.item(row, column)):
            item = self.tbWatchList.item(row, 0)
            if(item):
                stockcode = item.data(Qt.DisplayRole)
                if(stockcode):
                    try:
                        viewport.run('show', [stockcode])
                    except:
                        pass

    def handleCellChanged(self, row, column):
        if(column == 0):
            item0 =  self.tbWatchList.item(row, 0)
            stockcode = item0.data(Qt.DisplayRole)
            if(stockcode):
                norcode = stock.normalizeStockCode(stockcode)
                stockname = stock.getStockName(norcode)
                if(norcode):
                    if(norcode != stockcode):
                        item0 = QTableWidgetItem(norcode)
                        self.tbWatchList.setItem(row, 0, item0)
                    
                    if(stockname):
                        item1 = QTableWidgetItem(stockname)
                    else:
                        item1 = QTableWidgetItem('')

                    item1.setFlags(Qt.ItemIsSelectable|Qt.ItemIsEnabled)
                    self.tbWatchList.setItem(row, 1, item1) 

            self.saveAllItems()

        if(column == 2):
            item2 =  self.tbWatchList.item(row, 2)
            if(item2 and item2.data(Qt.DisplayRole)):
                self.saveAllItems()
                

            
    def saveAllItems(self):
        watchlist = []
        filename = globals.datapath + '/watchlist.dat'
        for i in range(0, 50):
            item0 = self.tbWatchList.item(i, 0)
            item1 = self.tbWatchList.item(i, 1)
            item2 = self.tbWatchList.item(i, 2)
            d0 = d1 = d2 = ''
            if(item0):
                d0 = item0.data(Qt.DisplayRole)
            if(d0 and item1):
                d1 = item1.data(Qt.DisplayRole)
            if(item2):
                d2 = item2.data(Qt.DisplayRole)

            scode = stock.normalizeStockCode(d0)
            sname = stock.getStockName(scode)
            if(sname):
                watchlist.append([d0, d1, d2])

        #write to file begin
        try:
            f = open(filename, 'wb')
        except IOError:
            exc_type, exc_value = sys.exc_info()[:2]
            errmsg = '{}: {}'.format(exc_type.__name__, exc_value)
            output(errmsg, 'red')
            return False
        
        pickle.dump(watchlist, f)
        f.close() 
        #write to file end           
        
    def loadAllItems(self):
        myData = []
        #read from file begin
        filename = globals.datapath + '/watchlist.dat'
        try:
            f = open(filename, 'rb')
            myData = pickle.load(f)
            f.close() 
        except IOError:
            myData = []
        #read from file end          
        
        cnt = 0
        for row in myData:
            item0 = QTableWidgetItem(row[0])
            item1 = QTableWidgetItem(row[1])
            item2 = QTableWidgetItem(row[2])
            item1.setFlags(Qt.ItemIsSelectable|Qt.ItemIsEnabled)
            self.tbWatchList.setItem(cnt, 0, item0)
            self.tbWatchList.setItem(cnt, 1, item1)
            self.tbWatchList.setItem(cnt, 2, item2)
            cnt += 1
            