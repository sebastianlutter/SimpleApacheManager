#!/usr/bin/python3
# -*- coding: utf-8 -*-

import collections
import pprint
import sys

import os

from sam.commands.ICommand import IAction

"""
This class manages SimpleApacheManager system tasks. Install and check if all services.
A Command class may call sys.exit if needed, a Service class should never do this.
"""
class SystemCommand(IAction):

    actions = collections.OrderedDict(sorted({
         "check" : "shows current options and configuration as well as runs some sanity checks."
         ,"install" : "install the environment integration in the host system. Needs sudo rights."
         #       ,"restore" : "TODO: restore to last sane configuration if something destroyed the configuration."
     }.items()))

    def __init__(self):
        pass

    """
    Do not add anything here, there is a check and install argument added by SimpleApacheManager
    """
    def addParserArgs(self, subparser):
        # add parameters for each action (i.e. check or install). But do not use "sam system install", add it to parent argparse directly "sam install"
        for action in self.actions.keys():
            tmp_parser=subparser.add_parser(action,help=self.actions[action])

    def getName(self):
        return "system"

    '''
    Return string list with usage examples
    '''
    def getExampleUsage(self):
        out=list()
        for action in self.actions.keys():
            out.append(' $ {:<45s} : {}'.format('samcli '+action,self.actions[action]))
        return out

    '''
    Process an action depending on the given args
    '''
    def process(self, services, config, args, real_user):
        if args.command=="check":
            self.commandStatus()
        elif args.command=="install":
            self.commandInstall(services,config)
        else:
            raise Exception("Unknown sub_command " + args.sub_command)

    def commandStatus(self):
        print("Show status of SimpleApacheManager installation")
        # TODO: Implement

    """
    Do all steps needed to install SimpleApacheManager folder structures (i.e. /var/www/vhosts/)
    and global configurations.
    """
    def commandInstall(self,services,config):
        sys_user=config['domain']['default_user']
        sys_group=config['domain']['default_group']
        admin_group=config['system']['admin_group']
        print("Install SimpleApacheManager in your OS.")
        # make sure user exists, abort if not
        if not services['user'].checkIfUserExistsInOS(sys_user):
            print("The given admin_user "+sys_user+" does not exist in your OS. \nPlease create it manually (i.e.: sudo adduser "+sys_user+").")
            sys.exit(1)
        else:
            print("Given default domain user "+sys_user+" exists in the OS.")
        # make sure group exists, add it if not
        admin_group=config['system']['admin_group']
        if not services['user'].checkIfGroupExistsInOS(admin_group):
            # add group to OS
            print("\tadmin group "+admin_group+" does not exist, try to create it.")
            services['user'].createOSGroup(admin_group,services['system'])
        # create samcli link to sam_wrapper.py
        sam_wrapper_file=os.path.join(config['system']['folder_sam_source_dir'],config['system']['file_wrapper_script'])
        services['system'].createSymlink(sam_wrapper_file,config['system']['file_samcli_link'])
        # add sudoers entry
        services['system'].addSudoersEntry(admin_group,config['system']['file_samcli_link'])
        # Now create the folder structure needed
        print("Creating folder structure:")
        config_dict=dict(config['system'])
        for property in config_dict.keys():
            if property.startswith("folder_vhost"):
                directory=config['system'][property]
                if not os.path.isdir(directory):
                    print("\tcreating folder "+directory)
                    services['system'].createDirWithParents(directory,sys_user,sys_group)
                else:
                    #check if ownership is ok
                    owner_user, owner_group = services['system'].getOwnership(directory)
                    if not (owner_user == sys_user and owner_group == sys_group):
                        print("\tfix ownership of folder "+directory)
                        services['system'].chownRecursive(directory,sys_user,sys_group)
                    else:
                        print("\tskip existing folder "+directory)
        try:
            # copy default vhost
            services['template'].copyDefaultVhost(services['system'],config['system']['folder_sam_source_dir'])
            # generate wildcard cert
            cert_default_path=os.path.join(services['template'].folder_vhost,'default','certs')
            services['apache'].generateSSLCertsSelfSigned(cert_default_path,'server',services['system'],config)
        except:
            print("Copy default template failed with exception. Continue anyway.")
        print("Generate default config in /etc/apache2/sites-available/SimpleApacheManager.conf")
        # now copy sam global configuration file to /etc/apache2/sites-enabled
        services['template'].createGlobalApacheConfig(config,services['system'])
        # unlink existing sites-enabled/000-default symlink and replace with new link to sam config
        services['template'].createGlobalSymlink(config['system']['folder_sam_source_dir'],services['system'])
        # LimitUID setting from apache mpm itk worker defaults to 1000 to 6000.
        # We use the www-data user as default user in /var/www/vhosts, and its uid=33.
        # So we relax this settings in the apache security config
        services['apache'].relaxLimitUIDRangeMpmItk()
        # now enable any mising apache modes
        services['apache'].enableNeededModules(services['system'])
        # now reload the apache configuration
        services['apache'].reloadApache(services['system'])
