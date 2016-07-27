#!/usr/bin/python3
# -*- coding: utf-8 -*-
import pwd

import grp

import shutil

import time

from sam.services.IService import IService
import subprocess
import sys
import os

"""
Do shell calls and error handling as service.
"""
__author__ = 'Sebastian Lutter'

class SystemService(IService):

    def __init__(self):
        pass

    """
    Check if the service environment is sane, and all option in config.ini are sane
    """
    def check(self,config):
        # check if we can succesfully run shell commands
        com=['ls']
        exitcode,stdout,stderr = self.run_shell_commando(com)
        if exitcode != 0:
            print("Error checking system service shell execution: "+' '.join(com))
            print('exitcode={}\nstdout={}\nstderr={}'.format(exitcode,stdout,stderr))
            return False
        # check if config values are sane
        sys_ip=config['system']['ip']
        if sys_ip==None:
            raise Exception('config.ini has no "ip" setting in [system] section')
        print("config.system.ip="+sys_ip)
        #TODO: get interfaces ips and compare them to the config
        return True

    def info(self):
        return "System service module for running shell commandos."

    def name(self):
        return "system service"

    def install(self):
        pass

    """
    Run a shell command and its arguments. Return a tupel of (exit code, stdout, stderr), or (1,None,None) if error
    happend.
    """
    def run_shell_commando(self,commandArr):
        try:
            print(" Running shell command: "+' '.join(commandArr))
            with subprocess.Popen([' '.join(commandArr)],stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE, shell=True, universal_newlines=True) as proc:
                resultStdout, resultStderr = proc.communicate()
                exitcode=proc.returncode
            return (exitcode,resultStdout,resultStderr)
        except:
            e = sys.exc_info()[0]
            print("An error happend while executing "+' '.join(commandArr))
            print(e)
            return (1,None,None)


    """
    Create a directory tree with all needed parent directories. Chown it to the given user and group.
    :return True if folder has been created and permission has been set, else False
    """
    def createDirWithParents(self,dir,user,group):
        if not os.path.isdir(dir):
            os.makedirs(dir)
        else:
            print("Directory "+dir+" already exists.")
            return False
        self.chownRecursive(dir,user,group)

    """
    Recursive chown of path to the given user and group
    """
    def chownRecursive(self,path,user,group):
        print('\tchown recursive {} for {}:{}'.format(path,user,group))
        if os.path.isdir(path):
            uid=pwd.getpwnam(user).pw_uid
            gid=grp.getgrnam(group).gr_gid
            # crawl the subtree and set permissions as given
            for root, dirs, files in os.walk(path):
                os.chown(root, uid, gid)
                for d in dirs:
                    os.chown(os.path.join(root, d), uid, gid)
                for f in files:
                    os.chown(os.path.join(root, f), uid, gid)

    """
    Returns a ( user , group ) tuple with the ownership info from the given file or directory
    """
    def getOwnership(self,filename):
        return ( pwd.getpwuid(os.stat(filename).st_uid).pw_name
                 , grp.getgrgid(os.stat(filename).st_gid).gr_name )

    """
    Delete a symlink
    """
    def unlinkSymlink(self, linkpath):
        if not os.path.islink(linkpath):
            raise Exception("Cannot unlink "+linkpath+". Is not a symlink.")
        print("\tunlink symlink "+linkpath)
        os.unlink(linkpath)

    """
    Create a symlink with linkname pointing to src
    """
    def createSymlink(self, src, linkname):
        if not os.path.exists(src):
            print("\tsymlink destination " + src + " does not exist. Abort.")
            raise Exception("\tsymlink destination " + src + " does not exist. Abort.")
        if not os.path.islink(linkname):
            print("\tsymlink " + linkname + " --> " + src)
            os.symlink(src, linkname)
        else:
            print("\t\tdo not touch existing link " + src)
        return os.path.islink(linkname)

    """
    Delete the given folder recursive. Ignore Errors, just do it.
    :return True if delete succeeded, else False
    """
    def deleteFolderRecursive(self, path):
        if not os.path.isdir(path):
            print("\tERROR:" + path + " is not a directory. Abort.")
            return False
        # delete folder ignore errors
        shutil.rmtree(path, True, onerror=None)
        # check if dir has been deleted
        return not os.path.isdir(path)

    """
    Create a tar.bz2 from the given path, and store it in /var/www/vhosts/backup
    :path Folder to backup
    :filename Filename of the backup without suffix. Name will be 2016_07_27_12_07_12__FILENAME.tar.bz2
    :archiveFolder Folder to store the backup file in.
    :return True if backup was successful, else return False
    """
    def createFolderBackup(self, path, filename,archiveFolder):
        abspath = os.path.abspath(path)
        if not os.path.isdir(abspath):
            print("Folder " + abspath + " does not exist. Abort.")
            return False
        # Create archive name with timestamp
        timestamp = time.strftime("%Y_%m_%d_%H_%M_%S__", time.localtime())
        domain = os.path.basename(abspath)
        backupfile = os.path.join("", timestamp + filename + ".tar.bz2")
        print("\tcreated backup of " + path + ": " + backupfile)
        exitcode,stdout,stderr = self.run_shell_commando(["tar", "cfj", backupfile, path])
        if exitcode != 0:
            print("Error while doing backup:\n{}\n{}".format(stdout,stderr))
            return False
        else:
            return True
    """
    Copy filetree from source to destination. Destination dir must not exist. Symlinks are
    alllowed.
    """
    def copyFolderRecursive(self,src,dst):
        print("\tcopy filetree {} to {}".format(src,dst))
        shutil.copytree(src, dst, symlinks=True)
