#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import pprint

from sam.services.IService import IService
from string import Template

__author__ = 'Sebastian Lutter'

class TemplateService(IService):

    folder_tpl_vhost='templates/vhost/'
    folder_tpl_subdomain='templates/subdomain/'
    folder_tpl_apache_etc='templates/system/apache2/'
    folder_tpl_vhost_default='templates/system/default/'
    folder_tpl_user='templates/system/user/web_domains/'

    folder_vhost='/var/www/vhosts'
    folder_vhost_backup='/var/www/backup/'
    folder_vhost_user='/var/www/users'

    file_tpl_apache_conf_global='templates/system/apache2/sam_default.conf'
    file_etc_apache_conf_global='/etc/apache2/sites-available/SimpleApacheManager.conf'
    file_etc_apache_conf_available_link = '/etc/apache2/sites-enabled/000-default.conf'

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

    def check(self,user):
        print("TODO: implement TemplateService.check()")

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
        tpl=os.path.join(config['system']['folder_sam_source_dir'],self.file_tpl_apache_conf_global)
        self.__fillTemplateFromMapping__(tpl,self.file_etc_apache_conf_global,mapping)

    '''
    Load template, replace variables, store modified text in file
    '''
    def __fillTemplateFromMapping__(self, tplfile,destfile, mapping):
        print("\tload template {}, fill it, and store it in {}".format(tplfile,destfile))
        f = open(tplfile)
        # load template file
        text = Template(f.read())
        # replace variables in string
        text = text.safe_substitute(mapping)
        f.close()
        # now override the file with the modified text
        f = open(destfile, "w")
        f.writelines(text)
        f.close()