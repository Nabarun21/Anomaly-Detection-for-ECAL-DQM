import numpy as np
import os
import h5py

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

from keras.layers import Input, Dense, Conv2D, MaxPooling2D, UpSampling2D
from keras.models import Model
from keras.models import load_model
from keras import backend as K
from keras import callbacks
from keras.utils import plot_model
from keras import callbacks
""" First fully running model to run on gpu: from here on we optimize"""



#helper fucntions

def get_data(file_name,group='EBOccupancyTask_EBOT_rec_hit_occupancy'):
   "picks samples out of a hdf file and return a numpy array"
   global data_folder
   input_file=h5py.File(data_folder+"/"+file_name,'r')
   logging.debug("Loading data from file: "+file_name)
   ret_array=np.array((input_file[group]))
   logging.debug("Supplying "+str(ret_array.shape[0])+" samples")
   return ret_array
   
def get_num_samples(file_list,group='EBOccupancyTask_EBOT_rec_hit_occupancy'):
   "returns total number of samples in a list of hdf files"
   global data_folder
   total_count=0
   for filename in file_list:
      input_file=h5py.File(data_folder+"/"+filename,'r')
      data=np.array((input_file[group]))
      total_count+=data.shape[0]
   return total_count

#custom callback fucntions

class train_histories(callbacks.Callback):
   def on_train_begin(self, logs={}):
      self.aucs = []
      self.epochwise_losses = []
      self.batchwise_losses = []

   def on_train_end(self, logs={}):
      return

   def on_epoch_begin(self, epoch, logs={}):
      return

   def on_epoch_end(self, epoch, logs={}):
      self.epochwise_losses.append(logs.get('loss'))
      return

   def on_batch_begin(self, batch, logs={}):
      return

   def on_batch_end(self, batch, logs={}):
      self.batchwise_losses.append(logs.get('loss'))
      return



#generator
def batch_generator(batch_size,data_file_list):
   """ generates batch_size images, well thats's obvious. throws exception when data runs out"""
   if batch_size<=0 or not isinstance(batch_size,int):
      logging.error("Batch size needs to be an integer greater than 0")
      raise StopIteration("Batch size needs to be an integer greater than !!")
   

   file_index=0
   leftover_array=get_data(data_file_list[file_index]) #start off with the first data file
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
               new_array=get_data(data_file_list[file_index])
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
      ret_array=np.reshape(ret_array,(len(ret_array),1,170,360))
      yield ret_array
      




#first the model

input_img=Input(shape=(1,170,360))

#encoder
encoder_layer_1=Conv2D(8,(3,3),activation='relu',padding='same',data_format='channels_first')(input_img)
encoder_layer_1_pooled=MaxPooling2D((2, 2), padding='same',data_format='channels_first')(encoder_layer_1)


encoder_layer_2=Conv2D(8,(3,3),activation='relu',padding='same',data_format='channels_first')(encoder_layer_1_pooled)
encoded_final=MaxPooling2D((5, 5), padding='same',data_format='channels_first')(encoder_layer_2)


#decoder
decoder_layer_1=Conv2D(8, (3, 3), activation='relu', padding='same',data_format='channels_first')(encoded_final)
decoder_layer_1_upsampled=UpSampling2D((5, 5),data_format='channels_first')(decoder_layer_1)


decoder_layer_2=Conv2D(8, (3, 3), activation='relu', padding='same',data_format='channels_first')(decoder_layer_1_upsampled)
decoder_layer_2_upsampled=UpSampling2D((2, 2),data_format='channels_first')(decoder_layer_2)


decoded_final=Conv2D(1,(3,3),activation='sigmoid',data_format='channels_first',padding='same')(decoder_layer_2_upsampled)


autoencoder=Model(input_img, decoded_final)
autoencoder.compile(optimizer='adadelta', loss='binary_crossentropy')



#get the data
try:
   data_folder=os.environ["DATA"]
except KeyError:
   "Please cd into the module's base folder and run set_env from there."
   
file_list=os.listdir(data_folder)
train_data_list=file_list[0:3] #choosing 63 here keeps ~80% of data for testing, rest for training and val, need to automatize this
test_data_list=file_list[63:64]


logging.debug("Current file list is "+str(file_list)+" and has "+str(len(file_list))+" files")

#start training
logging.info("Current training set is made from "+str(len(train_data_list))+" files and has "+str(get_num_samples(train_data_list))+" examples")


early_stopping = callbacks.EarlyStopping(monitor='val_loss', patience=3) # Well this is sorta useless here, since nb epochs is actually set to 1 in model.fit and the number of epochs here is the number of time the outer loop runs
tensorboard=callbacks.TensorBoard(log_dir='../logs', histogram_freq=1, batch_size=32, write_graph=True, write_grads=True, write_images=True, embeddings_freq=0, embeddings_layer_names=None, embeddings_metadata=None)
training_history=train_histories()
      

num_epochs=10
patience=3    #number of epochs where we see no improvement after which we stop training
current_epoch_loss=1000   #arbitrarily large number
epochwise_loss_history=[]
batchwise_loss_history=[]


for epoch in range(num_epochs):
   np.random.shuffle(train_data_list)
   my_generator=batch_generator(300,train_data_list)
   logging.info("Epoch no %s",epoch+1)
   gen_batch_loss_history=[]
   for batch in my_generator:
      autoencoder.fit(batch,batch,epochs=1,batch_size=30,shuffle=True,validation_split=0.25,callbacks=[tensorboard,training_history,early_stopping])
      batchwise_loss_history.extend(training_history.batchwise_losses)
      gen_batch_loss_history.extend(training_history.epochwise_losses)
   epoch_loss=np.mean(gen_batch_loss_history)
   epochwise_loss_history.extend(epoch_loss)
   if epoch_loss<last_epoch_loss:
      last_epoch_loss=epoch_loss
      count=0
   else:
      count+=1
   assert(count<=patience)
   if count==patience:
      logging.info("Stopping training:Loss hasn't decreased for last "+str(patience)+" epochs and I have run out of patience")
      break


print(epochwise_loss_history)
print(batchwise_loss_history)


#save the trained model
autoencoder.save("../models/autoencoder_v0.h5")

#training

logging.info("Current test set is made from "+str(len(test_data_list))+" files and has "+str(get_num_samples(test_data_list))+" examples")


my_test_generator=batch_generator(300,test_data_list)
for test_batch in my_test_generator:
   loss=autoencoder.evaluate(test_batch,test_batch,batch_size=30)
   print(loss)


