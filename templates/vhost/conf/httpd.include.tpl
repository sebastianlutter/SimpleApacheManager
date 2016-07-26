# Diese Datei soll nicht editiert werden. Zusätzliche Konfiguration in die folgenden Dateien schreiben: 
# /var/www/vhosts/$DOMAIN/conf/vhost.conf
# /var/www/vhosts/$DOMAIN/conf/vhost_ssl.conf
# /var/www/vhosts/$DOMAIN/subdomains/<subdomain-name>/conf/vhost.conf

<IfModule mod_ssl.c>

#
# SSL encrypted (https://) web access
#
<VirtualHost $IP:443>
	ServerName   $DOMAIN:443
	ServerAlias  www.$DOMAIN
	UseCanonicalName Off
	
	#{{ALIAS}}

	ServerAdmin  $ADMINMAIL
	DocumentRoot /var/www/vhosts/$DOMAIN/httpdocs

	CustomLog  /var/www/vhosts/$DOMAIN/logs/access_ssl_log combined
	ErrorLog  /var/www/vhosts/$DOMAIN/logs/error_log
	
	SSLEngine on
	SSLVerifyClient none
    SSLCertificateFile    $CRT
    SSLCertificateKeyFile $KEY

	#{{SSL}}

	<IfModule mpm_itk_module>
        AssignUserId $USER $GROUP
        MaxClientsVHost 50
        NiceValue 10
    </IfModule>

	<Directory /var/www/vhosts/$DOMAIN/httpdocs>
	    <IfModule mod_php5.c>
    		php_admin_flag engine on
#          php_admin_flag engine off
		    php_admin_flag safe_mode on
		    php_admin_value open_basedir "/var/www/vhosts/$DOMAIN/httpdocs:/tmp"
	    </IfModule>

		SSLRequireSSL
		Options +Includes +FollowSymLinks
		AllowOverride All
	</Directory>

	Include /var/www/vhosts/$DOMAIN/conf/vhost_ssl.conf
</VirtualHost>

</IfModule>

#
# Standard (http://) web access
#
<VirtualHost $IP:80>
	ServerName   $DOMAIN:80
	ServerAlias  www.$DOMAIN
	#{{ALIAS}}

	UseCanonicalName Off

	ServerAdmin $ADMINMAIL
	DocumentRoot /var/www/vhosts/$DOMAIN/httpdocs
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

	<Directory /var/www/vhosts/$DOMAIN/httpdocs>
	    <IfModule mod_php5.c>
		    php_admin_flag engine on
#		    php_admin_flag engine off
		    php_admin_flag safe_mode on
		    php_admin_value open_basedir "/var/www/vhosts/$DOMAIN/httpdocs:/tmp"
	    </IfModule>
		Options +Includes +FollowSymLinks
		AllowOverride All
	</Directory>

	Include /var/www/vhosts/$DOMAIN/conf/vhost.conf
</VirtualHost>

#{{SUBDOMAIN_TPL}}