
import re
import sys
import urllib.parse

from modules import utils

desc = 'suggest subcommand  给出建议'

subCommands ={
'code' : 'code stock_name  根据拼音给出股票代码'
}


def run(subcmd, params):
    if(subcmd == 'code'):
        if(len(params) != 1):
            utils.output('参数错误', 'red')
            utils.output(subCommands['code'])
            return

        return _suggestCode(params[0])

        


def _suggestCode(text):
    escapeTxt = urllib.parse.quote(text)
    url = 'http://suggest3.sinajs.cn/suggest/type=&key={}'.format(escapeTxt)
    err, u, content = utils.getWebContent(url)
    if(err):
        utils.output(err, 'red')
        return 'eee'
    
    content = content.decode('gbk')
    codeArr = []
    resultArr = re.findall(r'"(.*)"', content)[0].split(';')
    for line in resultArr:
        cArr = line.split(',')
        if(len(cArr) == 6 and cArr[1]=='11'): #cArr[1]==11 A股
            codestr = '{} {}'.format(cArr[3], cArr[4])
            codeArr.append(codestr)

    if(len(codeArr)<1):
        utils.output('nothing')
    else:
        utils.output(codeArr)
    return

