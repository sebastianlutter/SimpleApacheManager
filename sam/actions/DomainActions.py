#!/usr/bin/python3
# -*- coding: utf-8 -*-

import collections
from sam.actions.IAction import IAction
#
# Bundles different services to concrete actions (i.e. create vhost with SSL cert)
#
class DomainActions(IAction):
    """
    List all available actions and their description. Structure is:
    dict(action, list(
        list(sub args)
        , description
        , example usage))
    """
    actions=collections.OrderedDict(sorted({
            "list" : [[]
                    ,"list all available domains, subdomains and alias"
                    ,"sam domain list"]
            ,"add" : [["domain"]
                    ,"add a new vhost to the server"
                    ,"sam domain add example.org"]
            ,"del" : [["domain"]
                    ,"delete an existing vhost from the server"
                    ,"sam domain del example.org"]
            ,"addsub" : [["domain","subdomain"]
                    ,"add a new subdomain to an existing domain"
                    ,"sam domain addsub example.org dl"]
            ,"delsub" : [["domain","subdomain"]
                    ,"del a existing subdomain from an existing domain"
                    ,"sam domain delsub example.org dl"]
            ,"addalias" : [["domain","alias"]
                    ,"add an alias domain to a existing domain"
                    ,"sam domain addalias example.org www.foo.de"]
            ,"delalias" : [["domain","alias"]
                    ,"delete an alias name from an existing domain"
                    ,"sam domain delalias example.org www.foo.de"]
             }.items()))

    argHelp={"domain":"The domain name, i.e. example.org"
            ,"subdomain":"The subdomain name, i.e. sub1, projects"
            ,"alias":"An alias name for the domain, i.e. example.org or what.ever.org"
            }

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
        if arg == self.argHelp.keys()[0]:
            # if arg == domain
            pass
        elif arg == self.argHelp.keys()[1]:
            # if arg == subdomain
            pass
        elif arg == self.argHelp.keys()[2]:
            # if arg == alias
            pass
        else:
            raise AssertionError('invalid parameter "'+arg+'"')
        return True

    def getName(self):
        return "domain"

    '''
    Return string list with usage examples
    '''
    def getExampleUsage(self):
        out=list()
        # iterate through actions
        for action in self.actions.keys():
            # build example string for this action
            desc=self.actions[action][1]
            example=self.actions[action][2]
            out.append(' $ {:<45s} : {}'.format(example, desc))
        return out

    '''
    Process an action depending on the given args
    '''
    def process(self,args):
        print("DomainActions triggered")