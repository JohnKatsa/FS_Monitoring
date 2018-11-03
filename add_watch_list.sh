#!/bin/bash

echo "key given: " $1

if [ -z $1 ]; then
  echo "No key given"
else
  auditctl -a always,exit -F arch=b64 -S open,read,write,close -k $1
fi
