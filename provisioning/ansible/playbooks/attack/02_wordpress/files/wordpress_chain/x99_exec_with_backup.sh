#!/bin/bash

echo "Loading configs/$1"
source configs/$1

python3 util/shell.py exec $TARGET_BACKUP_WEBSHELL "${@:2}"



