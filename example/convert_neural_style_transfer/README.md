# Neural Style Transfer
Example of running Neural Style Transfer model with WebDNN

Trained model is from
- [yusuketomoto/chainer-fast-neuralstyle](https://github.com/yusuketomoto/chainer-fast-neuralstyle)
- [gafr/chainer-fast-neuralstyle-models](https://github.com/gafr/chainer-fast-neuralstyle-models)

## Steps


1.  Clone [gafr/chainer-fast-neuralstyle-models](https://github.com/gafr/chainer-fast-neuralstyle-models) into `../../resources/`
    Note: Download of about 200MB model is needed.
    
    ```bash
    $ cd ../../
    $ git clone https://github.com/gafr/chainer-fast-neuralstyle-models
    ```
    
2.  Convert model

    ```bash
    $ python convert.py 
    ```

    `--model` option selects the style. For details, see `python convert.py -h`
    
3.  Access to `index.html` with your browser
