#SUBDOMAIN $DOMAIN START#
<VirtualHost $IP:80>
    ServerName   $SUBDOMAIN.$DOMAIN:80
    #{{ALIAS}}

    ServerAdmin  $ADMINMAIL
    DocumentRoot /var/www/vhosts/$DOMAIN/subdomains/$SUBDOMAIN/httpdocs
    CustomLog  /var/www/vhosts/$DOMAIN/logs/access_log combined
    ErrorLog  /var/www/vhosts/$DOMAIN/logs/error_log

	<IfModule mpm_itk_module>
        AssignUserId $USER $GROUP
        MaxClientsVHost 50
        NiceValue 10
    </IfModule>

    <IfModule mod_ssl.c>
            SSLEngine off
    </IfModule>
    <Directory  /var/www/vhosts/$DOMAIN/subdomains/$SUBDOMAIN/httpdocs>
        <IfModule mod_php5.c>
            php_admin_flag engine on
            php_admin_flag safe_mode on
            php_admin_value open_basedir "/var/www/vhosts/$DOMAIN/subdomains/$SUBDOMAIN/httpdocs:/tmp"
        </IfModule>
        Options +Includes +FollowSymLinks
        AllowOverride All
    </Directory>

    Include /var/www/vhosts/$DOMAIN/subdomains/$SUBDOMAIN/conf/vhost.conf
</VirtualHost>

<VirtualHost $IP:443>
	ServerName   $SUBDOMAIN.$DOMAIN:443
	#{{ALIAS}}

	ServerAdmin  $ADMINMAIL
	DocumentRoot /var/www/vhosts/$DOMAIN/subdomains/$SUBDOMAIN/httpdocs
	CustomLog  /var/www/vhosts/$DOMAIN/logs/access_ssl_log combined
	ErrorLog  /var/www/vhosts/$DOMAIN/logs/error_log
	
	SSLEngine on
	SSLVerifyClient none
    SSLCertificateFile    $CRT
    SSLCertificateKeyFile $KEY

    <IfModule mpm_itk_module>
        AssignUserId $USER $GROUP
        MaxClientsVHost 50
        NiceValue 10
    </IfModule>
    	
	<Directory  /var/www/vhosts/$DOMAIN/subdomains/$SUBDOMAIN/httpdocs>
	    <IfModule mod_php5.c>
		    php_admin_flag engine on
		    php_admin_flag safe_mode on
		    php_admin_value open_basedir "/var/www/vhosts/$DOMAIN/subdomains/$SUBDOMAIN/httpdocs:/tmp"
	    </IfModule>
		SSLRequireSSL
		Options +Includes +FollowSymLinks
		AllowOverride All
	</Directory>

	Include /var/www/vhosts/$DOMAIN/subdomains/$SUBDOMAIN/conf/vhost_ssl.conf
</VirtualHost>
#SUBDOMAIN $DOMAIN END#