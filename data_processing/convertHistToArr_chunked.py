import numpy as np
import ROOT
import h5py

from root_numpy import hist2array

# Function to get ROOT histograms and convert to NumPy arrays
def convert_histos(root_files, hist):

    global input_dir
    
    # Set histogram directory prefix based on ECAL subdetector
    if hist.startswith("EB"):
        hist_name = 'EcalBarrel/Run summary/%s'%hist
    else:
        hist_name = 'EcalEndcap/Run summary/%s'%hist

    # Get list of associated ROOT histograms (ROOT::TH2F or ROOT::TProfile2D)
    hists = [root_file.Get('DQMData/Run %d/%s'%(run,hist_name)) for root_file in root_files] 

    # Convert ROOT histograms to NumPy arrays and stack
    X = np.stack([hist2array(hist).T for hist in hists])

    return X

# Function to clean histogram name
def clean_name(hist_name):

    return hist_name.replace('/','_').replace(' ','_')

#########################################################
# Given a run and lumisection-divided data,
# convert a list of ROOT histograms therein to numpy arrays
# and save as hdf5 file

# Specify run and lumisections to process
run = 276525
#lumis = np.arange(806,838+1)
#lumis = np.arange(100,1199+1)
#lumis = lumis[lumis != 470]
startLS, stopLS, chunkLS = 100, 109, 2

# Specify list of histograms to convert
hist_list = [
        'EBOccupancyTask/EBOT rec hit occupancy',
        'EBTimingTask/EBTMT timing map',
        'EEOccupancyTask/EEOT rec hit occupancy EE -',
        'EETimingTask/EETMT timing map EE -',
        'EEOccupancyTask/EEOT rec hit occupancy EE +',
        'EETimingTask/EETMT timing map EE +',
        ] 

# Specify list of input ROOT files (ROOT::TFile) to process
#input_dir='/eos/cms/store/user/tmudholk/NitroDQM'
input_dir='.'

# Loop over files in chunks:
# ROOT doesnt support loading arbitrarily large numbers of TFiles
# (TChain only for TTrees, not histos)
for it, ls in enumerate(range(startLS,stopLS,chunkLS)):

    start, stop = ls, ls+chunkLS
    if stop > stopLS:
        stop = stopLS
    lumis = np.arange(start,stop)
    lumis = lumis[lumis != 470] # Tanmay: LS470 is missing
    print "Doing LS: [",lumis[0],",", lumis[-1],"]"
    root_files = [ROOT.TFile('%s/DQM_V0001_R000%d__All__Run2016__CentralDAQ_LS%d.root'%(input_dir,run,lumi)) for lumi in lumis]

    # Load converted histograms into a dict
    # Initialize dict on first iteration
    if it == 0:
        X = {clean_name(hist):convert_histos(root_files, hist) for hist in hist_list} 
    # For succeeding iterations, append to original dict
    else:
        for hist in hist_list:
            X[clean_name(hist)] = np.concatenate((X[clean_name(hist)], convert_histos(root_files, hist)))
    print " >> Appending length:",len(convert_histos(root_files, 'EBTimingTask/EBTMT timing map'))

print " >> Total length:",len(X[clean_name('EBTimingTask/EBTMT timing map')])
# Write converted histograms to HDF5
h = h5py.File('ECAL_rechit_occ+time.hdf5','w')
[h.create_dataset(name, data=data, compression='lzf') for (name, data) in X.iteritems()] # for Python2.x
#[h.create_dataset(name, data=data, compression='lzf') for (name, data) in X.items()] # for Python3.x
