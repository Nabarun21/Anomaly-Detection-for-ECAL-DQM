#!/bin/bash
##$ -pe smp 24             # 24 cores and 4 GPUs per machine 
                         # so ask for 4 cores  to get one GPU
#$ -M ndev@nd.edu
#$ -m abe

#$ -q gpu                # Specify queue
#$ -l hostname="qa-1080ti-001"         # This job is just going to use one GPU card
#$ -N choose_loss               # Specify job name
#$ -o sgeLogs            # Where to put the output

# Since UGE doesn't have the nice submit file format from HTCondor, we have to define our possible jobs here

echo Starting...
echo `pwd`


echo Initializing environment

if [ -r /opt/crc/Modules/current/init/bash ];then
	source /opt/crc/Modules/current/init/bash 
fi


module load tensorflow
module load cudnn

echo '==================================='
pwd
echo '==================================='
#ls -alh
echo '==================================='
#printenv
echo '==================================='
#uname -a
echo '==================================='
#cat /proc/cpuinfo
echo '==================================='
#echo Will run $cmd
echo '==================================='

# Make a working directory
#wd=workingdir_${JOB_NAME}_${QUEUE}_${JOB_ID}
#mkdir -p results/$wd
#pushd results/$wd
#echo $cmd
cd /afs/crc.nd.edu/user/n/ndev/DQM_ML/Anomaly-Detection-for-ECAL-DQM/
echo `pwd`
source set_env.sh

python /afs/crc.nd.edu/user/n/ndev/DQM_ML/Anomaly-Detection-for-ECAL-DQM/scripts/autoencoder_v01.py --opt_name adam --model_name autoencoder_v01>&train_01.log
python /afs/crc.nd.edu/user/n/ndev/DQM_ML/Anomaly-Detection-for-ECAL-DQM/scripts/autoencoder_v02.py --opt_name adam --model_name autoencoder_v02>&train_02.log
python /afs/crc.nd.edu/user/n/ndev/DQM_ML/Anomaly-Detection-for-ECAL-DQM/scripts/autoencoder_v03.py --opt_name adam --model_name autoencoder_v03>&train_03.log


cd -
echo '==================================='
#ls -alh
echo '==================================='

# Move the log file into the appropriate results directory, in case something fails later.
#set model = *.tgz   #There should only be one of these!



echo Done!
