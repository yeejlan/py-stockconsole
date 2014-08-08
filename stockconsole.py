
import os
import sys

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from modules import globals
from modules import init
from modules import mainwindow
from modules import utils

app = QApplication(sys.argv)

#set window style
#app.setStyle(QStyleFactory.create('Cleanlooks'))

#enable utf-8 display
codec = QTextCodec.codecForName('UTF8')
QTextCodec.setCodecForLocale(codec)

#main window
globals.mainwin = mainwin = mainwindow.MainWindow()
mainwin.show()

#set default focus
mainwin.cmdedit.setFocus(Qt.OtherFocusReason)

#some initialize job
init.init()

sys.exit(app.exec_())