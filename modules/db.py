
import os
import sys
import sqlite3

from modules import globals
from modules import utils


dbfile = globals.datapath + '/stock.db'

class Sqlite3():

    def __init__(self):
        self.dbfile = dbfile
        self.conn = None

    def connect(self):
        try:
            self.conn = sqlite3.connect(self.dbfile)
            self.conn.row_factory = dict_factory
            self.cursor = self.conn.cursor()
        except:
            exc_type, exc_value = sys.exc_info()[:2]
            error = '{}: {}'.format(exc_type.__name__, exc_value)
            utils.output('db connect error: {}'.format(error), 'red')
            return False


        sqlList = []
        sqlList.append('PRAGMA cache_size =8000')
        sqlList.append('PRAGMA synchronous = 0')
        sqlList.append('PRAGMA encoding = "UTF-8"')
        for sql in sqlList:
            self.query(sql)

        self.commit()

        return self.conn

    def query(self, sql, parameters = None):
        try:
            if(parameters):
                self.cursor.execute(sql, parameters)
            else:
                self.cursor.execute(sql)
        except:
            exc_type, exc_value = sys.exc_info()[:2]
            error = '{}: {}'.format(exc_type.__name__, exc_value)
            utils.output('db query error: {}'.format(error), 'red')
            return False 

        return True

    def commit(self):
        self.conn.commit()

    def selectOne(self, sql, parameters = None):
        row = None
        c = self.conn.cursor()
        try:
            if(parameters):
                c.execute(sql, parameters)
            else:
                c.execute(sql)
        except:
            exc_type, exc_value = sys.exc_info()[:2]
            error = '{}: {}'.format(exc_type.__name__, exc_value)
            utils.output('db selectOne error: {}'.format(error), 'red')
            return False 

        for r in c:
            row = r
            break

        c.close()
        return row

    def selectAll(self, sql, parameters = None):
        rows = []
        c = self.conn.cursor()
        try:
            if(parameters):
                c.execute(sql, parameters)
            else:
                c.execute(sql)
        except:
            exc_type, exc_value = sys.exc_info()[:2]
            error = '{}: {}'.format(exc_type.__name__, exc_value)
            utils.output('db selectAll error: {}'.format(error), 'red')
            return False 

        for r in c:
            rows.append(r)

        c.close()
        return rows

    def close(self):
        if(self.cursor):
            self.cursor.close()
            self.cursor = None            
        if(self.conn):
            self.conn.close()
            self.conn = None

    def __del__(self):
        self.close()
            


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def initdb():
    lite3db = Sqlite3()
    if(not lite3db.connect()):
        return
    
    # Create table
    retOk = True
    sqlArr = []

    sqlArr.append('''create table stockhistory(id text NOT NULL PRIMARY KEY, 
        code text NOT NULL, 
        date text NOT NULL, 
        open real NOT NULL, 
        high real NOT NULL, 
        close real NOT NULL, 
        low real NOT NULL, 
        volume real NOT NULL, 
        amount real NOT NULL,
        multiplier real NOT NULL)''')

    sqlArr.append('create index stockhistory_code_index on stockhistory(code, date desc)')

    sqlArr.append('''create table stockinfo(id text NOT NULL PRIMARY KEY, 
        code text NOT NULL, 
        data text NOT NULL)''')

    sqlArr.append('create index stockinfo_code_index on stockinfo(code)')

    for sql in sqlArr:
        if(not lite3db.query(sql)):
            retOk = False
            break

    if(not retOk):
        lite3db.close()
        os.remove(dbfile)
        return     
  
    lite3db.close()

    

