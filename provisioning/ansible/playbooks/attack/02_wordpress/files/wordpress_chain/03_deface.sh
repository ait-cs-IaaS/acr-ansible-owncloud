#!/bin/bash

echo "Loading configs/$1"
source configs/$1

echo "Upload defaced index ..."
python3 util/shell.py upload $TARGET_WEBSHELL $DEFACEMENT_INDEX $DEFACEMENT_INDEX_NAME

echo "done."

