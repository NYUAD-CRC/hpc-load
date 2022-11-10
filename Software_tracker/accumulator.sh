#! /bin/bash

rm Application.csv
rm Apps.csv

cat Dalma_Results.csv | cut -d "," -f 1 |tail -n+2 >Application.csv
cat Jubail_Results.csv | cut -d "," -f 1 |tail -n+2 >>Application.csv
sort -u Application.csv > Apps.csv

file="Apps.csv"

while read -r line; do
    echo -e "$line"
    if grep -Fxq "$line" 
    then
	    count=$(grep $line Dalma_Results.csv | cut -d ":" -f 2)
    else
    count=0
fi
echo "Count for $line is $count"
done <$file
