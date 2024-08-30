#!/bin/bash
. config

echo "${red}Port scan is running...${reset}"
nmap $SUBNET_IP/$RANGE
nmap -p- $SUBNET_IP,1,2,30,60,178,201
nmap -iL ${PWN_PATH}/ip-targets.txt -A -sV -p 53
nmap -iL ${PWN_PATH}/ip-targets.txt -A -sV -p 22,7000
nmap -iL ${PWN_PATH}/ip-targets.txt -A -sV -p 22
nmap -iL ${PWN_PATH}/ip-targets.txt -A -sV -p 80,8009,8080 -oX ${PWN_PATH}/nmap-results.xml
sleep 60
echo "${red}Content discovery is running...${reset}"

cat ${PWN_PATH}/web-targets.txt | xargs -P4 -I{} -n1 wfuzz --hc 404,403 -c -z file,$WFZ_WORDLIST -u {}:$CONTENT_DIR_PORT/FUZZ
