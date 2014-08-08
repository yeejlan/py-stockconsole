

import threading

from modules import utils

desc = 'jobs  列出当前所有活动线程'

subCommands = {}

def run(subcmd, params):
    utils.output(threading.enumerate())