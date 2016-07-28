#!/usr/bin/python3
# -*- coding: utf-8 -*-

import collections
import re

import os

import sys

from sam.commands.ICommand import IAction
"""
Add or remove system users from beeing part of the SimpleApacheManager tool to manage their own domains and stuff.
"""
class UserCommand(IAction):
    """
    List all available commands and their description. Structure is:
    dict(action, list(
        list(sub args)
        , description
        , example usage))
    """
    actions=collections.OrderedDict(sorted({
                                               "list" : [[]
                                                   ,"list all available domains, subdomains and alias"
                                                   ,"samcli user list"]
                                               ,"add" : [["user"]
                                                    ,"add a new vhost to the server"
                                                    ,"samcli user add mary"]
                                           }.items()))

    argHelp={"user":"A username without whitespaces or special chars."}

    def __init__(self):
        pass

    """
    Create argparse parser to define the DomainAction CLI API
    """
    def addParserArgs(self, subparser):
        # create subparser for the options
        parser=subparser.add_parser(self.getName(), help = ', '.join(self.actions.keys()))
        subsubparser=parser.add_subparsers(dest = 'sub_command')
        # add a subparser for each action
        for action in self.actions.keys():
            data = self.actions[action]
            needed_params=data[0]
            description=data[1]
            # entry for each action
            tmp_parser=subsubparser.add_parser(action, help=description)
            # and now for the parameters of each action (i.e. domain and/or subdomain)
            for arg in needed_params:
                tmp_parser.add_argument(arg,help=self.argHelp[arg],action='store')

    '''
    Validate with regex if domain/alias/subdomain param is valid.
    :return True if given input is valid for the given type (arg parameter), else False is returned.
    '''
    def validateParam(self,arg,param):
        regex=r''
        if arg == "user":
            # if arg == user: Allow user123, user-local, username22
            regex=re.compile("^(?!-)[A-Z0-9\d-]{1,40}(?<!-)$", re.IGNORECASE)
        else:
            raise AssertionError('invalid parameter "'+arg+'"')
        if not regex.match(param):
            raise Exception("Given value "+param+" is not valid "+arg+" value")

    '''
    Return string list with usage examples
    '''
    def getExampleUsage(self):
        out=list()
        # iterate through commands
        for action in self.actions.keys():
            # build example string for this action
            desc=self.actions[action][1]
            example=self.actions[action][2]
            out.append(' $ {:<45s} : {}'.format(example, desc))
        return out

    '''
    Process an action depending on the given args
    '''
    def process(self,services,config,args, real_user):
        keys=list(self.actions.keys())
        if args.sub_command == "add":
            self.validateParam("user",args.user)
            self.commandAdd(args.user,services,config)
        elif args.sub_command == "list":
            self.commandList(services['system'],services['template'].folder_vhost_user)
        else:
            raise Exception("Unknown sub_command " + args.sub_command)

    def getName(self):
        return "user"


    def commandAdd(self,user,services,config):
        # check if OS know this user
        if not services['user'].checkIfUserExistsInOS(user):
            print('User {} does not exist in your OS. Please create the user manually. Abort')
            sys.exit(1)
        # Is user already part of the sam toolkit?
        if services['user'].checkIfSAMUserExists(user,services['system'],services['template']):
            print('User {} is already known to the SimpleApacheManager. Abort')
            sys.exit(1)
        print("Add system user "+user+" to the list of SimpleApacheManager user.")
        services['user'].addNewUser(user,services['template'],services['system'],config)

    def commandList(self,sys_service,path):
        print("Show the list of SimpleApacheManager users:")
        for user in sys_service.getFolderList(path):
            print('\t'+os.path.basename(user))