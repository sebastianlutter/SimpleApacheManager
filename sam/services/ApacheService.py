#!/usr/bin/python3
# -*- coding: utf-8 -*-
import pprint
import re
import string
import sys

import os

from sam.services.IService import IService

__author__ = 'Sebastian Lutter'

class ApacheService(IService):

    script_ssl_cert_creation='scripts/generateSSLcerts.sh'

    needed_modules=['ssl','proxy_html','rewrite']

    def __init__(self):
        pass

    def check(self,config,services):
        errors=list()
        return errors

    def info(self):
        return "Apache service module for reload and restart the webserver."

    def name(self):
        return "ApacheService"

    def install(self):
        pass

    """
    Check the apache configuration and reload apache configuration if check is ok.
    """
    def reloadApache(self,sys_service,restart=False):
        # Testen, ob die Konfiguration noch funktioniert
        try:
            print("\tCheck apache configuration for errors")
            exitcode,stdout,stderr = sys_service.run_shell_commando(["apache2ctl", "configtest"])
            if exitcode != 0:
                print("stdout={}\nstderr={}".format(stdout,stderr))
                msg="Apache coofiguration has errors. Abort to restart apache. Please fix the configuration manually."
                print(msg)
                raise Exception(msg)
            # everything seems ok, reload apache service
            command = 'restart' if restart else 'reload'
            exitcode, stdout, stderr = sys_service.run_shell_commando(["service", "apache2", command])
            if exitcode != 0:
                print("stdout={}\nstderr={}".format(stdout,stderr))
                msg="Apache coniguration reload failed. Please fix the configuration manually and restart apache server."
                print(msg)
                raise Exception(msg)
        except OSError:
            msg="An error happend while apache was restarted. Abort. "
            print(msg)
            raise Exception(msg)
        except:
            msg="Unexpected error:", sys.exc_info()[0]
            print(msg)
            raise Exception(msg)
        return True


    """
    Generate self signed server certificates for the apache webserver
    """
    def generateSSLCertsSelfSigned(self,out_folder,domain,sys_service,config):
        print("\tgenerate SSL certs for "+domain)
        company=domain
        email=config['DEFAULT']['mail']
        out_path = os.path.join(out_folder, domain)
        print("\ncreate SSL certificate for " + domain + " in folder " + out_path)
        # create cert by calling script
        script_path=os.path.join(config['system']['folder_sam_source_dir'],self.script_ssl_cert_creation)
        exitcode,stdout,stderr=sys_service.run_shell_commando([script_path, company, domain, email, out_path])
        if exitcode!=0:
            msg='Error creating cert for domain {} using script {}.\nstdout={}\nstderr={}'.format(domain,stdout,stderr)
            print(msg)
            raise Exception(msg)
        else:
            print(stdout)


    """
    Generate letencrypt server certificates for the apache webserver
    """
    def generateSSLCertsLetsencrypt(self,out_folder,domain,sys_service,config):
        # check ACME letsencrypt client and download if missing
        sys_service.downloadLetsEncryptClient(config['system']['folder_sam_source_dir'])
        print("\tgenerate SSL certs for "+domain)
        company=domain
        email=config['DEFAULT']['mail']
        out_path = os.path.join(out_folder, domain)
        print("\ncreate SSL certificate for " + domain + " in folder " + out_path)
        # create cert by calling script
        script_path=os.path.join(config['system']['folder_sam_source_dir'],self.script_ssl_cert_creation)
        exitcode,stdout,stderr=sys_service.run_shell_commando([script_path, company, domain, email, out_path])
        if exitcode!=0:
            msg='Error creating cert for domain {} using script {}.\nstdout={}\nstderr={}'.format(domain,stdout,stderr)
            print(msg)
            raise Exception(msg)
        else:
            print(stdout)


    """
    Get the vhosts folder of the given real user. If root or admin it
    is /var/www/vhosts, else it is /home/USER/web_domains
    """
    def getVHostFolderFor(self,user,tpl_service,config):
        # is this root or admin?
        if user == 'root' or user == config['system']['admin_user'] \
                or user == config['domain']['default_user']:
            # admin goes to /var/www/vhosts/
            return tpl_service.folder_vhost
        else:
            # user have their own vhosts folder
            return os.path.join('/home',user,'web_domains/')


    """
    Get the vhosts folder of the given real user. If root or admin it
    is /var/www/vhosts, else it is /home/USER/web_domains
    :return Tuple containing user and group
    """
    def getOwnershipFor(self,user,config):
        # is this root or admin?
        if user == 'root' or user == config['system']['admin_user']\
                or user == config['domain']['default_user']:
            # return tuple with (www-data,www-data)
            return (config['domain']['default_user'],config['domain']['default_group'])
        else:
            # return (username,sam_group)
            return (user,config['system']['admin_group'])



    '''
     Append an include line to a apache config
     '''
    def addIncludeToConf(self, includePath, config_path, key):
        print("\tappend include " + includePath + " to " + config_path+" (key "+key+")")
        # load template file
        with open(config_path, "r") as f:
            apacheConfString = f.read()
        # append include
        apacheConfString = apacheConfString.replace(key, "Include " + includePath + "\n" + key)
        # replace key in template with entry and key
        with open(config_path, "w") as f:
            f.write(apacheConfString)

    """
    Deletes a include entry made by self.addIncludeToConf
    """
    def deleteIncludeFromConf(self, includePath, config_path):
        print("\tremove include " + includePath + " from " + config_path)
        # Load content of file
        with open(config_path, "r") as f:
            apacheConfString = f.read()
        # remove the include from the string
        apacheConfString = apacheConfString.replace("Include " + includePath + "\n", "");
        with open(config_path, "w") as f:
            f.write(apacheConfString)

    def addAliasToConf(self, alias, config_path, key):
        entry = "ServerAlias " + alias
        print("\tappend entry " + entry + " to " + config_path + " (key " + key + ")")
        with open(config_path, "r") as f:
            apacheConfString = f.read()
            # check if Alias is already in the file
        if entry in apacheConfString:
            msg="alias {} already exists in file {}.\nAbort.".format(alias, config_path)
            print("\t"+msg)
            raise Exception(msg)
            # replace variable in conf with entry and variable
        apacheConfString = apacheConfString.replace(key, entry + "\n" + key)
        with open(config_path, "w") as f:
            f.write(apacheConfString)

    """
    Deletes a alias entry made by self.addAliasToConf
    """
    def deleteAliasFromConf(self, alias, config_path):
        entry = "ServerAlias " + alias
        print("\tremove alias " + alias + " from " + config_path)
        # Load content of file
        with open(config_path, "r") as f:
            apacheConfString = f.read()
        # check if alias does exist
        if not (entry in apacheConfString):
            msg="alias {} does not exists in file {}, cannot remove it.\nAbort.".format(alias, config_path)
            print("\t"+msg)
            raise Exception(msg)
        # remove the include from the string
        apacheConfString = apacheConfString.replace(entry + "\n\t", "");
        with open(config_path, "w") as f:
            f.write(apacheConfString)

    """
    Since Apache 2.4 the mpm itk worker has a user id limit from 1000 to 6000. www-data user
    has id 33 and is not allowed.
    Add configuration to /etc/apache2/conf-enabled/security.conf to relax this to 1 to 6000
    """
    def relaxLimitUIDRangeMpmItk(self):
        setting='<IfModule mpm_itk_module>\n\tLimitUIDRange 1 6000\n\tLimitGIDRange 1 6000\n</IfModule>\n'
        file_path='/etc/apache2/conf-available/security.conf'
        # check if entry already exists
        with open(file_path,'r') as file:
            if re.search('^.*LimitUIDRange.*$', file.read(), flags=re.M):
                print('\tLimitUIDRange setting exists in {}. Abort.'.format(file_path))
                return False
        # open file in append mode and add line
        print("\tadding relaxed LimitUIDRange setting to file "+file_path)
        with open(file_path,'a') as file:
            file.write(setting+'\n')
            return True

    """
    Enable needed modules of the apache webserver
    """
    def enableNeededModules(self,sys_service):
        # get list of enabled modules
        exitcode,stdout,stderr = sys_service.run_shell_commando(['apache2ctl','-M'])
        if exitcode!=0:
            msg="Was not able to call apache2ctl -M.\nstdout={}\nstderr={}".format(stdout,stderr)
            print(msg)
            raise Exception(msg)
        # check stdout for enabled module names
        missing=list()
        modules_enabled_list=list()
        for line in stdout.split('\n'):
            # format of a line: module_name (type)
            # only add module_name
            entry=line.strip().split(' ')[0].split('_')[0]
            modules_enabled_list.append(entry)
        # now check each needed module against the enabled list
        for needed_module in self.needed_modules:
            if not needed_module in modules_enabled_list:
                print('\tapache module {} is not enabled'.format(needed_module))
                missing.append(needed_module.split(' ')[0])
            else:
                print('\tapache module {} is already enabled. Skip it.'.format(needed_module))
        # skip here if there are no missing modules
        if len(missing)==0:
            print('\tall needed apache modules are enabled. No need to enable modules. ')
            return
        # enable each missing needed module using a2enmod
        for missing_module in missing:
            # enable the needed modules
            exitcode,stdout,stderr=sys_service.run_shell_commando(['a2enmod',missing_module])
            if exitcode!=0:
                msg='Enable apache module failed.\nstdout={}\nstderr={}'.format(stdout,stderr)
                print(msg)
                raise Exception(msg)
        # everything is fine :)
        print('\tsuccessfully enabled {} needed apache modules.'.format(len(missing)))

    """
    Print overview of all domains, subdomains and alias to console.
    """
    def printExistingVHostsList(self, tpl_service, sys_service):
        print("List available domains\n")
        # get list of folders in /var/www/vhosts
        fileList = sys_service.getFolderList(tpl_service.folder_vhost)
        if len(fileList) < 1:
            print("\t -- no domains configured yet")
            return True
        for i in fileList:
            domain = os.path.basename(i)
            if domain == "default" or domain == "backup":
                continue
            print("Domain\t" + domain)
            # Existiert eine Konfiguration?
            if os.path.exists(os.path.join(i, "conf/httpd.include")):
                # Testen ob AliasNames vorhanden
                files = open(os.path.join(i, "conf/httpd.include"), 'r')
                filelist = files.readlines()
                files.close()
                # search for alias domain entries
                aliasDict = dict()
                for i in filelist:
                    if re.match(".*ServerAlias.*", i):
                        key = i.replace("\n", "").replace("\t", "").replace("ServerAlias", "").replace(" ", "")
                        if (not (key in aliasDict)):
                            aliasDict[key] = "Done"
                            print("\tALIAS\t" + key)
            # Search for subdomains
            sub_path=os.path.join(tpl_service.folder_vhost, domain, "subdomains")
            if not os.path.isdir(sub_path):
                continue
            # get list of subfolders in subdomain
            subdomainList =sys_service.getFolderList(sub_path)
            # are subdomains available
            if (len(subdomainList) > 0):
                # if so, list them
                for j in subdomainList:
                    subdomain = os.path.basename(j)
                    # don't show hidden files
                    if re.match("^\w.*$", subdomain):
                        print("\tSUBDOMAIN\t" + subdomain + "." + domain)
                        pass
        return True

