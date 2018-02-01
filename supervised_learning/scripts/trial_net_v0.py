import numpy as np
import h5py
from keras.layers import Input, Dense, Conv2D, MaxPooling2D, UpSampling2D
from keras.models import Model
from keras import backend as K

""" This is the version 0 model, This is just to get the setup working and all """



#first the model

input_img=Input(shape=(1,170,360))

#encoder
encoder_layer_1=Conv2D(8,(5,5),activation='relu',padding='same',data_format='channels_first')(input_img)
encoder_layer_1_pooled=MaxPooling2D((2, 2), padding='same',data_format='channels_first')(encoder_layer_1)

print(encoder_layer_1_pooled.shape)

encoder_layer_2=Conv2D(8,(5,5),activation='relu',padding='same',data_format='channels_first')(encoder_layer_1_pooled)
encoded_final=MaxPooling2D((5, 5), padding='same',data_format='channels_first')(encoder_layer_2)

print(encoded_final.shape)

#decoder
decoder_layer_1=Conv2D(8, (5, 5), activation='relu', padding='same',data_format='channels_first')(encoded_final)
decoder_layer_1_upsampled=UpSampling2D((5, 5),data_format='channels_first')(decoder_layer_1)
print(decoder_layer_1_upsampled.shape)

decoder_layer_2=Conv2D(8, (5, 5), activation='relu', padding='same',data_format='channels_first')(decoder_layer_1_upsampled)
decoder_layer_2_upsampled=UpSampling2D((2, 2),data_format='channels_first')(decoder_layer_2)
print(decoder_layer_2_upsampled.shape)

decoded_final=Conv2D(1,(5,5),activation='sigmoid',data_format='channels_first',padding='same')(decoder_layer_2_upsampled)
print(decoded_final.shape)

autoencoder=Model(input_img, decoded_final)
autoencoder.compile(optimizer='adadelta', loss='binary_crossentropy')



#get the data

filename='../data/ECAL_rechit_occ_time_283877.hdf5'
input_file=h5py.File(filename,'r')
data=np.array((input_file['EBOccupancyTask_EBOT_rec_hit_occupancy']))
data=np.reshape(data,(len(data),1,170,360))


autoencoder.fit(data,data,
                epochs=5,
                batch_size=20,
                shuffle=True,
                validation_data=(data, data))


