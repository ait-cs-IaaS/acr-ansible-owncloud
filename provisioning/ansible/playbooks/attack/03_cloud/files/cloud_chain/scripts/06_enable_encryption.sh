#!/bin/bash

echo "This script only has to be run once ..."

dnsteal_pid=$(pgrep -f dnsteal.py)

echo "Activating kill switch ..."
kill -SIGHUP $dnsteal_pid

echo "done."
