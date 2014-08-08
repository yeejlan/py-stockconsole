
import os

#working path
base = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

#global data
data = {}

#main window holder
mainwin = None

#viewportclear
viewportclear = True

#debug mode
debug = True

#realtime mode
realtime = False

#tesing draw mode
testing = True

#stock data directory
datapath = os.path.join(base, 'data')

#cache directory
cachepath = datapath + '/cache'

#backup directory
backuppath = datapath + '/backup'

#user agent for download webpage
useragent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.2.13) Gecko/20101203 Firefox/3.6.13'


#钱龙设置
qldatabase = 'C:/LON/QLDATA/history/SHASE'
qldaybase = qldatabase + '/day'
qlweightbase = qldatabase + '/weight'

#通达信设置
tdxdaybase = 'C:/new_gtja_v6/Vipdoc/sh/lday'
