#! /bin/bash

rm Application.csv
rm Apps.csv

cat Dalma_Results.csv | cut -d "," -f 1 |tail -n+2 >Application.csv
cat Jubail_Results.csv | cut -d "," -f 1 |tail -n+2 >>Application.csv
sort -u Application.csv > Apps.csv

file=$(cat Apps.csv)

for line in $file
do
	echo -e "$line"
	     if grep -Fxq "$line"
    then
            count=$(grep $line Dalma_Results.csv | cut -d ":" -f 2)
    else
    count=0
    fi
    echo "Count for $line is $count"
done
#     if grep -Fxq "$line" 
 #   then
#	    count=$(grep $line Dalma_Results.csv | cut -d ":" -f 2)
 #   else
  #  count=0
   # fi
#echo "Count for $line is $count"
