#!/bin/bash
#
# Erzeugt ein SSL Zertifikat ohne den Benutzer zu fragen.
# 
# Folgende Variablen werden erwartet:
#
# $1 = Firmenname
# $2 = Domain
# $3 = EMail Adresse
# $4 = Ausgabename ohne Suffix, als absoluter Pfad (z.B. /etc/apache2/certs/default_cert)
#

if [ $UID -ne 0 ]; then
	echo "Run as root. Abort."
	echo
	exit 1
fi

if [ "$4" == "" ]; then
	echo
	echo "Need parameters. Abort."
	echo
	echo "$0 <Firmenname> <Domain> <EMail Adresse> <Ausgabename ohne Suffix, als absoluter Pfad (z.B. /etc/apache2/ssl/default_cert)>"
	echo
	exit 1
fi

COUNTRY="DE"
STATE="Germany"
CITY="Berlin"
ORG="$1"
UNIT="Administration"
HOST="$2"
EMAIL="$3"

# Key erzeugen
#openssl genrsa 2048 > "$4".key
# Sicherer
openssl genrsa -out "$4".key 1024

# Zertifikat erzeugen
umask 77 ; echo "$COUNTRY
$STATE
$CITY
$ORG
$UNIT
$HOST
$EMAIL" | openssl req -new -key "$4".key -x509 -days 365 -out "$4".crt &>/dev/null

# Details des gerade erstellten Keys zeigen
#openssl rsa -noout -text -in "$5".key
openssl x509 -noout -text -in "$4".crt | head 
