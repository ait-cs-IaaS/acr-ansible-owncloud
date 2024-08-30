#!/bin/bash

echo "Loading configs/$1"
source configs/$1

echo "Executing nmap port discovery scan ..."

nmap -v -p- $TARGET

echo "done."

attack_wait 5s

echo "Executing service discovery on open ports ..."

nmap -v -sV -p $OPEN_PORTS $TARGET

echo "done."

attack_wait 5s

echo "Executing vhosts scan ..."

nmap -v --script http-vhosts --script-args "http-vhosts.domain=$TARGET_DOMAIN,http-vhosts.filelist=util/vhosts.lst" -p 80,443 $TARGET

attack_wait 10s

echo "done."

attack_wait 5s

echo "Verifying vhosts ..."

for check in $CHECK_VHOSTS; do

echo "Checking $check ..."
curl -I --header "Host: $check"  https://$TARGET -k
done

echo "Finished scans!"





