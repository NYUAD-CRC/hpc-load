#! /bin/bash

# Cleaning old results
rm Dalma_Results.csv
#rm dalma_plot.html

# Defining all Dalma nodes that has running jobs
#echo "Running nodes are: "
sinfo -h -N | grep dn | grep 'alloc\|mix'| awk '{print $1}'| sort -u > Dalma_nodes.txt

# Replacing new line by , in nodes names
nodes=$(sed -z 's/\n/,/g;s/,$/\n/' Dalma_nodes.txt)

#echo "Checking the Runing commands: "
clush -w ${nodes} ps -axo user,%cpu,command | awk '$3>50 {print $4}'>> All_Dalma_Results

# Removal of aboslute path and change it to only application name
awk -F "/" '{print $NF }' All_Dalma_Results >> Cleaned_All_Dalma_Results

# Removal of [] from application name
sed -i 's/\[//g; s/\]//g' Cleaned_All_Dalma_Results

# Appending : at the end of each line (comparison purpose)
sed -i 's/$/,/' Cleaned_All_Dalma_Results

# Counting the total number of processes per Apllication
echo "Total number of processes per Apllication"
for i in $(cat Cleaned_All_Dalma_Results  | sort -u)
do
	count=$(grep -c $i Cleaned_All_Dalma_Results)
	echo $i $count >> Counting_Dalma_Results
done

# Putting the header of the output file
echo "Application,Processes" >Dalma_Results.csv
sort  -n -k 2 -r Counting_Dalma_Results >>Dalma_Results.csv

# Removing intermediate files
rm All_Dalma_Results
rm Cleaned_All_Dalma_Results
rm Counting_Dalma_Results
rm Dalma_nodes.txt
