"""Script to parse the goldenjson file and submit 1000 job for each lumi, wait an hour and then submit jobs again"""

import json
import subprocess
import time
my_golden_json=open('oldjson.txt','r')

my_dict=json.load(my_golden_json)

total_lumis_submitted=0
num_lumis_processed=0

run_list=my_dict.keys()
run_list.sort()
for run in run_list:
    if total_lumis_submitted>9000:sleep(3600)
    print "submitting jobs for run: ",run
    for lumirange in my_dict[run]:
        total_lumis_submitted+=lumirange[1]-lumirange[0]
        print lumirange
        print ""
        #first submit 500 jobs to 
        lumis_left_this_cycle=1000-num_lumis_processed
        num_lumis=lumirange[1]-lumirange[0]+1
        
        while num_lumis>=lumis_left_this_cycle:
            lumistart=lumirange[0]
            lumiend=lumirange[0]+lumis_left_this_cycle-1
            num_lumis_processed=1000
            lumirange[0]=lumiend+1
            if lumis_left_this_cycle>0:
                command="./generateByLumi_batch2.sh -run "+str(run)+" -lumistart "+str(lumistart) +" -lumiend "+ str(lumiend)+" -queue cmscaf1nd"
                print command
                print ""
                subprocess.call(command.split())
            print "waiting...."
            print "...."
            print "...."
            print "...."
            print "...."
            time.sleep(600)
            num_lumis_processed=0
            lumis_left_this_cycle=1000-num_lumis_processed
            num_lumis=lumirange[1]-lumirange[0]+1
        lumistart=lumirange[0]
        lumiend=lumirange[1]
        num_lumis_processed+=lumirange[1]-lumirange[0]+1
        command="./generateByLumi_batch2.sh -run "+str(run)+" -lumistart "+str(lumistart) +" -lumiend "+ str(lumiend)+" -queue cmscaf1nd"
        print command
        print ""
        subprocess.call(command.split())
        


