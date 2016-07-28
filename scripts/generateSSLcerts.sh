#!/bin/bash

if [ $UID -ne 0 ]; then
	echo "Run as root. Abort."
	echo
	exit 1
fi

if [ "$4" == "" ]; then
	echo
	echo "Need parameters. Abort."
	echo
	echo "$0 <company> <domain> <email> <path to cert base name without suffix, an absolute path (i.e.. /etc/apache2/ssl/default_cert)>"
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

openssl genrsa -out "$4".key 2048
if [ $? -ne 0 ]; then
 exit 1
fi

umask 77 ; echo "$COUNTRY
$STATE
$CITY
$ORG
$UNIT
$HOST
$EMAIL" | openssl req -new -key "$4".key -x509 -days 365 -out "$4".crt &>/dev/null
if [ $? -ne 0 ]; then
 exit 1
fi
openssl x509 -noout -text -in "$4".crt | head
if [ $? -ne 0 ]; then
 exit 1
fi