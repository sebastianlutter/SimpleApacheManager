#!/usr/bin/python3
# -*- coding: utf-8 -*-

import collections
from sam.actions.IAction import IAction
#
# Bundles different services to concrete actions (i.e. create vhost with SSL cert)
#
class SystemActions(IAction):

    actions = collections.OrderedDict(sorted({
        "status" : "shows current options and configuration as well as runs some sanity checks."
        ,"install" : "install the environment integration in the host system. Needs sudo rights."
 #       ,"restore" : "TODO: restore to last sane configuration if something destroyed the configuration."
    }.items()))

    def __init__(self):
        pass

    def addParserArgs(self, parser):
        parser_system = parser.add_parser(self.getName(), help=', '.join(self.actions.keys()))
        parser_system.add_argument(self.getName(), choices=self.actions, help='avail.')

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
    def process(self,args):
        print("SystemActions triggered")