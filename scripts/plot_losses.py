import pickle
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument(
      "--model_name",
      action="store",
      dest="model_name",
      default="autoencoder_v0",
      help="name of the saved model")
parser.add_argument(
      "--opt_name",
      action="store",
      dest="opt_name",
      default="adadelta",
      help="name of the optimizer used")

args=parser.parse_args()
def plot_losses(loss_list,plot_dir,save_name='autoencoder_v0_adadelta',x_label='epoch',y_label='validation_loss',is_xlog=False,is_ylog=False):
    x_list=range(2,len(loss_list)+2)
    
    my_fig=plt.figure()
    ax=my_fig.add_subplot(111)

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(save_name+"_"+y_label+"_v_"+x_label)
    if 'batch' in x_label:
        ax.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
    ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    if is_xlog and is_ylog:
        ax.loglog(x_list,loss_list)
    elif is_ylog:
        ax.semilogy(x_list,loss_list)
    elif is_xlog:
        ax.semilogx(x_list,loss_list)
    else:
        ax.plot(x_list,loss_list)
    my_fig.savefig(plot_dir+'/'+save_name+"_"+y_label+"_v_"+x_label+".png")



basedir=os.environ['BASEDIR']

if __name__=="__main__":
    with open(basedir+"/models/"+args.model_name+'_'+args.opt_name+"_epochwise_val_loss.txt", "r") as fp: 
        epoch_val_loss_list=pickle.load(fp)
    with open(basedir+"/models/"+args.model_name+'_'+args.opt_name+"_epochwise_loss.txt", "r") as fp: 
        epoch_loss_list=pickle.load(fp)
    with open(basedir+"/models/"+args.model_name+'_'+args.opt_name+"_batchwise_loss.txt", "r") as fp: 
        batchwise_loss_list=pickle.load(fp)
    
        
    plot_losses(epoch_val_loss_list[1:],basedir+'/plots',save_name=args.model_name+'_'+args.opt_name,is_ylog=False)
    plot_losses(epoch_loss_list[1:],basedir+'/plots',save_name=args.model_name+'_'+args.opt_name,is_ylog=False,y_label='training_loss')
    plot_losses(batchwise_loss_list[100:],basedir+'/plots',save_name=args.model_name+'_'+args.opt_name+'_loglog',is_ylog=True,is_xlog=True,x_label='batch',y_label='training_loss')
    plot_losses(batchwise_loss_list[100:],basedir+'/plots',save_name=args.model_name+'_'+args.opt_name,is_xlog=True,x_label='batch',y_label='training_loss')
