#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import pwd
import grp

__author__ = 'Sebastian Lutter'

from pwd import getpwnam
from grp import getgrnam

from sam.services.IService import IService


class UserService(IService):

    def __init__(self):
        pass

    def check(self,config,services):
        errors=list()
        return errors

    def info(self):
        return "User service module for adding and removing user."

    def name(self):
        return "User service"

    def install(self):
        pass

    """
    Add the user to the group with sudo permissions to samcli.
    Checks if user exists in OS.
    """
    def addNewUser(self, username,tpl_service,sys_service,config):
        print("\tadd new user "+username)
        if username in self.listLinkedUsers(sys_service,tpl_service.folder_vhost_user):
            print("\t\tuser "+username+" does already exist. Abort.")
            return False
        # construct path to template
        tpl_path=os.path.join(config['system']['folder_sam_source_dir'], tpl_service.folder_tpl_user)
        user_domain_path=os.path.join("/home", username, "web_domains")
        sys_service.copyFolderRecursive(tpl_path, user_domain_path)
        # symlink users web_domains folder to /var/www/users/$USERNAME
        sys_service.createSymlink(user_domain_path, os.path.join(tpl_service.folder_vhost_user, username))
        # change user and group of created folder
        sys_service.chownRecursive(user_domain_path,username,config['system']['admin_group'])
        #add user to phoenix_toolkit group if not already member of
        if not self.checkIfUserIsInGroup(username,config['system']['admin_group']):
            self.addUserToGroup(username,config['system']['admin_group'],sys_service)
        return True

    """
    Add the given user to the given group
    """
    def addUserToGroup(self,user,group,sys_service):
        exitcode, stdout, stderr = sys_service.run_shell_commando(['gpasswd','-a',user, group])
        if exitcode != 0:
            msg='Add user {} to group {} failed.\nstdout={}\nstderr={}'.format(user,group,stdout,stderr)
            print(msg)
            raise Exception(msg)

    """
    Check if a given user is in the given group
    """
    def checkIfUserIsInGroup(self,user,group):
        # get all groups of the given user
        groups = [g.gr_name for g in grp.getgrall() if user in g.gr_mem]
        gid = pwd.getpwnam(user).pw_gid
        groups.append(grp.getgrgid(gid).gr_name)
        # check if user is in group
        return group in groups


    """
    check if a user exists in the system
    """
    def checkIfUserExistsInOS(self,username):
        try:
            user=getpwnam(username)
            return True
        except KeyError:
            return False

    """
    check if a user exists in the system
    """
    def checkIfGroupExistsInOS(self, group):
        try:
            group = getgrnam(group)
            return True
        except KeyError:
            return False

    """
    create a group in the OS
    """
    def createOSGroup(self,group,system_service):
        exitcode, stdout, stderr = system_service.run_shell_commando(["addgroup",group])
        # check if it exists now
        if exitcode != 0:
            print("Failed to add group " + group + " to operation system.\nstdout="+stdout+"\nstderr=" + stderr)
            sys.exit(1)

    def listLinkedUsers(self,sys_service,user_folder):
        out = []
        for folder in sys_service.getFolderList(user_folder):
            out.append(os.path.basename(folder))
        return out

    """
    Check if user is part of the SimpleApacheManager OS group (to get sudo access)
    """
    def checkIfSAMUserExists(self,username,sys_service,tpl_service):
        listAddedUsers = self.listLinkedUsers(sys_service,tpl_service.folder_vhost_user)
        return username in listAddedUsers

