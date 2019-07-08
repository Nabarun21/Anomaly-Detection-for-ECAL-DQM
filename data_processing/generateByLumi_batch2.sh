#!/bin/bash                                                                                                                                                                                                                              

args=`getopt rdlp: -- "$@"`
if test $? != 0
     then
         echo $usage
         exit 1
fi

eval set -- "$args"


for i
 do
    case "$i" in
      -run) shift; run=$2;shift;;
      -lumistart) shift; lumistart=$2;shift;;
      -lumiend) shift;lumiend=$2;shift;;
      -queue) shift;queue=$2;shift;;
    esac
done


listDatasets() {
    if [ -z "$1" ]; then
	echo "Please enter run number" && return
    fi
    ./dasgoclient_linux -query "dataset run=$1" | grep -iI "SingleElectron"|grep -iI "RAW" |grep -v "RECO" | grep -vi "test"
}

updateFileList() {
    if [ -z "$1" ]; then
	echo "Please enter name of output file" && return
    else
        echo "Name of output file: $1"
    fi
    if [ -z "$2" ]; then
	echo "Please enter run number" && return
    else
        echo "Fetching file list for run number = $2"
    fi
    if [ -z "$3" ]; then
	echo "Please enter dataset" && return
    else
        echo "Updating file list for dataset $3"
    fi
    LUMI_ADDITION=""
    if [ -n "$4" ]; then
        echo "Limiting search to lumi=$4"
        LUMI_ADDITION=" lumi=$4"
    else
        echo "Including files for all lumisections"
    fi
    ./dasgoclient_linux -query "file dataset=$3 run=${2}${LUMI_ADDITION}" > ./${1}
}

shopt -s expand_aliases
#source ~/.bashrc


echo Processing run: ${run}
echo Processing from lumi ${lumistart} to lumi ${lumiend}

echo Dataset name is $Dataset
cd /afs/crc.nd.edu/user/n/ndev/DQM_ML/CMSSW_9_2_11/src/DAQ 

eval `scramv1 runtime -sh`


mkdir run$run
mkdir run$run/results
mkdir run$run/$run
myusername=$USER

retval=`voms-proxy-info &> /dev/null  ; echo $?`
    #echo "retval " $retval $ppid                                                                                                                                                                                                         
if [ $retval -ne 0 ]; then
    voms-proxy-init --voms cms
fi
cp `find /tmp/x509up_u* -user ${myusername}` run${run}/
listDatasets $run

dataset=`listDatasets $run`

echo ${dataset}


for lumiNumber in `seq ${lumistart} ${lumiend}`; do
    echo "Starting processing for lumi number ${lumiNumber}..."
    updateFileList run${run}/inputFileList_LS${lumiNumber}.txt ${run} ${dataset} ${lumiNumber}
    echo ""
    echo "File list updated. Modifying hardcoded parameters..."
    echo ""
    ./modifyHardcodedConfigParameters.py --runNumber=${run} --lumisToProcess=${lumiNumber} --workflow=/All/Run2016/CentralDAQ_LS${lumiNumber} --prescaleFactor=10 --outputcfg=run${run}/ecal_dqm_sourceclient-offline_LS${lumiNumber}_cfg.py --inputPath=inputFileList_LS${lumiNumber}.txt

    echo ""
    echo ""
    echo ""

    cd run${run}

    cp ../batch_job_template.sh batch_job_${lumiNumber}.sh
    batchdir="$(pwd)"
    sed -e "s,%cmsswdir%,$batchdir,"        \
        -e "s,%luminum%,$lumiNumber,"        \
        -e "s,%luminum%,$lumiNumber,"        \
        -e "s,%run%,${run}," \
        -e "s,%datasetPath%,${datasetpath}," \
        -e "s,%username%,${myusername}," \
        -i batch_job_${lumiNumber}.sh
#    rm DQM_V0001_R000${run}__All__Run2016__CentralDAQ_LS${lumiNumber}.root && rm ecal_dqm_sourceclient-offline_LS${lumiNumber}_cfg.py && rm inputFileList_LS${lumiNumber}.txt                                                           
    chmod a+x batch_job_${lumiNumber}.sh
    condor_qsub -q ${queue} batch_job_${lumiNumber}.sh
    echo ""
    echo ""
    echo ""
    cd -
done


