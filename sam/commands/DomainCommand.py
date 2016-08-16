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

    def process(self, services, config, args, user):
        # set the real user executed this script as class attribut
        self.real_user=user if not (user == 'root') else config['domain']['default_user']
        # is this a user or admin request
        self.is_user=not ( self.real_user == config['system']['admin_user']
                        or self.real_user == config['domain']['default_user'])
        # call the right action
        if args.sub_command=="add":
            self.validateParam("domain",args.domain)
            self.commandAdd(args.domain,services,config,self.real_user,self.is_user)
        elif args.sub_command=="del":
            self.validateParam("domain", args.domain)
            self.commandDel(args.domain,services,config,self.real_user,self.is_user)
        elif args.sub_command == "addsub":
            self.validateParam("domain", args.domain)
            self.validateParam("subdomain", args.subdomain)
            self.commandAddSub(args.domain,args.subdomain,services,config,self.real_user,self.is_user)
        elif args.sub_command == "delsub":
            self.validateParam("domain", args.domain)
            self.validateParam("subdomain", args.domain)
            self.commandDelSub(args.domain, args.subdomain,services,config,self.real_user)
        elif args.sub_command == "addalias":
            self.validateParam("domain", args.domain)
            self.validateParam("alias", args.alias)
            self.commandAddAlias(args.domain, args.alias,services,config,self.real_user,self.is_user)
        elif args.sub_command=="delalias":
            self.validateParam("domain", args.domain)
            self.validateParam("alias", args.alias)
            self.commandDelAlias(args.domain, args.alias,services,config,self.real_user)
        elif args.sub_command == "list":
            self.commandList(services)
        else:
            raise Exception("Unknown sub_command "+args.sub_command)

    """
    List all domains, subdomains and alias
    """
    def commandList(self,services):
        print("DomainActions triggered: list")
        services['apache'].printExistingVHostsList(services['template'], services['system'])

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
        services['apache'].addIncludeToConf(vhost_config_file,services['template'].file_etc_apache_conf_global,services['template'].var_etc_apache_include)
        # check apache service and reload
        changes_revoked=False
        try:
            services['apache'].reloadApache(services['system'])
        except:
            # apache failed to reload, remove include again and restart
            print("ERROR: Apache was not able to reload the config. Remove include entry and try again")
            services['apache'].deleteIncludeFromConf(vhost_config_file,services['template'].file_etc_apache_conf_global)
            print("Try to restart apache server after last added include has been removed from apache configuration..")
            services['apache'].reloadApache(services['system'],True)
            changes_revoked=True
        if not changes_revoked:
            # check if domain is properly configured
            services['system'].checkDomainIP(domain,config['system']['ip'])
        else:
            print("\nAn error occured while creating the doman. \nInclude of domain in file {} removed to be able to start apache again.".format(vhost_config_file,services['template'].file_etc_apache_conf_global))
            print('\nThe domain config has not been included in the domain.')
            print('Hopefully the apache server is now up again. Please fix your errors manually and redo the step.')


    """
    Delete an existing domain and all of its subdomains
    """
    def commandDel(self,domain,services,config,real_user,is_user):
        path_to_del=os.path.join(services['apache'].getVHostFolderFor(real_user,services['template'],config),domain)
        if not os.path.isdir(path_to_del):
            print("Domain path "+path_to_del+" is not a folder. Abort.")
            sys.exit(1)
        self.askUser("Delete domain " + domain + " with all its subdomains? ")
        print("Delete existing vhost " + domain)
        try:
            services['system'].createFolderBackup(path_to_del,domain+'_'+real_user,config['system']['folder_vhosts_backup'])
        except:
            print("Backup folder "+path_to_del+" failed. Abort to delete the vhost.")
            sys.exit(1)
        # delete the folder itself
        services['system'].deleteFolderRecursive(path_to_del)
        if is_user:
            # also delete the link in /var/www/vhosts
            link_path=os.path.join(config['system']['folder_vhosts'],domain)
            services['system'].unlinkSymlink(link_path)
        # remove the include lines for the config in global configuration
        include_path=os.path.join(path_to_del,'conf/httpd.include')
        services['apache'].deleteIncludeFromConf(include_path , services['template'].file_etc_apache_conf_global)
        # reload the apache service
        services['apache'].reloadApache(services['system'])


    def commandAddSub(self, domain,subdomain,services,config,real_user,is_user):
        # construct dest path
        domain_folder=os.path.join(services['apache'].getVHostFolderFor(real_user,services['template'],config),domain)
        subdomain_folder=os.path.join(domain_folder,'subdomains',subdomain)
        # Abort if it already exists
        if os.path.isdir(subdomain_folder):
            print("The subdomain folder {} already exists. Abort.".format(subdomain_folder))
            sys.exit(1)
        if not os.path.isdir(domain_folder):
            print("The domain folder {} does not exists. Cannot create subdomain in it. Abort.".format(domain_folder))
            sys.exit(1)
        print("Create subdomain {}.{} for existing domain {}".format(subdomain,domain,domain))
        #copy subdomain template
        tpl_path=os.path.join(config['system']['folder_sam_source_dir'],services['template'].folder_tpl_subdomain)
        services['template'].generateSubdomainTemplate(domain,subdomain,config,services['system'],real_user,subdomain_folder)
        # generate the SSL certs for this domain
        ssl_cert_folder = os.path.join(subdomain_folder, 'certs')
        services['apache'].generateSSLCertsSelfSigned(ssl_cert_folder, subdomain+'.'+domain, services['system'], config)
        # now chown the whole folder tree to the given ownership
        user, group = services['apache'].getOwnershipFor(real_user, config)
        services['system'].chownRecursive(subdomain_folder, user, group)
        # add entry in /etc/apache2/sites-enabled/000-default.conf
        vhost_config_file = os.path.join(domain_folder, 'conf/httpd.include')
        subdomain_config_file = os.path.join(subdomain_folder,'conf/httpd.include')
        services['apache'].addIncludeToConf(subdomain_config_file,vhost_config_file,services['template'].var_subdomain_tpl )
        # check apache service and reload
        changes_revoked=False
        try:
            services['apache'].reloadApache(services['system'])
        except:
            # apache failed to reload, remove include again and restart
            print("ERROR: Apache was not able to reload the config. Remove include entry and try again")
            services['apache'].deleteIncludeFromGlobalConf(vhost_config_file, services['template'])
            print("Try to restart apache server after last added include has been removed from apache configuration..")
            services['apache'].reloadApache(services['system'], True)
            print('\nBecause of an error while creating subdomain {} the domain config has not been included in domain {}')
            print('Hopefully the apache server is now up again. Please fix your errors manually and redo the step.')
            changes_revoked=True
        if not changes_revoked:
            # check if domain is properly configured
            services['system'].checkDomainIP(subdomain + '.' + domain, config['system']['ip'])
        else:
            print("\nAn error occured while creating the doman. \nInclude of domain in file {} removed to be able to start apache again.".format(vhost_config_file,services['template'].file_etc_apache_conf_global))
            print('\nThe domain config has not been included in the domain.')
            print('Hopefully the apache server is now up again. Please fix your errors manually and redo the step.')


    def commandDelSub(self, domain, subdomain,services,config,real_user):
        vhost_path=os.path.join(services['apache'].getVHostFolderFor(real_user,services['template'],config),domain)
        path_to_del=os.path.join(vhost_path,'subdomains',subdomain)
        if not os.path.isdir(path_to_del):
            print("Subdomain path "+path_to_del+" is not a folder. Abort.")
            sys.exit(1)
        self.askUser("Delete subdomain " + subdomain + '.' + domain + " ? ")
        print("Delete subdomain {}.{} from existing domain {}".format(subdomain, domain, domain))
        try:
            services['system'].createFolderBackup(path_to_del,subdomain+'.'+domain+'_'+real_user,config['system']['folder_vhosts_backup'])
        except:
            print("Backup folder "+path_to_del+" failed. Abort to delete the subdomain.")
            sys.exit(1)
        # delete the folder itself
        services['system'].deleteFolderRecursive(path_to_del)
        # remove the include lines for the config in global configuration
        include_path=os.path.join(path_to_del,'conf/httpd.include')
        vhost_conf_path=os.path.join(vhost_path,'conf/httpd.include')
        services['apache'].deleteIncludeFromConf(include_path , vhost_conf_path)
        # reload the apache service
        services['apache'].reloadApache(services['system'])


    def commandAddAlias(self, domain, alias,services,config,real_user,is_user):
        # check domain
        vhost_path=os.path.join(services['apache'].getVHostFolderFor(real_user,services['template'],config),domain)
        if not os.path.isdir(vhost_path):
            print("Domain {} does not exist (directory {}). Abort. ".format(domain,vhost_path))
            sys.exit(1)
        print("Add alias {} to existing domain {}".format(alias, domain))
        #TODO: implement

    def commandDelAlias(self, domain, alias,services,config,real_user):
        print("Delete alias {} from existing domain {}".format(alias, domain))
        #TODO: implement


