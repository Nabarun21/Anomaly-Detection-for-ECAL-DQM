import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os
import keras.models as models
import argparse
import helpers as helper_functions


""" plot loss histograms as metric"""


parser = argparse.ArgumentParser()
parser.add_argument(
      "--model_name",
      action="store",
      dest="model_name",
      default="autoencoder_v2",
      help="name of the saved model, will be saved as a h5 file under the models directory")
parser.add_argument(
      "--opt_name",
      action="store",
      dest="opt_name",
      default="adam",
      help="name of the optimizer to be used")
parser.add_argument(
      "--loss_name",
      action="store",
      dest="loss_name",
      default="MSE",
      help="name of the optimizer to be used")

parser.add_argument(
      "--log_level",
      action="store",
      dest="log_level",
      default="INFO",
      help="logging level: INFO, DEBUG, WARNING etc.")

args = parser.parse_args()

def plot_loss_as_metric(loss_list,plot_dir,save_name='autoencoder_v0_adadelta',is_xlog=False,is_ylog=False,x_label='loss',y_label='a.u.',train_test='train',anomalous_loss_list=None):

    if train_test=='train':
        assert(anomalous_loss_list==None,"This is training loss plotting and we do not train with bad examples")

    
    my_fig=plt.figure()
    ax=my_fig.add_subplot(111)
    mean_std="mean: {:.2e}".format(np.mean(loss_list))+", std: {:.2e}".format(np.std(loss_list))
    min_loss="min: {:.8e}".format(min(loss_list))
    max_loss="max: {:.8e}".format(max(loss_list))
    x_min=np.mean(loss_list)-4.5*np.std(loss_list)
    x_max=np.mean(loss_list)+4.5*np.std(loss_list)

    if anomalous_loss_list:
        print(anomalous_loss_list)
        x_max=max(max(loss_list),max(anomalous_loss_list))*1.01
        x_min=min(min(loss_list),min(anomalous_loss_list))*0.99
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    figure_title=save_name+"_"+train_test
    ax.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
    if anomalous_loss_list:
        print(min(anomalous_loss_list))
        print(max(anomalous_loss_list))

    if x_max/x_min>500 and anomalous_loss_list:
        plt.xscale('log')
    #    ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
        if is_ylog:
            ax.hist(anomalous_loss_list,bins=40,label='bad_data',log=True,color='#ff7f0e')
        else:
            ax.hist(anomalous_loss_list,bins=40,label='bad_data',log=False,color='#ff7f0e')



    if is_xlog and is_ylog:
        ax.hist(loss_list,bins=40,log=True,label='good_data',color='#1f77b4')
    elif is_ylog:
        ax.hist(loss_list,bins=40,log=True,label='good_data',color='#1f77b4')
    elif is_xlog:
        ax.hist(loss_list,bins=40,log=True,label='good_data',color='#1f77b4')
    else:
        ax.hist(loss_list,bins=40,label='good_data',log=False,color='#1f77b4')


    if anomalous_loss_list and x_max/x_min<=500:
        if is_ylog:
            ax.hist(anomalous_loss_list,bins=40,label='bad_data',log=True,color='#ff7f0e')
        else:
            ax.hist(anomalous_loss_list,bins=40,label='bad_data',log=False,color='#ff7f0e')


    ax.legend(loc='upper left')
    ylim=ax.get_ylim()
    ax.set_ylim(top=1.25*ylim[1])
    plt.text(0.5, 1.08, figure_title,
         horizontalalignment='center',
         fontsize=15,
         transform = ax.transAxes)
    plt.text(0.72, 0.92, mean_std,
         horizontalalignment='center',
         fontsize=10,
         transform = ax.transAxes)
    plt.text(0.72, 0.83, min_loss,
         horizontalalignment='center',
         fontsize=10,
         transform = ax.transAxes)
    plt.text(0.72, 0.74, max_loss,
         horizontalalignment='center',
         fontsize=10,
         transform = ax.transAxes)

    

    my_fig.savefig(plot_dir+'/loss_as_metric/'+save_name+"_"+train_test+".png")

def plot_loss_scatter(loss_list,plot_dir,save_name='autoencoder_v0_adadelta',is_xlog=False,is_ylog=False,y_label=' loss',train_test='train',anomalous_loss_list=None):

    if train_test=='train':
        assert(anomalous_loss_list==None,"This is training loss plotting and we do not train with bad examples")


    my_fig=plt.figure()
    ax=my_fig.add_subplot(111)

    if anomalous_loss_list:
        x_max=max(max(loss_list),max(anomalous_loss_list))*1.01
        x_min=min(min(loss_list),min(anomalous_loss_list))*0.99
    ax.set_xlabel('event')
    ax.set_ylabel(y_label)

    figure_title=save_name+"_"+train_test
    ax.ticklabel_format(style='sci', axis='x', scilimits=(0,0))

    ax.scatter(range(len(loss_list)),loss_list,color='#1f77b4',label='good data')
    if anomalous_loss_list:
        ax.scatter(range(len(anomalous_loss_list)),anomalous_loss_list,color='#ff7f0e',label='bad data')


    ax.legend(loc='upper left')

    plt.text(0.5, 1.08, figure_title,
         horizontalalignment='center',
         fontsize=15,
         transform = ax.transAxes)

    my_fig.savefig(plot_dir+'/loss_as_metric/'+save_name+"_"+train_test+".png")



