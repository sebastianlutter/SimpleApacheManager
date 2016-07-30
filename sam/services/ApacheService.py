#!/usr/bin/python3
# -*- coding: utf-8 -*-
import re
import string
import sys

import os

from sam.services.IService import IService

__author__ = 'Sebastian Lutter'

class ApacheService(IService):

    script_ssl_cert_creation='scripts/generateSSLcerts.sh'

    needed_modules=['ssl']

    def __init__(self):
        pass

    def check(self,config):
        print("TODO: implement ApacheService.check()")

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
        # crete cert by calling script
        script_path=os.path.join(config['system']['folder_sam_source_dir'],self.script_ssl_cert_creation)
        exitcode,stdout,stderr=sys_service.run_shell_commando([script_path, company, domain, email, out_path])
        if exitcode!=0:
            msg='Error creating cert for domain {} using script {}.\nstdout={}\nstderr={}'.format(domain,stdout,stderr)
            print(msg)
            raise Exception(msg)
        else:
            print(stdout)
    """
        # check if out_folder exists
        if not os.path.isdir(out_folder):
            raise Exception('Cannot create SSL certs in {}, folder does not exist.'.format(out_folder))
        CERT_FILE = os.path.join(out_folder,domain,'.crt')
        KEY_FILE = os.path.join(out_folder,domain,'.key')
        # create a key pair
        k = crypto.PKey()
        k.generate_key(crypto.TYPE_RSA, 2048)
        # create a self-signed cert
        cert = crypto.X509()
        cert.get_subject().C = "DE"
        cert.get_subject().ST = "Berlin"
        cert.get_subject().L = "Berlin"
        cert.get_subject().O = domain
        cert.get_subject().OU = domain+' owner'
        cert.get_subject().CN = domain
        cert.set_serial_number(1000)
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(10*365*24*60*60)
        cert.set_issuer(domain)
        cert.set_pubkey(k)
        cert.sign(k, 'sha1')
        with open(CERT_FILE, "wt") as cert:
            cert.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
        with open(KEY_FILE, "wt") as key:
            key.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))
"""


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
     Append an include line on the global apache config to include
     a vhost config there
     '''
    def addIncludeToGlobalConf(self, includePath, tpl_service):
        configFile=tpl_service.file_etc_apache_conf_global
        key=tpl_service.var_etc_apache_include
        print("\tappend include " + includePath + " to " + configFile)
        # load template file
        with open(configFile, "r") as f:
            apacheConfString = f.read()
        # append include
        apacheConfString = apacheConfString.replace(key, "Include " + includePath + "\n" + key)
        # replace key in template with entry and key
        with open(configFile, "w") as f:
            f.write(apacheConfString)

    """
    Deletes a include entry made by self.addIncludeToGlobalConf
    """
    def deleteIncludeFromGlobalConf(self, includePath, tpl_service):
        configFile = tpl_service.file_etc_apache_conf_global
        print("\tremove include " + includePath + " from " + configFile)
        # Load content of file
        with open(configFile, "r") as f:
            apacheConfString = f.read()
        # remove the include from the string
        apacheConfString = apacheConfString.replace("Include " + includePath + "\n", "");
        with open(configFile, "w") as f:
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
            modules_enabled_list.append(line.split(' ')[0])
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
    def getExistingVHostsList(self,tpl_service,sys_service):
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
            subdomainList =sys_service.getFolderList()
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

