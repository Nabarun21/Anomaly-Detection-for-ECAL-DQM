#creating anomalous sets

import h5py
import numpy as np
import helpers as helpers

def clean_name(hist_name):
    return hist_name.replace('/','_').replace(' ','_')

run_list=[273158,273450,274251,275059,275338,276092,276355,276454,276525,276544,276584,276655,276807,280016,283052,283478,273425,273730,274316,275066,275344,276097,276361,276458,276527,276545,276585,276659,276808,283042,283059,283865,273447,274198,274388,275311,275345,276315,276363,276495,276528,276581,276586,276775,276810,283043,283270,283876,273448,274199,274998,275319,275370,276317,276384,276501,276542,276582,276587,276776,276811,283049,283416,283877,273449,274200,275001,275337,275376,276318,276437,276502,276543,276583,276653,276794,280015,283050,283453]


hist_list=['EBOccupancyTask/EBOT rec hit occupancy']#,'EBTimingTask/EBTMT timing map','EEOccupancyTask/EEOT rec hit occupancy EE -',
#'EETimingTask/EETMT timing map EE -','EEOccupancyTask/EEOT rec hit occupancy EE +','EETimingTask/EETMT timing map EE +']


#create bad data with hot towers
for run in run_list:
    X={}
    for hist_name in hist_list:
        data_sample=helpers.get_data("ECAL_rechit_occ_time_"+str(run)+".hdf5",data_type='good_2016',group=clean_name(hist_name))
    
        for lumisec in range(len(data_sample)):
            if lumisec%10!=0:continue
            input_image=data_sample[lumisec,:]

            out_sample=helpers.insert_hot_tower(input_image)
#            print(np.max(out_sample))
            
            out_sample=np.reshape(out_sample,(1,out_sample.shape[0],out_sample.shape[1]))
        
            if clean_name(hist_name) not in X.keys():
                X[clean_name(hist_name)]=out_sample
            else:       
            #print ('not creating but adding')
                X[clean_name(hist_name)] = np.concatenate((X[clean_name(hist_name)],out_sample))
        
    h = h5py.File('../data_nopreprocess/bad_2016/hot_towers/ECAL_rechit_occ_time_'+str(run)+'.hdf5','w')
    [h.create_dataset(name, data=data, compression='lzf') for (name, data) in X.iteritems()] # for Python2.x                                                  
#    [h.create_dataset(name, data=data, compression='lzf') for (name, data) in X.items()] # for Python3.x         
    

#create bad data with missing modules
for run in run_list:
    X={}
    for hist_name in hist_list:
        data_sample=helpers.get_data("ECAL_rechit_occ_time_"+str(run)+".hdf5",data_type='good_2016',group=clean_name(hist_name))
    
        for lumisec in range(len(data_sample)):
            if lumisec%25!=0:continue
            input_image=data_sample[lumisec,:]
            out_sample=helpers.make_module_off(input_image)
            
            out_sample=np.reshape(out_sample,(1,out_sample.shape[0],out_sample.shape[1]))
        
            if clean_name(hist_name) not in X.keys():
                X[clean_name(hist_name)]=out_sample
            else:       
            #print ('not creating but adding')
                X[clean_name(hist_name)] = np.concatenate((X[clean_name(hist_name)],out_sample))
        
    h = h5py.File('../data_nopreprocess/bad_2016/missing_modules/ECAL_rechit_occ_time_'+str(run)+'.hdf5','w')
    [h.create_dataset(name, data=data, compression='lzf') for (name, data) in X.iteritems()] # for Python2.x                                                  
#    [h.create_dataset(name, data=data, compression='lzf') for (name, data) in X.items()] # for Python3.x         


