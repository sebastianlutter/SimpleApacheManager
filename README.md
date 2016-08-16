# SimpleApacheManager

Provides a CLI interface to manage vhosts and SSL keys for an apache2 webserver. It provides vhosts for user in their home directory or global in /var/www/vhosts when using root or the admin_user. 
It is released and distributed via setuptools/PyPI/pip for Python 3. It runs on Ubuntu Server 16.04 and Debian 8 systems.

## Status

Alpha status. All main functions are implemented, you can add and remove vhosts and subdomains. Check function is useless at the moment. Not well tested yet, but has been build with non desctructive behavior (it should not delete anything without doing a backup, and it stops if somethings goes wrong).

Documentation as well as speaking error messages are the next steps. Also using letsencrypt instead of self signed certificated for each vhost and subdomain is planned.


## Install

Clone this repository and build the project on your Ubuntu 16.04 server with setuptools / pip.

First of all edit the **config.ini** file and put in your environment details (SimpleApacheManager script path, IP etc.)

To install required python modules for SimpleApacheManager using setuptools and pip run:

    sudo python3 setup.py install
    
The application itself is installed by calling as root user:

    SimpleApacheManager # ./sam_runner.py install

You need to do this with the real root user, not as user with sudo. If you do not have 
access to the root account but you have sudo permissions than run:

    user@server:~$ sudo -s
    root@server:/home/user# su - root
    root@server:~#

After installation as root the application can be executed by calling **samcli** as root user or with the **admin_user** (config.ini) and sudo: 

    root@server:~$ sudo samcli -h
    Script executed with root permissions from user root
    Using config.ini found in /home/user/workspace/github/SimpleApacheManager/config.ini
    Found OSDebian8 environment
    usage: samcli [-h] [-v] {user,check,install,domain} ...
    
    SimpleApacheManager version 0.0.9.
    
    optional arguments:
      -h, --help            show this help message and exit
      -v                    run with verbose output.
    
    sub command help:
      {user,check,install,domain}
                            available subcommands
        check               shows current options and configuration as well as
                            runs some sanity checks.
        install             install the environment integration in the host
                            system. Needs sudo rights.
        user                add, list
        domain              add, addalias, addsub, del, delalias, delsub, list
    
    Example usage:
    
     $ samcli check                                  : shows current options and configuration as well as runs some sanity checks.
     $ samcli install                                : install the environment integration in the host system. Needs sudo rights.
     $ samcli user add mary                          : add a new vhost to the server
     $ samcli user list                              : list all available domains, subdomains and alias
     $ samcli domain add example.org                 : add a new vhost to the server
     $ samcli domain addalias example.org www.foo.de : add an alias domain to a existing domain
     $ samcli domain addsub example.org dl           : add a new subdomain to an existing domain
     $ samcli domain del example.org                 : delete an existing vhost from the server
     $ samcli domain delalias example.org www.foo.de : delete an alias name from an existing domain
     $ samcli domain delsub example.org dl           : del a existing subdomain from an existing domain
     $ samcli domain list                            : list all available domains, subdomains and alias
  

