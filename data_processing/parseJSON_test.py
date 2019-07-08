"""Script to parse the goldenjson file and submit 1000 job for each lumi, wait an hour and then submit jobs again"""

import json
import subprocess
import time
my_golden_json=open('2017goldenjson.txt','r')

my_dict=json.load(my_golden_json)

total_lumis_submitted=0
num_lumis_processed=0

run_list=my_dict.keys()
run_list.sort()
for run in run_list:
    print run
#    if int(run)<279767:continue
    if total_lumis_submitted>9000:break
    print "submitting jobs for run: ",run
    for lumirange in my_dict[run]:
        lumistart=lumirange[0]
        lumiend=min(lumirange[0]+1,lumirange[-1])
        total_lumis_submitted+=2
        command="./generateByLumi_batch2.sh -run "+str(run)+" -lumistart "+str(lumistart) +" -lumiend "+ str(lumiend)+" -queue cmscaf1nd"
        print command
        print ""
        subprocess.call(command.split())
        


