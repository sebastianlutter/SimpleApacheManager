#!/usr/bin/python3
# -*- coding: utf-8 -*-
from grp import getgrnam
import grp
import os
import subprocess
import sys

__author__ = 'Sebastian Lutter'
#TODO: clean old code
from pwd import getpwnam
from sam.services.IService import IService

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
        raise NotImplementedError("ERROR: Should have implemented this")

    def listLinkedUsers(self):
        pass

    # check if a user exists in the system
    def __checkIfUserExistsInOS__(self,username):
        try:
            user=getpwnam(username)
            return True
        except KeyError:
            return False

    def checkIfUserExistsInPhoenixToolkit(self,username):
        pass

    def __addNewUser__(self,username):
        pass

    def __addUserToSudoGroup__(self):
        pass

    def info(self):
        return "User service module for reload and restart the webserver."


    def name(self):
        return "User service"