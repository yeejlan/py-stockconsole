
import datetime

from modules import globals
from modules import stock
from modules import utils

desc = 'env subcommand  列出/设置全局变量'

subCommands = {
'list' : 'list  列出所有变量',
'realtime' : 'realtime [on]|off  实时/盘后 状态切换',  
}



def run(subcmd, params):
    
    if(subcmd == 'list'):
        setting = {}
        for k in subCommands.keys():
            if(k != 'list'):
                setting[k] = globals.__dict__.get(k)

        utils.output(setting)

    elif(subcmd == 'realtime'):
        if(len(params) < 1):
            msg = 'realtime on'
            globals.realtime = True
            utils.output(msg)
        elif(len(params) == 1 and (params[0]=='on' or params[0]=='off')):
            if(params[0]=='on'):
                msg = 'realtime on'
                globals.realtime = True
            else:
                msg = 'realtime off'
                globals.realtime = False
            utils.output(msg)
        else:
            utils.output('参数错误', 'red')
            utils.output(subCommands['realtime'])

        
        if(not globals.realtime):
            chart = globals.mainwin.chart
            hqinfo = chart.rt_data.get('data')
            if(hqinfo and chart.rt_data.get('status') == 'realtime'):
                chart.rt_data['status'] = ''
                if(chart.kdata[-1]['date'] == hqinfo['date']):
                    chart.kdata = chart.kdata[:-1] 

            globals.mainwin.scrollbar.setMaximum(len(chart.kdata))
            utils.update()
            