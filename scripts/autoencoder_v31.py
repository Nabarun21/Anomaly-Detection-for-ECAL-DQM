import numpy as np
import pickle
import os
import h5py
import argparse
import matplotlib.pyplot as plt

import logging

from keras.layers import Input, Dense, Conv2D, MaxPooling2D, UpSampling2D
from keras.models import Model
from keras import backend as K
from keras import callbacks
from keras import callbacks

""" v2: even more layers, yoohooo"""

parser = argparse.ArgumentParser()
parser.add_argument(
      "--model_name",
      action="store",
      dest="model_name",
      default="autoencoder_v2",
      help="name of the saved model, will be saved as a h5 file under the models directory")
parser.add_argument(
      "--int_log",
      action="store_true",
#      dest="model_name",
      help="print logging information to command line")
parser.add_argument(
      "--opt_name",
      action="store",
      dest="opt_name",
      default="adam",
      help="name of the optimizer to be used")
parser.add_argument(
      "--log_level",
      action="store",
      dest="log_level",
      default="INFO",
      help="logging level: INFO, DEBUG, WARNING etc.")
parser.add_argument(
      "--img_type",
      action="store",
      dest="img_type",
      default="EB_OCC",
      help="which class of DQM images to train on,EB_OCC (barrel occupancy), EB_TIM (barrel timing), EE_OCC (endcap occupacncy) etc")

args = parser.parse_args()

logging_numeric_level = getattr(logging, args.log_level.upper(), None)

if not isinstance(logging_numeric_level, int):
    raise ValueError('Invalid log level: %s' % args.log_level)
if args.int_log:
    logging.basicConfig(level=logging_numeric_level, format='%(asctime)s %(levelname)s: %(message)s')
else:
    logging.basicConfig(level=logging_numeric_level, format='%(asctime)s %(levelname)s: %(message)s',filename=os.environ["BASEDIR"]+'/logs/'+args.model_name+'_'+args.opt_name+'.log')
#logging.basicConfig(level=logging_numeric_level, format='%(asctime)s %(levelname)s: %(message)s')

logger = logging.getLogger(__name__)

#helper fucntions

def get_data(file_name,group='EBOccupancyTask_EBOT_rec_hit_occupancy',data_type='good'):
   "picks samples out of a hdf file and return a numpy array"
   data_folder=os.environ["DATA"].replace("good",data_type)
   input_file=h5py.File(data_folder+"/"+file_name,'r')
   logging.debug("Loading data from file: "+file_name)
   ret_array=np.array((input_file[group]))
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
def batch_generator(batch_size,data_file_list,group='EBOccupancyTask_EBOT_rec_hit_occupancy',data_type='good'):
   """ generates batch_size images, well thats's obvious. throws exception when data runs out"""
   if batch_size<=0 or not isinstance(batch_size,int):
      logging.error("Batch size needs to be an integer greater than 0")
      raise StopIteration("Batch size needs to be an integer greater than !!")
   

   file_index=0
   leftover_array=get_data(data_file_list[file_index],group,data_type) #start off with the first data file
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
               new_array=get_data(data_file_list[file_index],group,data_type)
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
      


