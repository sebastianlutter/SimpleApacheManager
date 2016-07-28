#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys

import os

from sam.services.IService import IService

__author__ = 'Sebastian Lutter'

class ApacheService(IService):

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
    def reloadApache(self,sys_service):
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
            exitcode, stdout, stderr = sys_service.run_shell_commando(["service", "apache2", "reload"])
            if exitcode != 0:
                print("stdout={}\nstderr={}".format(stdout,stderr))
                msg="Apache coofiguration reload failed. Please fix the configuration manually and restart apache server."
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
        pass
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
        if user == 'root' or user == config['system']['admin_user']:
            # admin goes to /var/www/vhosts/
            return tpl_service.folder_vhost
        else:
            # user have their own vhosts folder
            return os.path.join('/home',user,'webdomains/')


    """
    Get the vhosts folder of the given real user. If root or admin it
    is /var/www/vhosts, else it is /home/USER/web_domains
    :return Tuple containing user and group
    """
    def getOwnershipFor(self,user,config):
        # is this root or admin?
        if user == 'root' or user == config['system']['admin_user']:
            # return tuple with (www-data,www-data)
            return (config['domain']['default_user'],config['domain']['default_group'])
        else:
            # return (username,sam_group)
            return (user,config['system']['admin_group'])