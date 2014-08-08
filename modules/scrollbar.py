
import os
import sys

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from modules import globals
from modules import utils

class ScrollBar(QScrollBar):
    
    def __init__(self, orientation, parent):
        super().__init__(orientation, parent)

        self.valueChanged.connect(self.cbValueChanged)


    def cbValueChanged(self, value):
        utils.update()
    
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        globals.mainwin.chart.crossline = False
        globals.mainwin.chart.mousepos = None
        globals.mainwin.chart.update()