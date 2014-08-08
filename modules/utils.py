
import datetime
import imp
import os
import queue
import sys
import threading
import time
import traceback
import urllib.request
import urllib.parse

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from modules import globals

def confirm(parent, message, title = 'Confirm'):
    msgbox = QMessageBox(parent)
    msgbox.setWindowTitle(title)
    msgbox.setText(message)
    msgbox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    msgbox.setDefaultButton(QMessageBox.Ok)
    if (msgbox.exec() == QMessageBox.Ok):
        return True

    return False


def alert(parent, message, title = 'Alert'):
    msgbox = QMessageBox(parent)
    msgbox.setWindowTitle(title)
    msgbox.setText(message)
    msgbox.setStandardButtons(QMessageBox.Ok)
    msgbox.setDefaultButton(QMessageBox.Ok)
    msgbox.exec()

def output(text, color = ''):
    if color == 'red' :
        globals.mainwin.output.setTextColor(QColor(255,0,0))
    elif color == 'pink' :
        globals.mainwin.output.setTextColor(QColor(255,0,255))
    elif color == 'blue' :
        globals.mainwin.output.setTextColor(QColor(0,0,255))
    elif color == 'green' :
        globals.mainwin.output.setTextColor(QColor(0,128,0))
    else:
        globals.mainwin.output.setTextColor(QColor(0,0,0))

    if(type(text) == list):
        lst = []
        for i in text:
            lst.append('{}'.format(i))
        text = ', '.join(lst)
        
    globals.mainwin.output.append('{}'.format(text))
    globals.mainwin.output.verticalScrollBar().setSliderPosition(globals.mainwin.output.verticalScrollBar().maximum())
    QCoreApplication.processEvents()

def overwrite(text, prefix=''):
    if(prefix):
        if(getLastCmdeditLine()[0:len(prefix)] != prefix):
            output(text) 
            return

    cur = QTextCursor(globals.mainwin.output.document())
    cur.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)
    cur.select(QTextCursor.LineUnderCursor)
    cur.deleteChar()
    cur.insertText('{}'.format(text)) 
    QCoreApplication.processEvents()

#update viewport
def update():
    globals.mainwin.chart.update()

#get last line from cmdedit
def getLastCmdeditLine():
    cur = QTextCursor(globals.mainwin.output.document())
    cur.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)
    cur.select(QTextCursor.LineUnderCursor)
    return cur.selectedText()

def getWebContent(url):  #return tuple(error, url, content)

    in_queue = queue.Queue()
    in_queue.put(url)
    out_queue = queue.Queue()
    getWebContentMT(in_queue, out_queue)
    while(True):
        try:
            retval = out_queue.get(False)
            break
        except queue.Empty:
            time.sleep(0.01)
            QCoreApplication.processEvents()

    return retval

def _getWebContent(remote_url):  #internal function, return tuple(error, url, content)
    error = None
    content = ''
    try:
        req = urllib.request.Request(remote_url)
        req.add_header('Referer', remote_url)
        req.add_header('User-Agent', globals.useragent)
        res = urllib.request.urlopen(req, None, 30)
        content = res.read()
    except:
        exc_type, exc_value = sys.exc_info()[:2]
        error = '{}: {}'.format(exc_type.__name__, exc_value)
        
    return (error, remote_url, content)

'''
in_queue  item: url(String) the url we want to fetch
out_queue item: tuple(error, url, content) the web content we got
'''
def getWebContentMT(in_queue, out_queue, thread_max = 1, thread_name = ''):  #use multi-thread to get web content
    thread_list = []
    for i in range(0, thread_max):
        t = _GetWebContentWorker(in_queue, out_queue, thread_name)
        thread_list.append(t)
        t.start()
    
    return thread_list
    
#get all commands
def getCmdList():
    cmdList = []
    files = os.listdir('./commands')
    for f in files:
        if(f[0] != '_' and f[len(f)-3:] == '.py'):
            cmdList.append(f[:len(f)-3])

    return cmdList

def file_put_contents(filename, data, mode='w'):
    try:
        f = open(filename, mode)
    except IOError:
        exc_type, exc_value = sys.exc_info()[:2]
        errmsg = '{}: {}'.format(exc_type.__name__, exc_value)
        output(errmsg, 'red')
        return False
    
    length = f.write(data)
    f.close() 

    if(length == len(data)):
        return True

    return False