if __name__=="__main__":

    basedir=os.environ['BASEDIR']

    trained_model=models.load_model(basedir+"/models/"+args.model_name+'_'+args.loss_name+'_'+args.opt_name+'.h5') #load model


    image_type=os.environ['EB_OCC']

    try:       #get the data
        data_folder=os.environ["DATA"]
    except KeyError:
        "Please cd into the module's base folder and run set_env from there."
   
    file_list=os.listdir(data_folder)
    train_data_list=file_list[0:63] #choosing 63 here keeps ~80% of data for testing, rest for training and val, need to automatize this
    test_data_list=file_list[63:]

    anomalous_test_data_list_natural=[filename for filename in os.listdir(data_folder.replace("good_2016","bad_2016")) if "ECAL" in str(filename)] #from cms
    anomalous_test_data_list_artificial_hot_towers=os.listdir(data_folder.replace("good_2016","bad_2016/hot_towers")) #artificially created 
    anomalous_test_data_list_artificial_missing_modules=os.listdir(data_folder.replace("good_2016","bad_2016/missing_modules")) #artificially created

    #print(anomalous_test_data_list_natural)
 #   print(anomalous_test_data_list_artificial_hot_towers)
  #  print(anomalous_test_data_list_artificial_missing_modules)
    """
    print("Current training set is made from "+str(len(train_data_list))+" files and has "+str(helper_functions.get_num_samples(train_data_list))+" examples")

    my_training_data_generator=helper_functions.batch_generator(4,train_data_list,image_type)
    
    training_losses=[]
    for  batch in my_training_data_generator:
        loss=trained_model.evaluate(batch,batch,batch_size=4,verbose=0)
        training_losses.append(loss)
    
    """
    print("Current test set is made from "+str(len(test_data_list))+" files and has "+str(helper_functions.get_num_samples(test_data_list))+" examples")
    my_test_data_generator=helper_functions.batch_generator(4,test_data_list,image_type)



    test_losses=[]
    for  batch in my_test_data_generator:
        loss=trained_model.evaluate(batch,batch,batch_size=4,verbose=0)
        test_losses.append(loss)

    
    my_anomalous_test_data_generator_natural=helper_functions.batch_generator(1,anomalous_test_data_list_natural,data_type='bad_2016',group=image_type)
    my_anomalous_test_data_generator_artificial_hot_towers=helper_functions.batch_generator(1,anomalous_test_data_list_artificial_hot_towers,data_type='bad_2016/hot_towers',group=image_type)
    my_anomalous_test_data_generator_artificial_missing_modules=helper_functions.batch_generator(1,anomalous_test_data_list_artificial_missing_modules,data_type='bad_2016/missing_modules',group=image_type)

    anomalous_test_losses_natural=[]
    anomalous_test_losses_artificial_missing_modules=[]
    anomalous_test_losses_artificial_hot_towers=[]

    for  batch in my_anomalous_test_data_generator_natural:
        loss=trained_model.evaluate(batch,batch,batch_size=1,verbose=0)
        anomalous_test_losses_natural.append(loss)

    for  batch in my_anomalous_test_data_generator_artificial_hot_towers:
        loss=trained_model.evaluate(batch,batch,batch_size=1,verbose=0)
        anomalous_test_losses_artificial_hot_towers.append(loss)

    for  batch in my_anomalous_test_data_generator_artificial_missing_modules:
        loss=trained_model.evaluate(batch,batch,batch_size=1,verbose=0)
        anomalous_test_losses_artificial_missing_modules.append(loss)

   

#    plot_loss_as_metric(training_losses,basedir+'/plots',save_name=args.model_name+'_'+args.loss_name+'_'+args.opt_name,is_ylog=False)
    plot_loss_as_metric(test_losses,basedir+'/plots',save_name=args.model_name+'_'+args.loss_name+'_'+args.opt_name+'_hot_towers',is_ylog=False,train_test='test',anomalous_loss_list=anomalous_test_losses_artificial_hot_towers)
    plot_loss_as_metric(test_losses,basedir+'/plots',save_name=args.model_name+'_'+args.loss_name+'_'+args.opt_name+'_missing_modules',is_ylog=False,train_test='test',anomalous_loss_list=anomalous_test_losses_artificial_missing_modules)
    plot_loss_as_metric(test_losses,basedir+'/plots',save_name=args.model_name+'_'+args.loss_name+'_'+args.opt_name,is_ylog=True,train_test='test',anomalous_loss_list=None)
    
    plot_loss_scatter(test_losses,basedir+'/plots',save_name="scatter_"+args.model_name+'_'+args.loss_name+'_'+args.opt_name+'_hot_towers',is_ylog=False,train_test='test',anomalous_loss_list=anomalous_test_losses_artificial_hot_towers)
    plot_loss_scatter(test_losses,basedir+'/plots',save_name="scatter_"+args.model_name+'_'+args.loss_name+'_'+args.opt_name+'_missing_modules',is_ylog=False,train_test='test',anomalous_loss_list=anomalous_test_losses_artificial_missing_modules)
    plot_loss_scatter(test_losses,basedir+'/plots',save_name="scatter_"+args.model_name+'_'+args.loss_name+'_'+args.opt_name,is_ylog=True,train_test='test',anomalous_loss_list=anomalous_test_losses_natural)
    
    
