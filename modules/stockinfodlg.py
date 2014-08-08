
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class StockInfoDlg(QDialog):

    def __init__(self, parent):
        super().__init__(parent)
        self.resize(150, 160)
        self.setWindowTitle('Info')
        self.setWindowFlags(Qt.Tool|Qt.MSWindowsFixedSizeDialogHint)
        self.setStyleSheet('background: white')

        names = ['时  间', '数  值', '开盘价', '最高价', '最低价', '收盘价', '成交额', '涨  跌', '振  幅']
        self.labels = []
        for n in names:
            w = QLabel('')
            w.setAlignment(Qt.AlignRight)
            self.labels.append(w)

        grid = QGridLayout()
        grid.setSpacing(0)
        grid.setContentsMargins(0, 0, 0, 0)

        cnt = 0
        for w in names:
            grid.addWidget(QLabel(w), cnt, 0)
            grid.addWidget(self.labels[cnt], cnt, 1)
            cnt += 1

        self.setLayout(grid)
