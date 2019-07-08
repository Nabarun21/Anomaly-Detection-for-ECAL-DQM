cd /afs/cern.ch/work/n/ndev/DQM_ML/CMSSW_9_2_11/src && cmsenv

for lumiNumber in `seq $1 $2`; do
    echo "Starting processing for lumi number ${lumiNumber}..."
    echo "Updating file list..."
    updateFileList inputFileList_LS${lumiNumber}.txt 276525 /SingleElectron/Run2016D-v2/RAW ${lumiNumber}
    echo "File list updated. Modifying hardcoded parameters..."
    ./modifyHardcodedConfigParameters.py --runNumber=276525 --lumisToProcess=${lumiNumber} --workflow=/All/Run2016/CentralDAQ_LS${lumiNumber} --prescaleFactor=10 --outputcfg=ecal_dqm_sourceclient-offline_LS${lumiNumber}_cfg.py --inputPath=inputFileList_LS${lumiNumber}.txt
    echo "Hardcoded parameters modified. Starting CMSSW..."
    cmsRun ecal_dqm_sourceclient-offline_LS${lumiNumber}_cfg.py
    echo "CMSSW done. Copying file..."
    # eos mkdir -p /store/user/tmudholk/NitroDQM/run276525
    # eos cp DQM_V0001_R000276525__All__Run2016__CentralDAQ_LS${lumiNumber}.root /eos/cms/store/user/tmudholk/NitroDQM/run276525/DQM_V0001_R000276525__All__Run2016__CentralDAQ_LS${lumiNumber}.root
    # rsync --progress -av DQM_V0001_R000276525__All__Run2016__CentralDAQ_LS${lumiNumber}.root /afs/cern.ch/user/t/tmudholk/private/mount/eos_mount/cms/store/user/tmudholk/NitroDQM/run276525/
    rsync --progress -av DQM_V0001_R000276525__All__Run2016__CentralDAQ_LS${lumiNumber}.root /afs/cern.ch/work/n/ndev/DQM_ML/CMSSW_9_2_11/src
    echo "File copied. Removing root output, cfg file, and list of input files..."
#    rm DQM_V0001_R000276525__All__Run2016__CentralDAQ_LS${lumiNumber}.root && rm ecal_dqm_sourceclient-offline_LS${lumiNumber}_cfg.py && rm inputFileList_LS${lumiNumber}.txt
    echo "Lumi number ${lumiNumber} done!"
done
