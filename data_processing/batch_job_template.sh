#!/bin/bash                                                                                                                                                                                                                               

ps | grep `echo $$` | awk '{ print $4 }'

export mypwd=`pwd`




cd %cmsswdir%

#export SCRAM_ARCH slc5_amd64_gcc434                                                                                                                                                                                                      
#source /afs/cern.ch/cms/LCG/LCG-2/UI/cms_ui_env.sh                                                                                                                                                                                       

eval `scram runtime -sh`
if [ $X509_USER_PROXY!="" ]; then
    export X509_USER_PROXY=`find %cmsswdir%/x509up_u*`
fi
echo
cd -
#cd \${lxbatchpwd}                                                                                                                                                                                                                        

echo "Starting CMSSW"
cp %cmsswdir%/ecal_dqm_sourceclient-offline_LS%luminum%_cfg.py .
cp %cmsswdir%/inputFileList_LS%luminum%.txt .
cmsRun ecal_dqm_sourceclient-offline_LS%luminum%_cfg.py  >& run%luminum%.txt

mv run%luminum%.txt %cmsswdir%/results/

#mv DQM_V0001_R000%run%__All__Run2016__CentralDAQ_LS%luminum%.root %cmsswdir%/results/
runnum=%run%
mv DQM_V0001_R000%run%__All__Run2016__CentralDAQ_LS%luminum%.root %cmsswdir%/${runnum}/

#cmsStage -f ECALTPGtree.root /store/caf/user/%username%/TPG/%runNb%/ECALTPGtree_%njob%.root                                                                                                                                              


echo "LAST PWD" 'pwd'