if __name__=='__main__':

    #get the data
    try:
        data_folder=os.environ["DATA"]
    except KeyError:
        "Please cd into the module's base folder and run set_env from there."
   
    file_list=os.listdir(data_folder)
    train_data_list=file_list[0:63] #choosing 63 here keeps ~80% of data for testing, rest for training and val, need to automatize this
    test_data_list=file_list[63:]

    logging.debug("Current file list is "+str(file_list)+" and has "+str(len(file_list))+" files")

    if 'EB' in args.img_type.upper():
        image_type=os.environ[args.img_type]
    elif 'TIM' in args.img_type.upper():
        image_type=os.environ['EEP_TIM']
        image_type2=os.environ['EEM_TIM']
    else:
        image_type=os.environ['EEP_OCC']
        image_type_eem=os.environ['EEM_OCC']


    #get input image shape
    (_,image_height,image_width)=get_data(file_list[0],image_type).shape

    

    #load or build the model

    input_img=Input(shape=(1,image_height,image_width))

    #encoder
    encoder_layer_1=Conv2D(16,(3,3),activation='relu',padding='same',data_format='channels_first')(input_img)
    logging.debug(str(encoder_layer_1.shape))
    encoder_layer_1_pooled=MaxPooling2D((2, 2), padding='same',data_format='channels_first')(encoder_layer_1)
    logging.debug(str(encoder_layer_1_pooled.shape))

    encoder_layer_2=Conv2D(8,(3,3),activation='relu',padding='same',data_format='channels_first')(encoder_layer_1_pooled)
    logging.debug(str(encoder_layer_2.shape))

    encoder_layer_3=Conv2D(4,(3,3),activation='relu',padding='same',data_format='channels_first')(encoder_layer_2)
    logging.debug(str(encoder_layer_3.shape))
    encoder_layer_3_pooled=MaxPooling2D((2, 2), padding='same',data_format='channels_first')(encoder_layer_3)
    logging.debug(str(encoder_layer_3_pooled.shape))

    encoder_final=Conv2D(4,(3,3),activation='relu',padding='same',data_format='channels_first')(encoder_layer_3_pooled)
    logging.debug(str(encoder_final.shape))

    #decoder
    decoder_layer_1=Conv2D(4, (3, 3), activation='relu', padding='same',data_format='channels_first')(encoder_final)
    logging.debug(str(decoder_layer_1.shape))
    decoder_layer_1_upsampled=UpSampling2D((2, 2),data_format='channels_first')(decoder_layer_1)
    logging.debug(str(decoder_layer_1_upsampled.shape))

    decoder_layer_2=Conv2D(4, (3, 3), activation='relu', padding='same',data_format='channels_first')(decoder_layer_1_upsampled)
    logging.debug(str(decoder_layer_2.shape))

    decoder_layer_3=Conv2D(8, (3, 3), activation='relu', padding='same',data_format='channels_first')(decoder_layer_2)
    logging.debug(str(decoder_layer_3.shape))
    decoder_layer_3_upsampled=UpSampling2D((2, 2),data_format='channels_first')(decoder_layer_3)
    logging.debug(str(decoder_layer_3_upsampled.shape))
    
    decoder_layer_4=Conv2D(16, (3, 3), activation='relu', padding='same',data_format='channels_first')(decoder_layer_3_upsampled)
    logging.debug(str(decoder_layer_4.shape))

    if 'EB' in args.img_type.upper(): 
        decoder_final=Conv2D(1,(3,1),activation='sigmoid',data_format='channels_first',padding='valid')(decoder_layer_4)
        logging.debug(str(decoder_final.shape))
    else:
        decoder_final=Conv2D(1,(3,3),activation='sigmoid',data_format='channels_first',padding='same')(decoder_layer_4)
        logging.debug(str(decoder_final.shape))
    
    autoencoder=Model(input_img, decoder_final)
    autoencoder.compile(optimizer=args.opt_name, loss='mean_squared_error')



    #start training
    logging.info("Training with "+image_type+" images")
    logging.info("Current training set is made from "+str(len(train_data_list))+" files and has "+str(get_num_samples(train_data_list,image_type))+" examples")



    early_stopping = callbacks.EarlyStopping(monitor='val_loss', patience=3) # Well this is sorta useless here, since nb epochs is actually set to 1 in model.fit and the number of epochs here is the number of time the outer loop runs
    tensorboard=callbacks.TensorBoard(log_dir='../logs', histogram_freq=1, batch_size=32, write_graph=True, write_grads=True, write_images=True, embeddings_freq=0, embeddings_layer_names=None, embeddings_metadata=None)
    training_history=train_histories()
      

    num_epochs=100
    patience=3    #number of epochs where we see no improvement after which we stop training
    last_epoch_val_loss=1000   #arbitrarily large number
    perc_decrease_per_epoch=0.1
    epochwise_loss_history=[]
    batchwise_loss_history=[]
    epochwise_val_loss_history=[]
    batchwise_val_loss_history=[]
    epoch_count=0
    

    for epoch in range(num_epochs):
