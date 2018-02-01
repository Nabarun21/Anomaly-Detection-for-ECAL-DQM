import numpy as np
import pickle
import os
import h5py
#from keras import callbacks
import random
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
#logging.basicConfig(level=logging_numeric_level, format='%(asctime)s %(levelname)s: %(message)s')

logger = logging.getLogger(__name__)

#helper fucntions
#helper fucntions
def get_data(file_name,group='EBOccupancyTask_EBOT_rec_hit_occupancy',data_type='good'):
   "picks samples out of a hdf file and return a numpy array"
   data_folder=os.environ["DATA"].replace("good",data_type)
   input_file=h5py.File(data_folder+"/"+file_name,'r')
   logging.debug("Loading data from file: "+file_name)
   ret_array=np.array((input_file[group]))
   logging.debug("Supplying "+str(ret_array.shape[0])+" samples")
   ret_array_2=np.empty([ret_array.shape[0],2])
   if 'bad' in file_name:
      ret_array_2[:,:]=[0,1]
   else:
      ret_array_2[:,:]=[1,0]
   return ret_array,ret_array_2

   
def get_num_samples(file_list,group='EBOccupancyTask_EBOT_rec_hit_occupancy'):
   "returns total number of samples in a list of hdf files"
   data_folder=os.environ["DATA"]
   total_count=0
   for filename in file_list:
      input_file=h5py.File(data_folder+"/"+filename,'r')
      data=np.array((input_file[group]))
      total_count+=data.shape[0]
   return total_count

"""
class train_histories(callbacks.Callback):
   def on_train_begin(self, logs={}):
      self.aucs = []
      self.epochwise_losses = []
      self.epochwise_val_losses = []
      self.batchwise_losses = []


   def on_train_end(self, logs={}):
      return

   def on_epoch_begin(self, epoch, logs={}):
      return

   def on_epoch_end(self, epoch, logs={}):
      self.epochwise_losses.append(logs.get('loss'))
      self.epochwise_val_losses.append(logs.get('val_loss'))
      return

   def on_batch_begin(self, batch, logs={}):
      return

   def on_batch_end(self, batch, logs={}):
      self.batchwise_losses.append(logs.get('loss'))
      return

"""

#generator
def batch_generator(batch_size,data_file_list,group='EBOccupancyTask_EBOT_rec_hit_occupancy',data_type='good'):
   """ generates batch_size images, well thats's obvious. throws exception when data runs out"""
   if batch_size<=0 or not isinstance(batch_size,int):
      logging.error("Batch size needs to be an integer greater than 0")
      raise StopIteration("Batch size needs to be an integer greater than !!")
   

   file_index=0
   leftover_array,leftover_array_2=get_data(data_file_list[file_index],group,data_type) #start off with the first data file
   image_height=leftover_array.shape[1]
   image_width=leftover_array.shape[2]

   num_batches_generated=0
   while True:
      new_batch=False
      while not new_batch:
         num_samples_in_batch=leftover_array.shape[0] #samples_left_over_from_last_iteration
         samples_needed_for_next_batch=batch_size-num_samples_in_batch    

         if samples_needed_for_next_batch<=0:
            logging.debug("Have enough samples in current/leftover batch for another, not loading new file")
            ret_array=leftover_array[0:batch_size]
            leftover_array=leftover_array[batch_size:]
            ret_array_2=leftover_array_2[0:batch_size]
            leftover_array_2=leftover_array_2[batch_size:]
            new_batch=True
         else:
            logging.debug("Current/leftover batch doesn't have enough samples, loading new file")
            file_index+=1
            try:
               new_array,new_array_2=get_data(data_file_list[file_index],group,data_type)
            except IndexError as exc:
               if num_batches_generated>0:
                  logging.info("Ran out of data, can't suppy more images to the model, "+str(exc)+". Supplied "+str(num_batches_generated)+" batches")
                  raise StopIteration("Ran out of data, can't suppy more images to the model, "+str(exc)+". Supplied "+str(num_batches_generated)+" batches")
               else:
                  logging.info("Increase your dataset size or reduce your batch size, i can't even make a single batch!!") 
                  raise StopIteration("Increase your dataset size or reduce your batch size, i can't even make a single batch!! ,"+str(exc)) 

            
            num_current_samples=new_array.shape[0]

            if num_current_samples<samples_needed_for_next_batch:
               logging.debug("Still Not enough samples for another batch, just expanding leftover array")
               leftover_array=np.concatenate([leftover_array,new_array])
               leftover_array_2=np.concatenate([leftover_array_2,new_array_2])

            elif num_current_samples>samples_needed_for_next_batch:
               logging.debug("Enough Samples for next batch, keeping the rest as leftover")
               array_to_add=new_array[0:samples_needed_for_next_batch]
               ret_array=np.concatenate([leftover_array,array_to_add])
               array_2_to_add=new_array_2[0:samples_needed_for_next_batch]
               ret_array_2=np.concatenate([leftover_array_2,array_2_to_add])
               new_batch=True
               del leftover_array
               leftover_array=new_array[samples_needed_for_next_batch:]
               del leftover_array_2
               leftover_array_2=new_array_2[samples_needed_for_next_batch:]

            else:
               logging.debug("Exactly the number of samples for a batch,lefotver batch has now zero samples")
               ret_array=np.concatenate([leftover_array,new_array])
               left_over_array=np.zeros(shape=[0,image_height,image_width])
               ret_array_2=np.concatenate([leftover_array_2,new_array_2])
               left_over_array_2=np.zeros(shape=[0,image_height,image_width])
               new_batch=True

      assert(ret_array.shape[0]==batch_size)
      num_batches_generated+=1
      ret_array=np.reshape(ret_array,(len(ret_array),1,image_height,image_width))
      yield ret_array,ret_array_2
      

#create anomalous images: random hot towers, only works for barrel, endcap has super complicated geometry
def insert_hot_tower(input_image):
   to_ret=np.copy(input_image)

   height_range=range(0,to_ret.shape[0],5)
   width_range=range(0,to_ret.shape[1],5)

   y_cord=random.choice(height_range)#pick random y for a towers lower left point
   x_cord=random.choice(width_range)#pick random x ---do---

   for channel_y in range(y_cord,y_cord+5):
      for channel_x in range(x_cord,x_cord+5):
         to_ret[channel_y,channel_x]*=1e4 #a very large number representing a hot tower

   to_ret_max=np.amax(to_ret)
   to_ret=to_ret/float(to_ret_max)      #renormalize
   return to_ret


def make_module_off(input_image):
   to_ret=np.copy(input_image)

   modules_off=2 if random.choice(range(10))<2 else 1 # 1 out of 10 times switch off two modules
   height_range=range(0,to_ret.shape[0],85)
   width_range=range(0,to_ret.shape[1],20)

   for dummy in range(modules_off):
      y_cord=random.choice(height_range)#pick random y for a towers lower left point
      x_cord=random.choice(width_range)#pick random x ---do---

      for channel_y in range(y_cord,y_cord+85):
         for channel_x in range(x_cord,x_cord+20):
            to_ret[channel_y,channel_x]=0 #a very large number representing a hot tower

   return to_ret
