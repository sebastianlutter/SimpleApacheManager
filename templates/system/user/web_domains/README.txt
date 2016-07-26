# Das phoenixToolkit ermöglicht es euch eure Webseiten Domains zu verwalten.
# Ihr habt über sudo Zugriff auf das Skript wenn eurer User in der Gruppe phoenix_toolkit ist.
#
#
# Leer ausgeführt zeigt es die möglichen Optionen an:
#
$ sudo phoenixToolkit
Modified vhost folder: /home/tester/web_domains
Running script with user tester with sudo permissions.

Benutzung des Phoenix Server Toolkits

        phoenix  SERVICE JOBTYPE [ARGS...]

Examples:
        phoenix  domain add domain.de   Erstellt eine neue Domain für den Apache Webserver.
        phoenix  domain del domain.de   Entfernt eine Domain und alle ihre Subdomains.
        phoenix  domain addsub domain.de  subdomain     Erstellt eine neue Subdomain für eine existierende Domain.
        phoenix  domain delsub domain.de  subdomain     Löschen einer Subdomain für eine existierende Domain.
        phoenix  domain addalias domain.de  alias       Erstellt eine neues Alias für eine existierende Domain.
        phoenix  domain delalias domain.de  alias       Löschen eines Alias für eine existierende Domain.
        phoenix  domain list                     Zeigt eine Liste mit allen vorhandenen vhosts.
#
# Wird eine neue Domain angelegt so wird diese im eigenen Homeverzeichniss
# unter web_domains/ angelegt.
#
# Ein neuer VHost hat folgende Ordner:

