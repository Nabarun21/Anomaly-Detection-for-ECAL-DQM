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
        #    histo.Scale(1/histo.GetBinContent(histo.GetMaximumBin()))                                         #Normalize Histograms by its area
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
run_list=[297050,297483,297504,297603,298996,299065,299185,300369,300389,300396,303838,304158,304354,304507,304662,304777,305062,305179,305188,305237,305312,305351,305405,305636,305842,306036,306051,297056,297484,297505,297666,298997,299067,299327,300370,300390,300397,303885,304169,304366,304562,304663,304778,305063,305180,305202,305247,305313,305358,305406,305766,305862,306037,306092,297434,297485,297557,297670,299000,299096,299329,300371,300391,300398,303948,304204,304446,304616,304737,304797,305064,305181,305204,305248,305314,305364,305440,305809,305898,306038,306095,297435,297486,297558,297674,299042,299149,300365,300372,300392,300399,303998,304209,304447,304625,304738,305044,305112,305182,305207,305252,305338,305365,305518,305814,305902,306041,306122,297467,297487,297562,297675,299061,299178,300366,300373,300393,300400,303999,304291,304451,304626,304739,305045,305113,305183,305208,305282,305341,305366,305586,305821,305967,306042,306126,297468,297488,297563,297722,299062,299180,300367,300374,300394,303825,304125,304292,304505,304655,304740,305046,305114,305184,305234,305310,305349,305376,305589,305832,306029,306048,297469,297503,297599,297723,299064,299184,300368,300375,300395,303832,304144,304333,304506,304661,304776,305059,305178,305186,305236,305311,305350,305377,305590,305840,306030,306049]

for run in run_list:
    print "Converting files from ROOT to hdf5 for run: ",run
    run_dir ="/hadoop/users/ndev/DQM_ML/good_2017/"+str(run)
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

    try:
        print " >> Total length:",len(X[clean_name('EBOccupancyTask/EBOT rec hit occupancy')])
    except:
        print "no files"

    # Write converted histograms to HDF5
    h = h5py.File('hdf_files_nopreprocess/good_2017/ECAL_rechit_occ_time_'+str(run)+'.hdf5','w')
    [h.create_dataset(name, data=data, compression='lzf') for (name, data) in X.iteritems()] # for Python2.x
#[h.create_dataset(name, data=data, compression='lzf') for (name, data) in X.items()] # for Python3.x
