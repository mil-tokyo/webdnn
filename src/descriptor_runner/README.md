## Overview

WebDNN JavaScript API is consisted of main module ([[webdnn|`WebDNN`]]) and support modules 
[[webdnn/math|`WebDNN.Math`]], [[webdnn/image|`WebDNN.Image`]]).

You can use this API by follow two usage.

- Use with `import` syntax

    ```js
    // index.js
    import * as WebDNN from "webdnn"
    
    let runner = WebDNN.load('./model');
    ```

- Use with `<script>` tag

    ```html
    <!-- index.html -->
    <script src="./webdnn.js"></script>
    <script>
        WebDNN.load('./model');
    </script>
    ```

Support libraries are also loaded when main module is loaded.

## Basic Example

First, load your model by [[webdnn.load|`WebDNN.load`]]. This function load your model asynchronously. 
Therefore you have to use ES2016 async/await syntax or promise syntax.

```ts
// ES2016
let runner = await WebDNN.load('./model');
```

```ts
// ES2015
WebDNN.load('./model')
    .then(function(runner) { /* do something */ });
```

Then you can get [[webdnn.DescriptorRunner|`DescriptorRunner`]] instance, which executes your model.
Runner also provides interface of input and output buffers. You can read and write data through this interface.

For example, load image data by using [[webdnn/image.getImageArray|`WebDNN.Image.getImageArray()`]] and set it into 
input buffer.

```ts
// ES2016
let imageArray = await WebDNN.Image.getImageArray(); // Load image RGB data as Float32Array
runner.getInputViews()[0].set(imageArray); // Write data
```

```ts
// ES2015
WebDNN.Image.getImageArray()
    .then(function(imageArray) { runner.getInputViews()[0].set(imageArray) });
```

Also you can access the output buffer.

```ts
let result = runner.getOutputViews()[0];
```

Finally, run inference!

```ts
// ES2016
await runner.run();
```

```ts
// ES2015
runner.run()
    .then(function() { /* do something */ });
```

Because [[webdnn.DescriptorRunner.getOutputViews|`DescriptorRunner.getOutputViews()`]] returns 
[[webdnn.SymbolicTypedArray|`SymbolicTypedArray`]], which is not actual typed array, 
you need to convert it into actual typed array by using [[webdnn.SymbolicTypedArray.toActual|`SymbolicTypedArray.toActual()`]].

```ts
console.log(result.toActual());
``` 
