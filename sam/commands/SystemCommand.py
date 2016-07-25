#!/usr/bin/python3
# -*- coding: utf-8 -*-

import collections
from sam.commands.ICommand import IAction
"""
This class check if the installation is sane or can install the SimpleApacheManager in the system.
"""
class SystemCommand(IAction):

    actions = collections.OrderedDict(sorted({
         "status" : "shows current options and configuration as well as runs some sanity checks."
         ,"install" : "install the environment integration in the host system. Needs sudo rights."
         #       ,"restore" : "TODO: restore to last sane configuration if something destroyed the configuration."
     }.items()))

    def __init__(self):
        pass

    def addParserArgs(self, subparser):
        parser=subparser.add_parser(self.getName(), help = ', '.join(self.actions.keys()))
        subsubparser=parser.add_subparsers(dest = 'sub_command')
        # and now for the parameters of each action (i.e. domain and/or subdomain)
        for action in self.actions.keys():
            tmp_parser=subsubparser.add_parser(action,help=self.actions[action])

    def getName(self):
        return "system"

    '''
    Return string list with usage examples
    '''
    def getExampleUsage(self):
        out=list()
        for action in self.actions.keys():
            out.append(' $ {:<45s} : {}'.format('sam system '+action,self.actions[action]))
        return out

    '''
    Process an action depending on the given args
    '''
    def process(self,args,operationSystemImpl):
        if args.sub_command=="status":
            self.commandStatus()
        elif args.sub_command=="install":
            self.commandInstall(operationSystemImpl)
        else:
            raise Exception("Unknown sub_command " + args.sub_command)

    def commandStatus(self):
        print("Show status of SimpleApacheManager installation")
        # TODO: Implement

    def commandInstall(self,operationSystemImpl):
        print("Install SimpleApacheManager in your system")
