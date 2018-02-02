#python prediction.py --loss_name binary_crossentropy --model_name CNN_v2
#python prediction.py --loss_name binary_crossentropy --model_name CNN_v3
#python prediction.py --loss_name binary_crossentropy --model_name CNN_v4
python prediction.py --loss_name binary_crossentropy --model_name CNN_v5

#python prediction.py --loss_name binary_crossentropy --model_name best_model_v2
#python prediction.py --loss_name binary_crossentropy --model_name best_model_v3
#python prediction.py --loss_name binary_crossentropy --model_name best_model_v4
python prediction.py --loss_name binary_crossentropy --model_name best_model_v5

#python plot_loss_as_metric.py --loss_name binary_crossentropy --model_name CNN_v2
#python plot_loss_as_metric.py --loss_name binary_crossentropy --model_name CNN_v3
#python plot_loss_as_metric.py --loss_name binary_crossentropy --model_name CNN_v4
python plot_loss_as_metric.py --loss_name binary_crossentropy --model_name CNN_v5
