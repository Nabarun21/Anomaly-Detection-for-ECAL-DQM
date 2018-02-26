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
      default="model_v0",
      help="name of the saved model")
parser.add_argument(
      "--opt_name",
      action="store",
      dest="opt_name",
      default="adam",
      help="name of the optimizer used")
parser.add_argument(
      "--loss_name",
      action="store",
      dest="loss_name",
      default="MSE",
      help="name of the optimizer used")
parser.add_argument(
      "--prep_level",
      action="store",
      dest="prep_level",
      default=0,
      help="preprocess-ng type")

args=parser.parse_args()
def plot_losses(loss_list,plot_dir,save_name='autoencoder_v0_adadelta',x_label='epoch',y_label='validation_loss',is_xlog=False,is_ylog=False):
    x_list=range(1,len(loss_list)+1)
    
    my_fig=plt.figure()
    ax=my_fig.add_subplot(111)
    final_loss="final training loss: {:.3e}".format(min(loss_list))
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    figure_title=save_name+"_"+y_label+"_v_"+x_label
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
    plt.text(0.5, 1.08, figure_title,
         horizontalalignment='center',
         fontsize=15,
         transform = ax.transAxes)
    plt.text(0.72, 0.85, final_loss,
         horizontalalignment='center',
         fontsize=13,
         transform = ax.transAxes)

    my_fig.savefig(plot_dir+'/train_val_losses/'+save_name+"_"+y_label+"_v_"+x_label+".png")



basedir=os.environ['BASEDIR']

if __name__=="__main__":
    with open(basedir+"/models/"+args.model_name+'_'+args.loss_name+'_'+args.opt_name+"_epochwise_val_loss.txt", "r") as fp: 
        epoch_val_loss_list=pickle.load(fp)

    with open(basedir+"/models/"+args.model_name+'_'+args.loss_name+'_'+args.opt_name+"_epochwise_loss.txt", "r") as fp: 
        epoch_loss_list=pickle.load(fp)

    with open(basedir+"/models/"+args.model_name+'_'+args.loss_name+'_'+args.opt_name+"_batchwise_loss.txt", "r") as fp: 
        batchwise_loss_list=pickle.load(fp)
    
        
    plot_losses(epoch_val_loss_list[0:],basedir+'/plots',save_name=args.model_name+'_'+args.loss_name+'_'+args.opt_name,is_ylog=False)
    plot_losses(epoch_loss_list[0:],basedir+'/plots',save_name=args.model_name+'_'+args.loss_name+'_'+args.opt_name,is_ylog=False,y_label='training_loss')
    plot_losses(batchwise_loss_list[100:],basedir+'/plots',save_name=args.model_name+'_'+args.loss_name+'_'+args.opt_name+'_loglog',is_ylog=True,is_xlog=True,x_label='batch',y_label='training_loss')
    plot_losses(batchwise_loss_list[100:],basedir+'/plots',save_name=args.model_name+'_'+args.loss_name+'_'+args.opt_name,is_xlog=True,x_label='batch',y_label='training_loss')
