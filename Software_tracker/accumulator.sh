#! /bin/bash

rm Application.csv
rm Apps.csv

cat Dalma_Results.csv | cut -d "," -f 1 |tail -n+2 >Application.csv
cat Jubail_Results.csv | cut -d "," -f 1 |tail -n+2 >>Application.csv
sort -u Application.csv > Apps.csv

file="Dalma_Results.csv"

while read -r line; do
    echo -e "$line"
done <$file
