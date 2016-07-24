#!/usr/bin/python3
# -*- coding: utf-8 -*-
from grp import getgrnam
import grp
import os
import subprocess
import sys
from filesystem import FolderWorker

__author__ = 'Sebastian Lutter'
#TODO: clean old code
from pwd import getpwnam
from sam.services.IService import IService

class UserServices(IService):

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


    def checkInstall(self):
        raise NotImplementedError("ERROR: Should have implemented this")

    def init(self):
        raise NotImplementedError("ERROR: Should have implemented this")


    def listLinkedUsers(self):
        #print("Collecting all users that are part of the phoenix toolkit system")
        fw = FolderWorker.FolderWorker()
        out = []
        for folder in fw.getFolderList(Config.FOLDER_VHOST_USERS):
            out.append(os.path.basename(folder))
        return out

    # check if a user exists in the system
    def __checkIfUserExistsInOS__(self,username):
        try:
            user=getpwnam(username)
            return True
        except KeyError:
            return False

    def checkIfUserExistsInPhoenixToolkit(self,username):
        listAddedUsers = self.listLinkedUsers()
        if not Config.USER in listAddedUsers:
            return False
        else:
            return True

    def __addNewUser__(self,username):
        print("Add new user "+username)
        if username in self.listLinkedUsers():
            print("\t\tuser "+username+" does already exist. Abort.")
            return False
        # construct path to template
        tpl_path=os.path.join(Config.FOLDER_SCRIPT_PFAD, Config.FOLDER_TPL_USER)
        fw = FolderWorker.FolderWorker()
        user_domain_path=os.path.join("/home", username, "web_domains")
        fw.copyTemplateFolder(tpl_path, user_domain_path)
        # symlink users web_domains folder to /var/www/users/$USERNAME
        fw.createSymLink(user_domain_path, os.path.join(Config.FOLDER_VHOST_USERS, username))
        # change user and group of created folder
        fw.setPermissionsRecursive(user_domain_path,username,Config.SUDO_GROUP_NAME)
        #add user to phoenix_toolkit group if not already member of
        self.__addUserToSudoGroup__()
        return True

    def __addUserToSudoGroup__(self):
        try:
            gid=getgrnam(Config.SUDO_GROUP_NAME).gr_gid
        except KeyError:
            print("\n\nThe group "+Config.SUDO_GROUP_NAME+" does not exist on the system. Have you forgot to install the phoenix toolkit? \nAbort.\n")
            sys.exit(1)
        # get user name from params
        username=sys.argv[3]
        # get list of all groups of an user
        groups = [g.gr_name for g in grp.getgrall() if username in g.gr_mem]
        # check if sudo group is in this list
        if Config.SUDO_GROUP_NAME in groups:
            print("\tuser "+username+" is already member of "+Config.SUDO_GROUP_NAME)
            return True
        else:
            print("Add user: "+username + " to group "+Config.SUDO_GROUP_NAME)
            if subprocess.call(["gpasswd", "-a", username, Config.SUDO_GROUP_NAME]) != 0:
                print("Fehler beim Erstellen des Backups.")
                return False
            else:
                return True

    def info(self):
        return "User service module for reload and restart the webserver."


    def name(self):
        return "User service"