def file_get_contents(filename, mode='r'):
    try:
        f = open(filename, mode)
    except IOError:
        exc_type, exc_value = sys.exc_info()[:2]
        errmsg = '{}: {}'.format(exc_type.__name__, exc_value)
        #output(errmsg, 'red')
        return False

    return f.read()

def md5(str, encoding = 'utf8'):
    m = hashlib.md5()
    m.update(str.encode(encoding))
    return m.hexdigest()

def runCmd(cmdLine):
    errmsg = None
    cmds = cmdLine.split(' ')
    cmd = cmds[0]
    try:
        subcmd = cmds[1]
    except IndexError:
        subcmd = None
    params = cmds[2:]

    if(cmd == '?'):
        cmd = 'help'

    if(subcmd == '?'):
        subcmd = 'help'

    filepath = './commands/'+cmd+'.py'
    if not os.path.exists(filepath):
        errmsg = '找不到命令: {}'.format(cmd)
        output(errmsg, 'red')
    else:
        #command found
        modname = 'commands.{}'.format(cmd)
        __import__(modname)
        module = sys.modules[modname]
        if(globals.debug):
            imp.reload(module)

        #command help
        if(subcmd == 'help'):
            output('{}'.format(module.desc))
            if	module.subCommands :
                output(list(module.subCommands.values()))	

            return

        #subcommand checking
        if(subcmd and (not (subcmd in module.subCommands))):
            errmsg = '找不到子命令: {}'.format(subcmd)
            output(errmsg, 'red')
            output(list(module.subCommands.keys()))	
            return

        #make sure subcommand given
        if((not subcmd) and module.subCommands):
            errmsg = '{} 需要提供子命令'.format(cmd)
            output(errmsg, 'red')
            output(list(module.subCommands.values()))	
            return

        #subcommand help
        try:
            param = cmds[2]
        except IndexError:
            param = ''
        if(param == '?' or param == 'help'):
            if(subcmd in module.subCommands):
                output('{}'.format(module.subCommands[subcmd]))
            else:
                output('{}'.format(module.subCommands))	
            return

        #run command
        ret_isError = False
        ret_info = ''
        try:
            ret_value = module.run(subcmd, params)
            if(ret_value == False):
                ret_isError = True
            elif(ret_value):
                ret_info = ret_value

        except:
            exc_type, exc_value = sys.exc_info()[:2]
            errmsg = '{}: {}'.format(exc_type.__name__, exc_value)
            output(errmsg, 'red')
            if(globals.debug):
                traceback.print_exc()

        if(ret_isError or errmsg != None):
            retval = 'exit with error'
            retcolor = 'red'
        else:
            retval = 'exit'
            retcolor = 'pink'
        
        if(cmd == 'help' or cmd == 'clear'):
            return

        if(ret_info):
            output('{} [{} {}]'.format(cmdLine, retval, ret_info), retcolor)
        else:
            output('{} [{}]'.format(cmdLine, retval), retcolor)         
            


class _GetWebContentWorker(threading.Thread):
    def __init__(self, in_queue, out_queue, thread_name):
        threading.Thread.__init__(self)
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.running = True
        if(thread_name != ''):
            self.name = thread_name

    def run(self):
        while(self.running):
            try:
                url = self.in_queue.get(False)
                self.out_queue.put(_getWebContent(url))
                self.in_queue.task_done()
            except queue.Empty:
                break
      
    def stop(self):
        self.running = False


#方差
def variance (vals):
    l = len(vals)
    avg = sum(vals) / l
    return sum([(v - avg) ** 2 for v in vals]) / l

#indicator helper fnction
def feedstockdata(oneindicator):
        chart = globals.mainwin.chart
        if(not oneindicator.chart):
            oneindicator.chart = chart

        kdata = chart.kdata
        if(globals.realtime):
            #kdata = chart.kdata[-1000:]
            pass

        if(globals.realtime or oneindicator.stockcode != chart.stockcode):
            oneindicator.stockcode = chart.stockcode
            oneindicator.data = oneindicator.calculateData(kdata)