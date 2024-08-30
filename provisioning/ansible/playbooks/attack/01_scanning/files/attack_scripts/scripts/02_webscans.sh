#!/bin/bash

echo "Loading configs/$1"
source configs/$1

echo "Executing wpscan wordpress discovery ..."

wpscan --disable-tls-checks --detection-mode aggressive --rua -e p,u1-500 --url http://$TARGET_WORDPRESS_DOMAIN

echo "done."

attack_wait 10s

echo "Initiating background nikto scans on public cloud and wordpress ..."

nikto -C all -vhost $TARGET_WORDPRESS_DOMAIN -port 443 -ssl -host $TARGET > /dev/null 2> /dev/null &
nikto -C all -vhost $TARGET_CLOUD_DOMAIN -port 443 -ssl -host $TARGET > /dev/null 2> /dev/null &
nikto -C all -vhost $TARGET_APP_DOMAIN -port 443 -ssl -host $TARGET > /dev/null 2> /dev/null &

echo "Finished with scan phase."