#        np.random.shuffle(train_data_list)
        logging.info("Epoch no %s",epoch+1)
        my_generator=batch_generator(400,train_data_list,image_type)
        gen_batch_loss_history=[]
        gen_batch_val_loss_history=[]

        logging.info("Training on EB or EE+ images")
        for batch in my_generator:
            autoencoder.fit(batch,batch,epochs=1,batch_size=30,shuffle=True,validation_split=0.25,callbacks=[training_history,early_stopping])
            batchwise_loss_history.extend(training_history.batchwise_losses)
            gen_batch_loss_history.extend(training_history.epochwise_losses)
            gen_batch_val_loss_history.extend(training_history.epochwise_val_losses)
        if 'EB' not in args.img_type.upper():
            logging.info("Training on EE- images")
            my_generator_eem=batch_generator(400,train_data_list,image_type_eem)
            for batch_eem in my_generator_eem:
                autoencoder.fit(batch_eem,batch_eem,epochs=1,batch_size=30,shuffle=True,validation_split=0.25,callbacks=[training_history,early_stopping])
                batchwise_loss_history.extend(training_history.batchwise_losses)
                gen_batch_loss_history.extend(training_history.epochwise_losses)
                gen_batch_val_loss_history.extend(training_history.epochwise_val_losses)


        epoch_loss=np.mean(gen_batch_loss_history)
        epochwise_loss_history.append(epoch_loss)

        epoch_val_loss=np.mean(gen_batch_val_loss_history)
        epochwise_val_loss_history.append(epoch_val_loss)
        if epoch_val_loss<last_epoch_val_loss*(1-0.01*perc_decrease_per_epoch):
            last_epoch_val_loss=epoch_val_loss
            epoch_count=0
        else:
            logging.info("Validation loss hasn't decreased by more than "+str(perc_decrease_per_epoch)+'%')
            logging.info("####                        ######")
            epoch_count+=1
        assert(epoch_count<=patience)
        if epoch_count==patience:
            logging.info("Stopping training:Loss hasn't decreased for last "+str(patience)+" epochs and I have run out of patience")
            logging.info("        ")
            logging.info("        ")
            logging.info("*********************====================*************************")
            logging.info("*********************====================*************************")
            logging.info("*********************====================*************************")
            logging.info("        ")
            logging.info("        ")
            break


    logging.info("Epochwise training loss history is : "+str(epochwise_loss_history))
    logging.info("        ")
    logging.info("        ")
    logging.info("*********************====================*************************")
    logging.info("*********************====================*************************")
    logging.info("*********************====================*************************")
    logging.info("        ")
    logging.info("        ")
    logging.info("Batchwise training loss history is : "+str(batchwise_loss_history))
    logging.info("        ")
    logging.info("        ")
    logging.info("*********************====================*************************")
    logging.info("*********************====================*************************")
    logging.info("*********************====================*************************")
    logging.info("        ")
    logging.info("        ")
    logging.info("Epochwise validation loss history is : "+str(epochwise_val_loss_history))



    #save the trained model
    autoencoder.save(os.environ['BASEDIR']+"/models/"+args.model_name+'_'+args.opt_name+'.h5')

    with open(os.environ['BASEDIR']+"/models/"+args.model_name+'_'+args.opt_name+"_epochwise_loss.txt", "wb") as fp:   #Pickling
        pickle.dump(epochwise_loss_history, fp)
    with open(os.environ['BASEDIR']+"/models/"+args.model_name+'_'+args.opt_name+"_batchwise_loss.txt", "wb") as fp:   #Pickling
        pickle.dump(batchwise_loss_history, fp)
    with open(os.environ['BASEDIR']+"/models/"+args.model_name+'_'+args.opt_name+"_epochwise_val_loss.txt", "wb") as fp:   #Pickling
        pickle.dump(epochwise_val_loss_history, fp)


