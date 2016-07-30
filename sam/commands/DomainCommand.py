#!/usr/bin/python3
# -*- coding: utf-8 -*-

import collections
import re

import os

import sys

from sam.commands.ICommand import IAction
"""
Domain commands to modify vhost settings (i.e. create vhost with SSL or add alias )
"""
class DomainCommand(IAction):
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
           ,"samcli domain list"]
        ,"add" : [["domain"]
            ,"add a new vhost to the server"
            ,"samcli domain add example.org"]
        ,"del" : [["domain"]
            ,"delete an existing vhost from the server"
            ,"samcli domain del example.org"]
        ,"addsub" : [["domain","subdomain"]
            ,"add a new subdomain to an existing domain"
            ,"samcli domain addsub example.org dl"]
        ,"delsub" : [["domain","subdomain"]
            ,"del a existing subdomain from an existing domain"
            ,"samcli domain delsub example.org dl"]
        ,"addalias" : [["domain","alias"]
            ,"add an alias domain to a existing domain"
            ,"samcli domain addalias example.org www.foo.de"]
        ,"delalias" : [["domain","alias"]
            ,"delete an alias name from an existing domain"
            ,"samcli domain delalias example.org www.foo.de"]
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
    Throws exception if param is not valid
    '''
    def validateParam(self,arg,param):
        regex=r''
        # validate domain if domain or alias
        if arg == "domain" or arg == "alias":
            # if arg == domain or arg == alias: i.e. example.org www.example123.tech www2.foo-bar.org an.alias.domain.org
            regex=re.compile("[A-Z\d]{1,}\.?(?!-)[A-Z\d-]{1,63}(?<!-)\.[A-Z]{2,}$", re.IGNORECASE)
        elif arg == "subdomain":
            # if arg == subdomain: i.e. www2, foobar or also ww.aa.dd (that leads to www.aa.dd.example.org subdomain)
            # not starting with point, than any A-Z chars, numbers and minus char in the name, then zero or more
            # sequences of point and any A-Z chars, numbers and minus char. It is not allowed that it end with a point char.
            regex=re.compile("^(?!\.$)([A-Z\d-]{1,})(\.([A-Z\d-]{1,}))*$", re.IGNORECASE)
        else:
            raise AssertionError('invalid parameter "'+arg+'"')
        if not regex.match(param):
            raise Exception("Given value "+param+" is not valid "+arg+" value")

    def getName(self):
        return "domain"

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

    def process(self, services, config, args, real_user):
        # set the real user executed this script as class attribut
        self.real_user=real_user if real_user != 'root' else config['domain']['default_user']
        # is this a user or admin request
        self.is_user=(not self.real_user == config['system']['admin_user'])
        # call the right action
        if args.sub_command=="add":
            self.validateParam("domain",args.domain)
            self.commandAdd(args.domain,services,config,self.real_user,self.is_user)
        elif args.sub_command=="del":
            self.validateParam("domain", args.domain)
            self.commandDel(args.domain)
        elif args.sub_command == "addsub":
            self.validateParam("domain", args.domain)
            self.validateParam("subdomain", args.subdomain)
            self.commandAddSub(args.domain,args.subdomain)
        elif args.sub_command == "delsub":
            self.validateParam("domain", args.domain)
            self.validateParam("subdomain", args.domain)
            self.commandDelSub(args.domain, args.subdomain)
        elif args.sub_command == "addalias":
            self.validateParam("domain", args.domain)
            self.validateParam("alias", args.alias)
            self.commandAddAlias(args.domain, args.alias)
        elif args.sub_command=="delalias":
            self.validateParam("domain", args.domain)
            self.validateParam("alias", args.alias)
            self.commandDelAlias(args.domain, args.alias)
        elif args.sub_command == "list":
            self.commandList(services)
        else:
            raise Exception("Unknown sub_command "+args.sub_command)

    """
    List all domains, subdomains and alias
    """
    def commandList(self,services):
        print("DomainActions triggered: list")
        services['apache'].getExistingVHostsList(services['template'],services['system'])
    """
    Add a new domain to the system
    """
    def commandAdd(self,domain,services,config,real_user,is_user):
        # construct dest path
        dest_folder=os.path.join(services['apache'].getVHostFolderFor(real_user,services['template'],config),domain)
        # Abort if it already exists
        if os.path.isdir(dest_folder):
            print("The domain {} already exists in folder {}. Abort.".format(domain,dest_folder))
            sys.exit(1)
        print("Create vhost for {} in folder {}".format(domain,dest_folder))
        # copy and fill template
        services['template'].generateVHostTemplate(domain,config,services['system'],real_user,dest_folder,is_user)
        # generate the SSL certs for this domain
        ssl_cert_folder=os.path.join(dest_folder,'certs')
        services['apache'].generateSSLCertsSelfSigned(ssl_cert_folder,domain,services['system'],config)
        # now chown the whole folder tree to the given ownership
        user,group = services['apache'].getOwnershipFor(real_user,config)
        services['system'].chownRecursive(dest_folder,user,group)
        # add entry in /etc/apache2/sites-enabled/000-default.conf
        vhost_config_file=os.path.join(dest_folder,'conf/httpd.include')
        services['apache'].addIncludeToGlobalConf(vhost_config_file,services['template'])
        # check apache service and reload
        try:
            services['apache'].reloadApache(services['system'])
        except:
            # apache failed to reload, remove include again and restart
            print("ERROR: Apache was not able to reload the config. Remove include entry and try again")
            services['apache'].deleteIncludeFromGlobalConf(vhost_config_file,services['template'])
            print("Try to restart apache server after last added include has been removed from apache configuration..")
            services['apache'].reloadApache(services['system'],True)



    def commandDel(self,domain):
        print("Delete existing vhost " + domain)
        #TODO: implement

    def commandAddSub(self, domain,subdomain):
        print("Create subdomain {}.{} for existing domain {}".format(subdomain,domain,domain))
        #TODO: implement

    def commandDelSub(self, domain, subdomain):
        print("Delete subdomain {}.{} from existing domain {}".format(subdomain, domain, domain))
        #TODO: implement

    def commandAddAlias(self, domain, alias):
        print("Add alias {} to existing domain {}".format(alias, domain))
        #TODO: implement

    def commandDelAlias(self, domain, alias):
        print("Delete alias {} from existing domain {}".format(alias, domain))
        #TODO: implement


