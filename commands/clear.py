
from modules import globals

desc = 'clear  清屏'

subCommands = {}

def run(subcmd, params):
    globals.mainwin.output.clear()