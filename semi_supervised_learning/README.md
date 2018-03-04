# Anomaly-Detection-for-ECAL-DQM

(need keras, tensorflow and h5py packages)

First setup some global env variables:

```
source set_env.sh

```

To train:

```
cd scripts

python autoencoder_v[].py **options**

```

Training is logged in logs/model_name_lossfunc_name_optimizer_name.log

Model is saved in models/model_namelossfunc_name_optimizer_name.h5


For plotting training/validation v/s batch/epoch losses:

```
plot_losses.py  **options**

```

To plot reconstruction loss spectrum as metric

```
plot_loss_as_metric.py **options**

```


