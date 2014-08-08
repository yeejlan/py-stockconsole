import os
import sys
import sqlite3

from modules import db
from modules import globals
from modules import utils


def init():

    if (not os.path.exists(globals.datapath)):
        os.mkdir(globals.datapath)

    if (not os.path.exists(globals.cachepath)):
        os.mkdir(globals.cachepath)

    if (not os.path.exists(globals.backuppath)):
        os.mkdir(globals.backuppath)
        
#    #initialize database
#    if (not os.path.exists(db.dbfile)):
#        db.initdb()

    if(os.path.exists('D:/GTJARZ/Vipdoc/sh/lday')):
        globals.tdxdaybase = 'D:/GTJARZ/Vipdoc/sh/lday'