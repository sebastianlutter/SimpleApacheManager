#!/usr/bin/python3
# -*- coding: utf-8 -*-

from sam.services.IService import IService

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

    file_etc_apache_conf_global='/etc/apache2/sites-enabled/000-default.conf'

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