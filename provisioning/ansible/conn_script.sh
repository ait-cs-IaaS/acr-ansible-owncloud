#!/bin/bash


get_floating_ip(){
  # NEW: just take an IP from the internet, that doesn't start with 240. (same for OVH and our RANGE)
  local ip=$(grep $1 ~/infra | grep -Eo 'internet=[0-9a-fA-F:., ]+' | grep -Eo '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | awk '!/^240\./ { print; exit }')
  #local ip=$(grep $1 ~/infra | grep -Eo '10\.17\.[0-9]+\.[0-9]+' | head -n 1) #ON OUR RANGE: just take the IP starting with 10.17. -- OLD
  #if [ -z "$ip" ]; then # ON OVH: search for the Extn-Net and just take the IPv4. --- OLD
  #   ip=$(grep $1 ~/infra | grep -Eo 'Ext-Net=[0-9a-fA-F:., ]+' | grep -Eo '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | head -n 1) # OVH
  #fi
  echo $ip
}

get_any_ip(){
  local ip="$(grep -w $1 ~/infra | grep -Eo '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | head -n 1)" # any IP can be used to connect to machine
  echo $ip
}

flag_j=""
hostname=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    -j)
      if [ -n "$2" ]; then
        flag_j="$2"
        shift 2
      else
        echo "Flag -j requires a value."
        exit
      fi
      ;;
    -h)
      echo "Usage: conn [-j VALUE] VM_NAME"
      echo "-j VALUE   Defines the ID of the jumphost that should be used to reach the instance."
      echo "-h         Display this help message."
      echo "-infra	   Creates (or overwrites) the file ~/infra that must exist in order to allow \"conn\" to work properly"
      exit 0
      ;;
    -infra)
      #$(openstack server list | awk -F'|' '{ printf("%.30s \t %.250s\n", $3 ,$5);}' > ~/infra)
      $(openstack server list | awk -F'|' '{ print $3, $5; }' > ~/infra)
      exit 0
      ;;
    *)
      if [ -z "$hostname" ]; then
        hostname="$1"
        shift
      else
        echo "Invalid argument: $1"
        exit 1
      fi
      ;;
  esac
done

#If no hostname is set --> exit script
if [ -z "$hostname" ]; then
  echo "Missing VM_NAME. Use -h for help."
  exit 1
fi

#if flag -j for jumphost is set:
if [ -n "$flag_j" ]; then
  # get jumphost
  jumphost_ip=$(get_floating_ip "mgmthost_$flag_j")
  if [ -z "$jumphost_ip" ]; then # if no IP was found
    echo "no jumphost was found with hostname: mgmthost_$flag_j"
    exit 1
  fi
  # get machine
  machine_ip=$(get_any_ip "$hostname")
  if [ -z "$machine_ip" ]; then # if no IP was found
    echo "no host was found with hostname: $hostname"
    exit 1
  fi
  # connect
  ssh -o StrictHostKeyChecking=no -J ait@$jumphost_ip ait@$machine_ip
else # if flag -j is not set
  # get machine
  machine_ip=$(get_floating_ip "$hostname")
  if [ -z "$machine_ip" ]; then # if no IP was found
    echo "no host was found with hostname: $hostname"
    exit 1
  fi
  # connect
  ssh -o StrictHostKeyChecking=no ait@$machine_ip
fi
