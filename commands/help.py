
import os

from modules import utils

desc = '[command] [subcommand] help|?  显示帮助信息'

subCommands = {}


def run(subcmd, params):

    cmdList = utils.getCmdList()
    utils.output(desc)
    utils.output(cmdList)
            