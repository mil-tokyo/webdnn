This is work in progress.

# export model
Python 3.6+Keras 1.2.2
```
git clone https://github.com/robertomest/neural-style-keras
cd neural-style-keras
git apply ../export_model.patch
cd data/models
sh download_models.sh
cd ../..
mkdir dummy
python fast_style_transfer.py --checkpoint_path data/models/candy.h5 --input_path content_imgs/ --output_path dummy --use_style_name --img_size 256
```
Commit: 11fecd8e99228aab4851e4c00e85ed31217406db

This will produce `model.h5` which contains model structure and weight data.


# convert model
Python 3.6+Keras 2.0.8
```
OPTIMIZE=0 DEBUG=1 python ../../bin/convert_keras.py neural-style-keras/model.h5 --input_shape '(1,256,256,3)' --out output --plugin custom.py --plugin kernels_webassembly.py --backend webassembly
```

