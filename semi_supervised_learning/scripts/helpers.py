import subprocess as sp
import numpy as np
import pickle
import os
import h5py
from keras import callbacks
import random
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
#logging.basicConfig(level=logging_numeric_level, format='%(asctime)s %(levelname)s: %(message)s')

logger = logging.getLogger(__name__)

#helper fucntions
def _output_to_list(output):
    return output.decode('ascii').split('\n')[:-1]

def mask_busy_gpus(leave_unmasked=1, random=True):
  try:
    command = "nvidia-smi --query-gpu=memory.free --format=csv"
    memory_free_info = _output_to_list(sp.check_output(command.split()))[1:]
    memory_free_values = [int(x.split()[0]) for i, x in enumerate(memory_free_info)]
    available_gpus = [i for i, x in enumerate(memory_free_values) if x > 1024]

    if len(available_gpus) < leave_unmasked:
      logging.info('Found only %d usable GPUs in the system' % len(available_gpus))
      exit(0)

    if random:
      available_gpus = np.asarray(available_gpus)
      np.random.shuffle(available_gpus)

    # update CUDA variable
    gpus = available_gpus[:leave_unmasked]
    setting = ','.join(map(str, gpus))
    os.environ["CUDA_VISIBLE_DEVICES"] = setting
    logging.info('Left next %d GPU(s) unmasked: [%s] (from %s available)'
          % (leave_unmasked, setting, str(available_gpus)))
  except sp.CalledProcessError as e:
    logging.info("Error on GPU masking:\n", e.output)

  except Exception as e:
    logging.info('"nvidia-smi" is probably not installed. GPUs are not masked')
    logging.info(e)

def normalize(a):
    means=a.mean(axis=(1,2))
    stds=a.std(axis=(1,2))
    means=np.reshape(means,(a.shape[0],1,1))
    stds=np.reshape(stds,(a.shape[0],1,1))
    ret_array=a-means
    ret_array=ret_array/stds
    return ret_array

def max_abs_scale(a):
    maxes=np.abs(a).max(axis=(1,2))
    maxes=np.reshape(maxes,(a.shape[0],1,1))
    ret_array=a/maxes
    return ret_array


def preprocess(a,level=0):
    a[a==0]=1e-10
    try:
        level=int(level)
    except TypeError:
        print("preprocessing level needs to be integer type or be able to be cast into integer type")
    if level==0:return a #so nothin
    if level==1:return max_abs_scale(a) #sigmoid +binary cross entropy or MSE
    if level==2:return normalize(a) #linear +MSE
    if level==3:return max_abs_scale(normalize(a))#tanh +MSE
    if level==4:return max_abs_scale(np.log(a))#tanh +MSE
    if level==5:return np.log(a)#linear +MSE
    
def get_data(file_name,group='EBOccupancyTask_EBOT_rec_hit_occupancy',data_type='good_2016',preprocess_level=0):
   "picks samples out of a hdf file and return a numpy array"
   data_folder=os.environ["DATA"].replace("good_2016",data_type)
   input_file=h5py.File(data_folder+"/"+file_name,'r')
   logging.debug("Loading data from file: "+file_name)
   ret_array=np.array((input_file[group]))
   ret_array=preprocess(ret_array,preprocess_level)
   logging.debug("Supplying "+str(ret_array.shape[0])+" samples")
   return ret_array
   
def get_num_samples(file_list,group='EBOccupancyTask_EBOT_rec_hit_occupancy'):
   "returns total number of samples in a list of hdf files"
   data_folder=os.environ["DATA"]
   total_count=0
   for filename in file_list:
      input_file=h5py.File(data_folder+"/"+filename,'r')
      data=np.array((input_file[group]))
      total_count+=data.shape[0]
   return total_count


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



#generator
def batch_generator(batch_size,data_file_list,group='EBOccupancyTask_EBOT_rec_hit_occupancy',data_type='good_2016',prep_level=0):
   """ generates batch_size images, well thats's obvious. throws exception when data runs out"""
   if batch_size<=0 or not isinstance(batch_size,int):
      logging.error("Batch size needs to be an integer greater than 0")
      raise StopIteration("Batch size needs to be an integer greater than !!")
   

   file_index=0
   leftover_array=get_data(data_file_list[file_index],group,data_type,prep_level) #start off with the first data file
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
            new_batch=True
         else:
            logging.debug("Current/leftover batch doesn't have enough samples, loading new file")
            file_index+=1
            try:
               new_array=get_data(data_file_list[file_index],group,data_type,prep_level)
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
            elif num_current_samples>samples_needed_for_next_batch:
               logging.debug("Enough Samples for next batch, keeping the rest as leftover")
               array_to_add=new_array[0:samples_needed_for_next_batch]
               ret_array=np.concatenate([leftover_array,array_to_add])
               new_batch=True
               del leftover_array
               leftover_array=new_array[samples_needed_for_next_batch:]
            else:
               logging.debug("Exactly the number of samples for a batch,lefotver batch has now zero samples")
               ret_array=np.concatenate([leftover_array,new_array])
               new_batch=True
               left_over_array=np.zeros(shape=[0,image_height,image_width])

      assert(ret_array.shape[0]==batch_size)
      num_batches_generated+=1
      ret_array=np.reshape(ret_array,(len(ret_array),1,image_height,image_width))
      yield ret_array
      

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

#   to_ret_max=np.amax(to_ret)
#   to_ret=to_ret/float(to_ret_max)      #renormalize
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
            to_ret[channel_y,channel_x]=0 #0, module is off

   return to_ret
