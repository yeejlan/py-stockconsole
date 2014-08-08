
import imp
import os
import sys
import re

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from modules import globals
from modules import utils

class Cmdedit(QLineEdit):

    def __init__(self):
        super().__init__()

        self.cmdHistory = []
        self.cmdHistoryIdx = 0

    def focusInEvent(self, event):
        super().focusInEvent(event)

        globals.mainwin.restoreDockWidget(globals.mainwin.dockOne)

    def keyPressEvent(self, event):
        super().keyPressEvent(event)

        key = event.key()
        if(key == Qt.Key_Escape):
            globals.mainwin.chart.setFocus(Qt.OtherFocusReason)
            globals.mainwin.removeDockWidget(globals.mainwin.dockOne)
        elif(key == Qt.Key_Return):
            res = re.findall(r'(\S+)', self.text())
            text = ' '.join(res)
            if(text!=''):
                #add command history
                if(not self.cmdHistory or self.cmdHistory[len(self.cmdHistory)-1] != text):   
                    self.cmdHistory.append(text)
                    length = len(self.cmdHistory)
                    if(length>100):
                        self.cmdHistory = self.cmdHistory[length-50:]

                self.cmdHistoryIdx = len(self.cmdHistory)
                #run command
                utils.output(text,'blue')
                self.clear()
                utils.runCmd(text)

        elif(key == Qt.Key_U):
            if(event.modifiers() == Qt.ControlModifier):
                pos = self.cursorPosition()
                txt = self.text()[pos:]
                self.setText(txt)
                self.setCursorPosition(0)

        elif(key == Qt.Key_K):
            if(event.modifiers() == Qt.ControlModifier):
                pos = self.cursorPosition()
                txt = self.text()[:pos]
                self.setText(txt)

        elif(key == Qt.Key_Up):
            idx = self.cmdHistoryIdx - 1
            if(idx < 0):
                idx = len(self.cmdHistory) - 1

            try:
                self.setText(self.cmdHistory[idx])
                self.cmdHistoryIdx = idx
            except:
                pass

        elif(key == Qt.Key_Down):
            idx = self.cmdHistoryIdx + 1
            if(idx > len(self.cmdHistory) -1):
                idx = 0

            try:
                self.setText(self.cmdHistory[idx])
                self.cmdHistoryIdx = idx
            except:
                pass

        elif(key == Qt.Key_Tab):
            res = re.findall(r'(\S+)', self.text())
            text = ' '.join(res)
            if(text!=''):
                self.suggestCmd(text)


    def suggestCmd(self, cmdLine):
        cmds = cmdLine.split(' ')
        cmd = cmds[0]
        try:
            subcmd = cmds[1]
        except IndexError:
            subcmd = None

        param = None
        if(subcmd):
            try:
                param = cmds[2]
            except IndexError:
                pass
    
        if(cmd and (not subcmd)): #only have command
            #try to suggest command
            suggestArr = []
            for c in utils.getCmdList():
                if(c[:len(cmd)] == cmd):
                    suggestArr.append(c)
            
            if(len(suggestArr) == 1): #now we got the only one correct command
                cmd = suggestArr[0]
                cmdLine = cmd + ' '
                if(self.text() == cmdLine):  #need suggest subcommand
                    self.suggestSubcmd(cmd, None)
                else:
                    self.setText(cmdLine)
                return
            elif(len(suggestArr) > 1): #output all possible cmds
                cmd = self._suggest(cmd, suggestArr)
                cmdLine = cmd
                self.setText(cmdLine)
                utils.output(suggestArr)
                return
            
        #now we have command and subcommand
        if(subcmd and (not param)):	
            self.suggestSubcmd(cmd, subcmd)



    def suggestSubcmd(self, cmd, subcmd):
        filepath = './commands/'+cmd+'.py'
        if not os.path.exists(filepath):
            return

        modname = 'commands.{}'.format(cmd)
        __import__(modname)
        module = sys.modules[modname]
        if(globals.debug):
            imp.reload(module)
            
        if(not subcmd): #no subcommand
            if(len(module.subCommands.keys()) == 1): #only have one subcommand
                subcmd = list(module.subCommands.keys())[0]
                cmdLine = cmd + ' ' + subcmd + ' '
                self.setText(cmdLine)
                return
                
            elif(len(module.subCommands) > 1):
                utils.output(list(module.subCommands.keys()))
                subcmd = self._suggest('', list(module.subCommands.keys()))
                cmdLine = cmd + ' ' + subcmd
                self.setText(cmdLine)
                return

        #have subcommand
        suggestSubcmd = []
        for sc in module.subCommands.keys():
            if(subcmd and sc[:len(subcmd)] == subcmd):
                suggestSubcmd.append(sc)

        if(len(suggestSubcmd) == 1): #only find one subcommand
            subcmd = suggestSubcmd[0]
            cmdLine = cmd + ' ' + subcmd + ' '
            self.setText(cmdLine)
            return

        elif(len(suggestSubcmd) > 1):
            subcmd = self._suggest(subcmd, suggestSubcmd)
            cmdLine = cmd + ' ' + subcmd
            self.setText(cmdLine)
            utils.output(suggestSubcmd)
            return



    def _suggest(self, cmd, cmdList):
        if(len(cmdList) < 2):
            raise ValueError('cmdList need have more than one elements')

        sl = 1
        match = True
        
        p = cmdList[0]+'  '
        while(match):
            s = p[:sl]
            sl = len(s)
            for c in cmdList:
                if(len(c) == s or c[:sl] != s):
                    match = False
                    break
            sl = sl+1
            
        s = s[:len(s)-1]
        if(s[:len(cmd)] == cmd):
            return s
        return cmd