#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import pwd
import grp

__author__ = 'Sebastian Lutter'
#TODO: clean old code
from pwd import getpwnam
from grp import getgrnam

from sam.services.IService import IService
from sam.services.SystemService import SystemService

class UserService(IService):

    def __init__(self):
        pass

    def execute(self,jobtype):
        #TODO: split into a method for each (list, add)
        if jobtype == self.job.TYPE_USER_LIST:
            userList=self.listLinkedUsers()
            if len(userList) == 0:
                print("No users found")
            else:
                print("\tThe following users are known to the phoenix toolkit:\n")
                for u in userList:
                    print("\t "+u)
            return True
        elif jobtype == self.job.TYPE_USER_ADD:
            userName=alias = sys.argv[3].lower()
            return self.__addNewUser__(userName)
        else:
            print("User module does not know jobtype "+jobtype)

    def check(self,config):
        pass

    def info(self):
        return "User service module for adding and removing user."

    def name(self):
        return "User service"

    def install(self):
        pass

    """
    Returns true if script has been called with sudo permissions.
    """
    def sudoPermissionsAvailable(self):
        # check if we have sudo rights
        return os.geteuid() == 0

    """
    Add the user to the group with sudo permissions to samcli.
    Checks if user exists in OS.
    """
    def addNewUser(self, username):
        pass

    """
    Add the given user to the given group
    """
    def addUserToGroup(self,user,group):
        pass

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

    def __listLinkedUsers__(self):
        pass

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
