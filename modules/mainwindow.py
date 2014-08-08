
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from modules import cmdedit
from modules import chart
from modules import globals
from modules import output
from modules import scrollbar
from modules import stockinfodlg
from modules import stockfilterresultdlg
from modules import stockwatchdlg
from modules import utils


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        
        self.setMinimumSize(980, 960)

        self.stockinfodlg = stockinfodlg.StockInfoDlg(self)
        self.stockfilterresultdlg = stockfilterresultdlg.StockFilterResultDlg(None)
        self.stockwatchdlg = stockwatchdlg.StockWatchDlg(None)

        self.chart = chart.Chart()
        self.chart.setMinimumSize(868, 438)
        self.chart.setFocusPolicy(Qt.ClickFocus)
        self.chart.setBackgroundRole(QPalette.Base)
        self.chart.setMouseTracking(True)

        self.scrollbar = scrollbar.ScrollBar(Qt.Horizontal, self)
        self.scrollbar.setMaximum(2000)

        w = QWidget()
        vbox = QVBoxLayout()
        vbox.setSpacing(0)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(self.chart)
        vbox.addWidget(self.scrollbar)
        w.setLayout(vbox)

        self.setCentralWidget(w)

        self.createActions()
        self.createMenus()
        self.createDockWindows()
        #self.createStatusBar()

        self.setWindowTitle('Stock Console')
        self.setWindowIcon(QIcon('./images/console.png'))

        desktop = QApplication.desktop()
        self.move((desktop.width() - self.width())/2, (desktop.height() - self.height() - 50)/2)
    
    def createStatusBar(self):
        self.statusBar().showMessage('Ready')

    def createActions(self):
        self.quitAct = QAction('&Quit', self, triggered=self.quit)
        self.quitAct.setShortcuts(QKeySequence('Alt+Q'))

        self.windowInfoAct = QAction('&Info', self, triggered=self.windowInfo)
        self.windowInfoAct.setShortcuts(QKeySequence('Alt+I'))
        self.windowStockFilterResultAct = QAction('&Filter Result', self, triggered=self.windowStockFilterResult)
        self.windowStockFilterResultAct.setShortcuts(QKeySequence('Ctrl+F'))
        self.windowWatchListAct = QAction('&Watch List', self, triggered=self.windowWatchListDlg)
        self.windowWatchListAct.setShortcuts(QKeySequence('Ctrl+W'))
        
        self.aboutAct = QAction('&About', self, triggered=self.about)
        self.aboutQtAct = QAction('About &Qt', self, triggered=qApp.aboutQt)

    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu('&File')
        self.fileMenu.addAction(self.quitAct)

        self.windowMenu = self.menuBar().addMenu('&Window')
        self.windowMenu.addAction(self.windowInfoAct)
        self.windowMenu.addAction(self.windowStockFilterResultAct)
        self.windowMenu.addAction(self.windowWatchListAct)

        self.helpMenu = self.menuBar().addMenu('&Help')
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)

    def createDockWindows(self):
        self.dockOne = QDockWidget('Output', self)
        self.dockOne.setFeatures(QDockWidget.NoDockWidgetFeatures)

        self.output = output.Output()
        self.dockOne.setWidget(self.output)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.dockOne)

        self.dockTwo = QDockWidget('Command', self)
        self.dockTwo.setFeatures(QDockWidget.NoDockWidgetFeatures)

        self.cmdedit = cmdedit.Cmdedit()
        self.dockTwo.setWidget(self.cmdedit)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.dockTwo)
        self.splitDockWidget(self.dockOne, self.dockTwo, Qt.Vertical)        

    def about(self):
        QMessageBox.about(self, 'About Stock Console',
            "This is a stock analysis program.\r\nEnjoy it:)")

    def closeEvent(self, event):
        if utils.confirm(self, 'Are you sure to quit?', 'Quit'):
            self.stockfilterresultdlg.close()
            self.stockwatchdlg.close()
            event.accept()
        else:
            event.ignore()

    def quit(self):
        self.close()

    def showStockInfoDlg(self):
        self.stockinfodlg.show()
        self.stockinfodlg.activateWindow()

    def windowInfo(self):
        self.showStockInfoDlg()

    def windowStockFilterResult(self):
        self.stockfilterresultdlg.show()
        self.stockfilterresultdlg.activateWindow()

    def windowWatchListDlg(self):
        self.stockwatchdlg.show()
        self.stockwatchdlg.activateWindow()