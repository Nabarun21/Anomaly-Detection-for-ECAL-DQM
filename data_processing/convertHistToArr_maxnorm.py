import numpy as np
import ROOT
import h5py
import os
from root_numpy import hist2array


# Function to get ROOT histograms and convert to NumPy arrays
def convert_histos(root_files, hist):

    global input_dir
    
    # Set histogram directory prefix based on ECAL subdetector
    if hist.startswith("EB"):
        hist_name = 'EcalBarrel/Run summary/%s'%hist
    else:
        hist_name = 'EcalEndcap/Run summary/%s'%hist


    hists=[]
    for root_file in root_files:
        histo=root_file.Get('DQMData/Run %d/%s'%(run,hist_name))                # Get list of associated ROOT histograms (ROOT::TH2F or ROOT::TProfile2D)
        try:
            histo.Scale(1/histo.GetBinContent(histo.GetMaximumBin()))                                         #Normalize Histograms by its max
            hists.append(histo)
        except ZeroDivisionError:
            print "Empty histogram: ",hist," in file: ",root_file
        except AttributeError:
            print "Empty root filr: ",root_file
    X = np.stack([hist2array(hist).T for hist in hists])                     # Convert ROOT histograms to NumPy arrays and stack


    return X

# Function to clean histogram name
def clean_name(hist_name):

    return hist_name.replace('/','_').replace(' ','_')






##################################################################
# Given a run and lumisection-divided data as separate root files,
# convert a list of ROOT histograms therein to numpy arrays
# and save as hdf5 file

# Specify list of histograms to convert
hist_list = [
        'EBOccupancyTask/EBOT rec hit occupancy',
        'EBTimingTask/EBTMT timing map',
        'EEOccupancyTask/EEOT rec hit occupancy EE -',
        'EETimingTask/EETMT timing map EE -',
        'EEOccupancyTask/EEOT rec hit occupancy EE +',
        'EETimingTask/EETMT timing map EE +',
        ] 

# Specify run(s)
run_list=[273158,273450,274251,275059,275338,276092,276355,276454,276525,276544,276584,276655,276807,280016,283052,283478,273425,273730,274316,275066,275344,276097,276361,276458,276527,276545,276585,276659,276808,283042,283059,283865,273447,274198,274388,275311,275345,276315,276363,276495,276528,276581,276586,276775,276810,283043,283270,283876,273448,274199,274998,275319,275370,276317,276384,276501,276542,276582,276587,276776,276811,283049,283416,283877,273449,274200,275001,275337,275376,276318,276437,276502,276543,276583,276653,276794,280015,283050,283453]

for run in run_list:
    print "Converting files from ROOT to hdf5 for run: ",run
    run_dir ="/hadoop/users/ndev/DQM_ML/bad_2016/"+str(run)
    X={}
    files_in_chunk=min(100,len(os.listdir(run_dir)))        # ROOT doesnt support loading arbitrarily large numbers of TFiles, Loop over files in chunks:)

    root_file_list=[]
    num_iters=0
    for filename in os.listdir(run_dir):

        root_file_list.append(ROOT.TFile(run_dir+"/"+filename))

        # Load converted histograms into a dict
        if len(root_file_list)%files_in_chunk!=0 and (num_iters*100+len(root_file_list))!=len(os.listdir(run_dir)):              
            continue
        else:
            if len(X)==0:
                print 'creating'                                                                         # Initialize dict on first iteration
                X = {clean_name(hist):convert_histos(root_file_list, hist) for hist in hist_list} 
                num_iters+=1
            else:                                                                                        # For succeeding iterations, append to original dict
                print 'not creating but adding'
                for hist in hist_list:
                    X[clean_name(hist)] = np.concatenate((X[clean_name(hist)], convert_histos(root_file_list, hist)))
                num_iters+=1
            root_file_list=[]


    print " >> Total length:",len(X[clean_name('EBTimingTask/EBTMT timing map')])


    # Write converted histograms to HDF5
    h = h5py.File('hdf_files_maxnorm/bad_2016/ECAL_rechit_occ_time_'+str(run)+'.hdf5','w')
    [h.create_dataset(name, data=data, compression='lzf') for (name, data) in X.iteritems()] # for Python2.x
#[h.create_dataset(name, data=data, compression='lzf') for (name, data) in X.items()] # for Python3.x
