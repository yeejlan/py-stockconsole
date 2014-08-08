
import pickle

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from modules import globals
from modules import utils
from commands import viewport

class StockFilterResultDlg(QDialog):

    def __init__(self, parent):
        super().__init__(parent)
        self.resize(356, 518)
        self.setWindowTitle('Stock Filter Result')
        self.setWindowFlags(Qt.MSWindowsFixedSizeDialogHint)
        self.setStyleSheet('selection-background-color: #efefef; selection-color: black; font: "Tahoma"; font-size: 10pt')
      
        vbox = QVBoxLayout()
        vbox.setSpacing(0)
        vbox.setContentsMargins(0, 0, 0, 0)

        self.tbResults = 	QTableView()      #QTableView
        vbox.addWidget(self.tbResults)

        self.setLayout(vbox)
        self.setWindowIcon(QIcon('./images/console.png'))

        my_array = [[' ', ' ', ' ']]

        #read from file begin
        filename = globals.datapath + '/lastFilterResult.dat'
        try:
            f = open(filename, 'rb')
            my_array = pickle.load(f)
            f.close() 
        except IOError:
            pass
        #read from file end        

        tablemodel = FilterResultModel(my_array, self)
        self.tbResults.setModel(tablemodel)

        hview = QHeaderView(Qt.Horizontal)
        hview.setDefaultSectionSize(100)
        self.tbResults.setHorizontalHeader(hview)
        vview = QHeaderView(Qt.Vertical)
        vview.setDefaultSectionSize(25)
        self.tbResults.setVerticalHeader(vview)

        #self.tbResults.setColumnWidth(1, 160)
        self.tbResults.setShowGrid(True)
        self.tbResults.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tbResults.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.tbResults.doubleClicked.connect(self.rowDoubleClicked)

    def rowDoubleClicked(self, idx):
        stockcode = self.tbResults.model().codedata(idx)
        viewport.run('show', [stockcode])


class FilterResultModel(QAbstractTableModel):
    def __init__(self, datain, parent=None, *args):
        super().__init__()
        self.arraydata = datain

    def rowCount(self, parent):
        return len(self.arraydata)

    def columnCount(self, parent):
        return len(self.arraydata[0])

    def data(self, index, role = Qt.DisplayRole):
        if not index.isValid():
            return None
        if role != Qt.DisplayRole:
            return None
        return self.arraydata[index.row()][index.column()]

    def codedata(self, index):
        if not index.isValid():
            return None

        return self.arraydata[index.row()][0]