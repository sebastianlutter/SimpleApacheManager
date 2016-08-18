#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import pprint

import re

from sam.services.IService import IService
from string import Template

__author__ = 'Sebastian Lutter'

class TemplateService(IService):

    folder_tpl_vhost = 'templates/vhost/'
    folder_tpl_subdomain = 'templates/subdomain/'
    folder_tpl_apache_etc = 'templates/system/apache2/'
    folder_tpl_vhost_default = 'templates/system/default/'
    folder_tpl_user = 'templates/system/user/web_domains/'

    folder_vhost = '/var/www/vhosts'
    folder_vhost_backup = '/var/www/backup/'
    folder_vhost_user = '/var/www/users'

    file_tpl_apache_conf_global = 'templates/system/apache2/sam_default.conf'
    file_etc_apache_conf_global = '/etc/apache2/sites-available/SimpleApacheManager.conf'
    file_etc_apache_conf_enabled_link = '/etc/apache2/sites-enabled/000-default.conf'

    # keys of the variables in the template confs
    var_ip = "IP"
    var_domain = "DOMAIN"
    var_user = "USER"
    var_group = "GROUP"
    var_admin_mail = "ADMINMAIL"
    var_subdomain = "SUBDOMAIN"
    var_alias = "#{{ALIAS}}"
    # SSL vars
    var_ssl = "#{{SSL}}"
    var_ssl_key = "KEY"
    var_ssl_crt = "CRT"
    var_subdomain_tpl = "#{{SUBDOMAIN_TPL}}"
    var_etc_apache_include = "#{{INCLUDE}}"

    def __init__(self):
        pass

    def check(self,config,services):
        errors=list()
        srcDir=config['system']['folder_sam_source_dir']
        # go through all variables
        patternFolder=re.compile("^folder_.*$")
        patternFile=re.compile("^file_.*$")
        for var in vars(self.__class__).items():
            # get tuple of varname and value
            varname,value = var
            # what kind is it?
            if patternFile.match(varname):
                if "tpl" in varname:
                    # Template file, check if it exists
                    if not os.path.isfile(os.path.join(srcDir,value)):
                        msg="variable {}: Path {} is not a file.".format(varname,os.path.join(srcDir,value))
                        print("\t"+msg)
                        errors.append(msg)
                elif "link" in varname:
                    # check if link exist, but do not produce error (just print warning)
                    if not os.path.islink(value):
                        msg="variable {}: Path {} is not a link.".format(varname,value)
                        print("\t"+msg)
                        errors.append(msg)
                else:
                    # global file_etc_ vars, check if they exist
                    if not os.path.isfile(value):
                        msg = "variable {}: Path {} is not a file.".format(varname, value)
                        print("\t"+msg)
                        errors.append(msg)
            elif patternFolder.match(varname):
                # check folder vars
                if "tpl" in varname:
                    # Template folder, check if it exists
                    if not os.path.isdir(os.path.join(srcDir,value)):
                        msg="variable {}: Path {} is not a directory.".format(varname,os.path.join(srcDir,value))
                        print("\t"+msg)
                        errors.append(msg)
                elif "vhost" in varname:
                    # VHost folder, check if they exists
                    if not os.path.isdir(value):
                        msg="variable {}:\t Path {}\tis not a directory.".format(varname,value)
                        print("\t"+msg)
                        errors.append(msg)
            else:
                #print("No check implemented for {} = {}".format(varname,value))
                pass
        return errors


    def info(self):
        return "Template service module for generating config from the template stubs."

    def name(self):
        return "VHost service"

    def install(self):
        pass
    """
    Copy the global apache conf template and fill its values
    """
    def createGlobalApacheConfig(self,config,sys_service):
        # create mapping of vars to values
        mapping = dict()
        mapping[self.var_ip] = config['system']['ip']
        mapping[self.var_domain] = config['domain']['default_domain']
        mapping[self.var_admin_mail] = config['DEFAULT']['mail']
        mapping[self.var_user] = config['domain']['default_user']
        mapping[self.var_group] = config['domain']['default_group']
        mapping[self.var_ssl_crt] = config['domain']['default_ssl_cert']
        mapping[self.var_ssl_key] = config['domain']['default_ssl_key']
        # now copy template file to /etc/apache2/sites-available/
        tpl = os.path.join(config['system']['folder_sam_source_dir'],self.file_tpl_apache_conf_global)
        self.__fillTemplateFromMapping__(tpl,self.file_etc_apache_conf_global,mapping)

    """
    Replace the /etc/apache2/sites-enabled/000-default.conf symlink to point
    to our sites-available/SimpleApacheManager.conf
    """
    def createGlobalSymlink(self,source_folder,sys_service):
        # should be a symlink or should not exist
        if os.path.exists(self.file_etc_apache_conf_enabled_link):
            if not os.path.islink(self.file_etc_apache_conf_enabled_link):
                msg="File {} should either be a symlink or should not exist at all. But it exists and is not a symlink. Abort.".format(self.file_etc_apache_conf_enabled_link)
                print("\t"+msg)
                raise Exception(msg)
        # if symlink unlink it
        if os.path.islink(self.file_etc_apache_conf_enabled_link):
            sys_service.unlinkSymlink(self.file_etc_apache_conf_enabled_link)
        # create link to our config
        vhost_conf_file = os.path.join(source_folder,self.file_etc_apache_conf_global)
        if not os.path.isfile(vhost_conf_file):
            msg="File {} does not exist. Cannot symlink to it. Abort."
            print('\t'+msg)
            raise Exception(msg)
        # create the new link
        sys_service.createSymlink(self.file_etc_apache_conf_global, self.file_etc_apache_conf_enabled_link)

    """
    Copy template to new vhost dir. Apply mappings in template and store new configuration.
    The new vhost is not registered in the global config afterwards. Just the skeleton is
    copied and values filled in.
    """
    def generateVHostTemplate(self,domain,config,sys_service,user,vhost_dir,is_user):
        # first of all copy vhost template to dest dir
        #vhost_dir = os.path.join(self.folder_tpl_vhost, domain)
        tpl_dir = os.path.join(config['system']['folder_sam_source_dir'],self.folder_tpl_vhost)
        if not os.path.isdir(tpl_dir):
            print("Template folder "+tpl_dir+" does not exist. Abort.")
            raise Exception("Template folder "+tpl_dir+" does not exist. Abort.")
        # copy the filetree from tpl to its destination
        sys_service.copyFolderRecursive(tpl_dir,vhost_dir)
        # if this is a user vhost, then make the symlink now
        # if this is a user request create the vhost link now
        if is_user:
            sys_service.createSymlink(vhost_dir,os.path.join(config['system']['folder_vhosts'],domain))
        # path of the new vhost configuration
        vhost_conf_path = os.path.join(vhost_dir, "conf/httpd.include")
        # build mapping
        mapping = dict()
        mapping[self.var_ip] = config['system']['ip']
        mapping[self.var_domain] = domain
        mapping[self.var_admin_mail] = config['DEFAULT']['mail']
        mapping[self.var_user] = user
        mapping[self.var_group] = config['system']['admin_group']
        # SSL cert pathes
        mapping[self.var_ssl_crt] = os.path.join(self.folder_vhost, domain, "certs/", domain + ".crt")
        mapping[self.var_ssl_key] = os.path.join(self.folder_vhost, domain, "certs/", domain + ".key")
        self.printMapping(mapping)
        # now apply the mapping and store the new config file
        self.__fillTemplateFromMapping__(vhost_conf_path, vhost_conf_path, mapping)
        # generate a index.html file with domain infos
        self.__generateIndexHtml__(domain,None)

    """
    Print a mapping dict
    """
    def printMapping(self,mapping):
        print("Tamplate mapping:")
        for key, value in mapping.items():
            print('\t\t{} -> {}'.format(key,value))

    """
     Copy template to new subdomain dir. Apply mappings in template and store new configuration.
     The new vhost is not registered in the global config afterwards. Just the skeleton is
     copied and values filled in.
     """
    def generateSubdomainTemplate(self, domain, subdomain,config,sys_service,user,subdomain_dir):
        # first of all copy vhost template to dest dir
        # vhost_dir = os.path.join(self.folder_tpl_vhost, domain)
        tpl_dir = os.path.join(config['system']['folder_sam_source_dir'], self.folder_tpl_subdomain)
        if not os.path.isdir(tpl_dir):
            print("Template folder " + tpl_dir + " does not exist. Abort.")
            raise Exception("Template folder " + tpl_dir + " does not exist. Abort.")
        # copy the filetree from tpl to its destination
        sys_service.copyFolderRecursive(tpl_dir, subdomain_dir)
        # path of the new vhost configuration
        vhost_conf_path = os.path.join(subdomain_dir, "conf/httpd.include")
        # build mapping
        mapping = dict()
        mapping[self.var_ip] = config['system']['ip']
        mapping[self.var_domain] = domain
        mapping[self.var_admin_mail] = config['DEFAULT']['mail']
        mapping[self.var_subdomain] = subdomain
        mapping[self.var_user] = user
        mapping[self.var_group] = config['system']['admin_group']        # first generate cert for subdomain.domain.org
        # SSL cert pathes
        mapping[self.var_ssl_crt] = os.path.join(self.folder_vhost, domain, "subdomains",subdomain,"certs/", subdomain + "." + domain + ".crt")
        mapping[self.var_ssl_key] = os.path.join(self.folder_vhost, domain, "subdomains",subdomain, "certs/", subdomain + "." + domain + ".key")
        self.printMapping(mapping)
        # now apply the mapping and store the new config file
        self.__fillTemplateFromMapping__(vhost_conf_path, vhost_conf_path, mapping)
        # generate a subdomain index.html file with domain infos
        self.__generateIndexHtml__(domain, subdomain)



    """
    Copy the default vhost to its destination in /var/www/vhosts/default
    """
    def copyDefaultVhost(self,sys_service,sam_src_folder):
        # tpl path
        tpl_dir=os.path.join(sam_src_folder,self.folder_tpl_vhost_default)
        # destination /var/www/vhosts/default
        dest_dir=os.path.join(self.folder_vhost,'default')
        if os.path.exists(dest_dir):
            print('\tskip copy of default vhost {}, it already exists.'.format(dest_dir))
            return
        sys_service.copyFolderRecursive(tpl_dir,dest_dir)


    '''
    Load template, replace variables, store modified text in file
    '''
    def __fillTemplateFromMapping__(self, tplfile,destfile, mapping):
        print("\tload template {}, fill it, and store it in {}".format(tplfile,destfile))
        with open(tplfile) as f:
            # load template file
            text = Template(f.read())
            # replace variables in string
            text = text.safe_substitute(mapping)
        # now override the file with the modified text
        with open(destfile, "w") as f:
            f.writelines(text)

    '''
    Generate a domain or subdomain index.html file. Depending on subdomain is filled
    the template and destination folder is choosen.
    '''
    def __generateIndexHtml__(self, domain, subdomain=None):
        if subdomain == None:
            tpl=os.path.join(self.folder_tpl_vhost,"httpdocs/index.html")
            file=os.path.join(self.folder_vhost,domain, "httpdocs/index.html")
        else:
            tpl = os.path.join(self.folder_tpl_subdomain, "httpdocs/index.html")
            file = os.path.join(self.folder_vhost, domain,'subdomains',subdomain,"httpdocs/index.html")
        with open(file, "r") as f:
                vhostConf = Template(f.read())
        # create mapping
        mapping = dict()
        mapping[self.var_domain] = domain
        mapping[self.var_subdomain] = subdomain
        # write file
        newIndexHtml = vhostConf.safe_substitute(mapping)
        with open(file, "w") as f:
            f.write(newIndexHtml)

