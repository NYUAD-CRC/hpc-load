#! /bin/bash

rm Application.csv
rm Apps.csv
rm Applications_dalma
rm Applications_jubail

cat Dalma_Results.csv | cut -d "," -f 1 |tail -n+2 >Application.csv
cat Jubail_Results.csv | cut -d "," -f 1 |tail -n+2 >>Application.csv
sort -u Application.csv > Apps.csv

file=$(cat Apps.csv)

for line in $file
do	
#echo -e "$line"
if grep "$line" Dalma_Results.csv
    then
            count=$(grep $line Dalma_Results.csv | cut -d "," -f 2)
    else
            count="0"
    fi
    echo "$count" >>Applications_dalma
    if grep "$line" Jubail_Results.csv
    then
            count=$(grep $line Jubail_Results.csv | cut -d "," -f 2)
    else
            count="0"
    fi
    echo "$count" >>Applications_jubail

done

# Removal of spaces in files
cat Applications_dalma | tr -d " \t\r" >dalma_apps_final
cat Applications_jubail | tr -d " \t\r" >jubail_apps_final 
 
