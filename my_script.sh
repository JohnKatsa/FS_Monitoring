#!/bin/bash

echo "key given: " $1

if [ -z $1 ]; then
  echo "No key given"
else
  ausearch -k $1 >> myfile
  #ausearch -k $1 | aureport -f -i >> myfile
fi

#make the manipulation program
gcc manipulate_audit.c

#run it with the file
./a.out myfile myfileout
rm myfile
