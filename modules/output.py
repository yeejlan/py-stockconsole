
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from modules import globals

class Output(QTextEdit):

    def __init__(self):
        super().__init__()

        self.setReadOnly(True)
        self.setFontFamily('Courier New')
        self.setFontPointSize(10)
        self.setFocusPolicy(Qt.ClickFocus)
        self.setMinimumHeight(200)
        self.document().setMaximumBlockCount(200)

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        
        key = event.key()
        if(key== Qt.Key_Escape or key == Qt.Key_Return):
            globals.mainwin.cmdedit.setFocus(Qt.OtherFocusReason)
