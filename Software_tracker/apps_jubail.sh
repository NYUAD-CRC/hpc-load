#! /bin/bash

# Cleaning old results
rm Jubail_Results.csv

# Defining all Jubail nodes that has running jobs
echo "Running nodes are: "
sinfo -h -N | grep cn | grep 'alloc\|mix'| awk '{print $1}'| sort -u | tee Jubail_nodes.txt

# Replacing new line by , in nodes names
nodes=$(sed -z 's/\n/,/g;s/,$/\n/' Jubail_nodes.txt)

echo "Checking the Runing commands: "
clush -w ${nodes} ps -axo user,%cpu,command | awk '$3>50 {print $4}'>> All_Jubail_Results

# Removal of aboslute path and change it to only application name
awk -F "/" '{print $NF }' All_Jubail_Results >> Cleaned_All_Jubail_Results

# Removal of [] from application name
sed -i -e 's/\[//g; s/\]//g' Cleaned_All_Jubail_Results

# Appending : at the end of each line (comparison purpose)
sed -i -e 's/$/,/' Cleaned_All_Jubail_Results


# Counting the total number of processes per Apllication
echo "Total number of processes per Apllication"
for i in $(cat Cleaned_All_Jubail_Results  | sort -u)
do
	count=$(grep -c $i Cleaned_All_Jubail_Results)
	echo $i $count | tee -a Counting_Jubail_Results
done

# Putting the header of the output file
echo "Application,Processes" >Jubail_Results.csv
sort  -n -k 2 -r Counting_Jubail_Results >>Jubail_Results.csv

# Removing intermediate files
rm All_Jubail_Results
rm Cleaned_All_Jubail_Results
rm Counting_Jubail_Results.csv
rm Jubail_nodes.txt

