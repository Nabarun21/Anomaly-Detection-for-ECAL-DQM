import h5py
import os
import numpy as np
import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s',filename='../logs/datacount.txt')
logger = logging.getLogger(__name__)

total_count=0
data_folder=os.environ['DATA']
data_files=os.listdir(data_folder)
print len(data_files)

for filename in data_files:
    input_file=h5py.File(data_folder+"/"+filename,'r')
    data=np.array((input_file['EBOccupancyTask_EBOT_rec_hit_occupancy']))
    total_count+=data.shape[0]
    logging.info("%s : %s : %s ",filename,str(data.shape[0]),str(total_count))

train_data=data_files[0:63]  #you ask why 63?? this keeps ~80% of data for train/val
test_data=data_files[63:]    #and 20% for testing, see logs/datacount.txt. this number should be automated later

print(train_data[0],train_data[-1])
print(test_data[0],test_data[-1])
print(len(train_data)+len(test_data))
