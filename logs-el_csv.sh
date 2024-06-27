#!/bin/bash

# Uloží výstup do souboru 'vysledky_el.csv'
{
    echo 'AIQ,HCI,SD,refm,refmN,Nn,EL,Alg,q,lambda,alpha,epsilon,gamma'
find log-el -type f | while read soubor; do 
  python ./ComputeFromLog.py "$soubor" | tail -n +4  | 
  sed 's/ +\/\- /,/' | 
  sed 's/ SD /,/' | 
  sed 's/ :/, /'|
  sed 's/ \ log\//, /' | \
  sed 's/_/ /' | 
  sed 's/_/, /' | 
  sed 's/_/, /' | \
  tr '(' ',' | 
  tr ')' ',' | 
  sed 's/,_.*//' | 
  cut -c9-
done
} > vysledky_el.csv
