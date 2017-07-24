# Use with caffemodel

In this section, you will learn about how to convert your caffemodel
into `GraphDescriptor`, and run `GraphDescriptor` on your web page.

## 1. Convert Caffemodel into GraphDescriptor

See jupyter notebook ([caffenet_conversion.ipynb](https://github.com/mil-tokyo/mil-web-dnn/blob/master/example/convert_caffe/caffenet_conversion.ipynb)) to see how to convert model offline.

## 2. Run on web browser

In this section, I'll describe how to run generated descriptor on web browser. 
you can view complete codes (HTML and JS file) in `/example/convert_caffe`.

First, You have to initialize [`DescriptorRunner`](../api_reference/descriptor_runner/interfaces/webdnn.dnndescriptorrunner.html) 
and load model data.

```js
let runner = await WebDNN.load('./output');
```

WebDNN automatically select the best backend based on Browser type and 
compiled model data on the server.

You can check the backend type

```js
console.log(runner.backendName);
```

![backend](../_static/tutorial/check_backend.png)

Then you can get input and output variable references (`SymbolicFloat32Array` type).

```js
let x = runner.getInputViews()[0];
let y = runner.getOutputViews()[0];
```

That's all for initialization. You only have to do this at once in the application.

Let's classify this image.

![sample image](../_static/tutorial/sample_image.jpeg)

First, set input data.

```js
// loadImageData() returns image data as Float32Array
x.set(loadImageData());
```

Next, run model.

```js
await runner.run();
```

That's all.

Show computed vector and predicted label.

```js
let y_typed_array = y.toActual();
console.log('Computed vector', y_typed_array);
console.log('Predicted Label', WebDNN.Math.argmax(y_typed_array));
```

![result](../_static/tutorial/result.png)

Congratulation! `LabelID:230` is `"Shetland sheepdog"` in ImageNet. It looks work well.
