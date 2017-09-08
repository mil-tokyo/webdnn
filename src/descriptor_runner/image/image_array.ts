/**
 * @module webdnn/image
 */
/** Don't Remove This comment block */

import { getContext2D } from "./canvas";
import { Color, Order } from "./enums";
import { DestinationRect, getImageData, setImageDataToCanvas, SourceRect } from "./image_data";
import { loadImageByUrl, loadImageFromFileInput } from "./image_source";

/**
 * @protected
 */
function flatten<T>(arr: ArrayLike<T>) {
    return (arr instanceof Array) ? Array.prototype.concat.apply([], arr.map(arr => flatten(arr))) : arr;
}

/**
 * Option structure of [[webdnn/image.getImageArray|`WebDNN.Image.getImageArray`]]
 */
export interface ImageArrayOption {
    /** Type of packed array */
    type?: { new(length: number): (Float32Array | Int32Array) },

    /** The color format */
    color?: Color,

    /** The data order */
    order?: Order,

    /** Bias value, which is parsed based on [[webdnn/image.ImageArrayOption.order|`order`]] value */
    bias?: number[]

    /** Scale value, which is parsed based on [[webdnn/image.ImageArrayOption.order|`order`]] value */
    scale?: number[]
}

/**
 * Types which are drawable at `HTMLCanvasElement`
 */
export type Drawable = HTMLImageElement | HTMLVideoElement | HTMLCanvasElement | ImageData;

/**
 * All type of image source which `WebDNN.Image` can be handled. For `string`, only the url of image resource is valid.
 */
export type ImageSource = string | HTMLInputElement | Drawable;

/**
 * Get image array as `{Float32 or Int32}ArrayBufferView` from ImageData object.
 *
 * @see getImageArrayFromCanvas
 *
 * @param {ImageData} imageData Canvas ImageData object
 * @param [options] Options
 * @param [options.type=Float32Array] Data type of image array. Valid value is `Float32Array` or `Int32Array`.
 * @param {Color} [options.color=Color.RGB] Color order of image array
 * @param {Order} [options.order=Order.HWC] Data order of image array
 * @param {number[]} [options.bias=[0, 0, 0]] Bias value of image data (`ImageData = ImageArray + bias`). This value is
 * parsed based on `options.order`.
 * @returns {ArrayBufferView} buffer with specified type
 * @protected
 */
export function getImageArrayFromImageData(imageData: ImageData,
                                           options: SourceRect & DestinationRect & ImageArrayOption = {}) {
    let {
        type = Float32Array,
        color = Color.RGB, order = Order.HWC,
        bias = [0, 0, 0], scale = [1, 1, 1]
    } = options;

    const width = imageData.width;
    const height = imageData.height;

    let data = imageData.data;
    let array: Float32Array | Int32Array;
    let biasR: number, biasG: number, biasB: number;
    let scaleR: number, scaleG: number, scaleB: number;

    switch (color) {
        case Color.RGB:
            array = new type(width * height * 3);
            [scaleR, scaleG, scaleB] = scale;
            [biasR, biasG, biasB] = bias;
            switch (order) {
                case Order.HWC:
                    for (let h = 0; h < height; h++) {
                        for (let w = 0; w < width; w++) {
                            array[(h * width + w) * 3 + 0] = (data[(h * width + w) * 4 + 0] - biasR) / scaleR;
                            array[(h * width + w) * 3 + 1] = (data[(h * width + w) * 4 + 1] - biasG) / scaleG;
                            array[(h * width + w) * 3 + 2] = (data[(h * width + w) * 4 + 2] - biasB) / scaleB;
                        }
                    }
                    break;

                case Order.CHW:
                    for (let h = 0; h < height; h++) {
                        for (let w = 0; w < width; w++) {
                            array[(0 * height + h) * width + w] = (data[(h * width + w) * 4 + 0] - biasR) / scaleR;
                            array[(1 * height + h) * width + w] = (data[(h * width + w) * 4 + 1] - biasG) / scaleG;
                            array[(2 * height + h) * width + w] = (data[(h * width + w) * 4 + 2] - biasB) / scaleB;
                        }
                    }
                    break;
            }
            break;

        case Color.BGR:
            array = new type(width * height * 3);
            [biasB, biasG, biasR] = bias;
            [scaleB, scaleG, scaleR] = scale;
            switch (order) {
                case Order.HWC:
                    for (let h = 0; h < height; h++) {
                        for (let w = 0; w < width; w++) {
                            array[(h * width + w) * 3 + 0] = (data[(h * width + w) * 4 + 2] - biasR) / scaleR;
                            array[(h * width + w) * 3 + 1] = (data[(h * width + w) * 4 + 1] - biasG) / scaleG;
                            array[(h * width + w) * 3 + 2] = (data[(h * width + w) * 4 + 0] - biasB) / scaleB;
                        }
                    }
                    break;

                case Order.CHW:
                    for (let h = 0; h < height; h++) {
                        for (let w = 0; w < width; w++) {
                            array[(0 * height + h) * width + w] = (data[(h * width + w) * 4 + 2] - biasR) / scaleR;
                            array[(1 * height + h) * width + w] = (data[(h * width + w) * 4 + 1] - biasG) / scaleG;
                            array[(2 * height + h) * width + w] = (data[(h * width + w) * 4 + 0] - biasB) / scaleB;
                        }
                    }
                    break;
            }
            break;

        case Color.GREY:
            array = new type(width * height);
            [biasB, biasG, biasR] = bias;
            [scaleB, scaleG, scaleR] = scale;
            for (let h = 0; h < height; h++) {
                for (let w = 0; w < width; w++) {
                    let r = (data[(h * width + w) * 4 + 2] - biasR) / scaleR;
                    let g = (data[(h * width + w) * 4 + 1] - biasG) / scaleG;
                    let b = (data[(h * width + w) * 4 + 0] - biasB) / scaleB;
                    array[h * width + w] = 0.2126 * r + 0.7162 * g + 0.0722 * b;
                }
            }
            break;

        default:
            throw Error(`Unknown color format: ${color}`)
    }

    return array
}

/**
 * Get image array from canvas element as `{Float32 or Int32}ArrayBufferView`.
 *
 * @example <caption>Get image data into Float32Array</caption>
 *
 * let array = getImageArrayFromCanvas(canvas);
 *
 * @example <caption>Get image data with rescaling to 224x224</caption>
 *
 * let array = getImageArrayFromCanvas(canvas, { dstW: 224, dstH: 224 });
 *
 * @example <caption>Get image data with considering mean image value normalization</caption>
 *
 * let array = getImageArrayFromCanvas(canvas, { bias: [MEAN_B, MEAN_G, MEAN_R], color: BGR });
 *
 * @param {HTMLCanvasElement} canvas Canvas
 * @param [options] Options
 * @param [options.type=Float32Array] Data type of image array. Valid value is `Float32Array` or `Int32Array`.
 * @param {Color} [options.color=Color.RGB] Color order of image array
 * @param {Order} [options.order=Order.HWC] Data order of image array
 * @param {number} [options.srcX=0] left position of input clipping rect
 * @param {number} [options.srcY=0] top position of input clipping rect
 * @param {number} [options.srcW=canvas.width] width of input clipping rect
 * @param {number} [options.srcH=canvas.height] height of input clipping rect
 * @param {number} [options.dstW=canvas.width] width of output
 * @param {number} [options.dstH=canvas.height] height of output
 * @param {number[]} [options.bias=[0, 0, 0]] Bias value of image data (`ImageData = ImageArray + bias`). This value is
 * parsed based on `options.order`.
 * @returns {ImageData} buffer with specified type
 * @protected
 */
export function getImageArrayFromCanvas(canvas: HTMLCanvasElement,
                                        options: SourceRect & DestinationRect & ImageArrayOption = {}) {
    let {
        type = Float32Array,
        color = Color.RGB, order = Order.HWC,
        srcX = 0, srcY = 0, srcW = canvas.width, srcH = canvas.height,
        dstX = 0, dstY = 0,
        bias = [0, 0, 0], scale = [1, 1, 1]
    } = options;
    let {dstW = srcW, dstH = srcH} = options;

    let imageData = getImageData(canvas, {srcX, srcY, srcW, srcH, dstX, dstY, dstW, dstH});
    return getImageArrayFromImageData(imageData, {type, color, order, bias, scale});
}

/**
 * Get image array from image element as `{Float32 or Int32}ArrayBufferView`.
 *
 * @example <caption>Get image data into Float32Array</caption>
 *
 * let array = getImageArrayFromCanvas(canvas);
 *
 * @example <caption>Get image data with rescaling to 224x224</caption>
 *
 * let array = getImageArrayFromCanvas(canvas, { dstW: 224, dstH: 224 });
 *
 * @example <caption>Get image data with considering mean image value normalization</caption>
 *
 * let array = getImageArrayFromCanvas(canvas, { bias: [MEAN_B, MEAN_G, MEAN_R], color: BGR });
 *
 * @param {HTMLImageElement|HTMLVideoElement} drawable Image
 * @param [options] Options
 * @param [options.type=Float32Array] Data type of image array. Valid value is `Float32Array` or `Int32Array`.
 * @param {Color} [options.color=Color.RGB] Color order of image array
 * @param {Order} [options.order=Order.HWC] Data order of image array
 * @param {number} [options.srcX=0] left position of input clipping rect
 * @param {number} [options.srcY=0] top position of input clipping rect
 * @param {number} [options.srcW=canvas.width] width of input clipping rect
 * @param {number} [options.srcH=canvas.height] height of input clipping rect
 * @param {number} [options.dstW=canvas.width] width of output
 * @param {number} [options.dstH=canvas.height] height of output
 * @param {number[]} [options.bias=[0, 0, 0]] Bias value of image data (`ImageData = ImageArray + bias`). This value is
 * parsed based on `options.order`.
 * @returns {ImageData} buffer with specified type
 * @protected
 */
export function getImageArrayFromDrawable(drawable: Drawable,
                                          options: SourceRect & DestinationRect & ImageArrayOption = {}) {
    let srcW: number, srcH: number;

    if (drawable instanceof HTMLVideoElement) {
        srcW = drawable.videoWidth;
        srcH = drawable.videoHeight;

    } else if (drawable instanceof HTMLImageElement) {
        srcW = drawable.naturalWidth;
        srcH = drawable.naturalHeight;

    } else if (drawable instanceof HTMLCanvasElement) {
        return getImageArrayFromCanvas(drawable, options)

    } else if (drawable instanceof ImageData) {
        return getImageArrayFromImageData(drawable, options)

    } else throw TypeError('Failed to execute "getImageDataFromDrawable(drawable, options)": "drawable" must be an instanceof Drawable');

    let {
        type = Float32Array,
        color = Color.RGB, order = Order.HWC,
        srcX = 0, srcY = 0,
        dstX = 0, dstY = 0, dstW = srcW, dstH = srcH,
        bias = [0, 0, 0], scale = [1, 1, 1]
    } = options;

    let canvas = document.createElement('canvas');
    canvas.width = dstX + dstW;
    canvas.height = dstY + dstH;

    let context = getContext2D(canvas);
    context.drawImage(drawable, srcX, srcY, srcW, srcH, dstX, dstY, dstW, dstH);

    return getImageArrayFromCanvas(canvas, {type, color, order, bias, scale});
}

/**
 * Create typed array by packing image data from image source with specified options.
 *
 * First, this method loads specified image resource. The behavior of this method depends on the `image` argument.
 *
 * - If `image` is an instance of `string`, it will be regarded as image url, and this method fetches that url.
 *
 * - If `image` is an instance of `HTMLInputElement`, it will be regarded as file inpu,
 *   and this method loads the selected image file.
 *
 * - Otherwise, `image` will be regarded as drawable object.
 *
 * Then, loaded images are packed into typed array based on `options` argument.
 *
 * - The image is cropped based on [[SourceRect|`{srcX, srcY, srcW, srcH}`]].
 *   As default, entire image is used.
 *
 * - The image is resized and translated into [[DestinationRect|`{dstX, dstY, dstW, dstH}`]].
 *   As default, no resize and translation is performed.
 *
 * - [[ImageArrayOption.type|`options.type`]] is the type of packed typed array. As default, Float32Array is used.
 *
 * - [[ImageArrayOption.type|`options.color`]] is the color format of packed typed array. As default, [[Color.RGB|`RGB`]] is used.
 *
 * - [[ImageArrayOption.type|`options.order`]] is the data order of packed typed array. As default, [[Order.HWC|`HWC`]] is used.
 *
 * - [[ImageArrayOption.bias|`options.bias`]] is the bias value.
 *   If specified, this method **subtracts** this value from original pixel value.
 *
 * - [[ImageArrayOption.scale|`options.scale`]] is the scale value. If specified, original pixel values are **divided** by this value.
 *   [[ImageArrayOption.scale|`options.scale`]] and [[ImageArrayOption.bias|`options.bias`]] is used for converting pixel value `x` and
 *   packed value `y` as follows:
 *
 *   - `y = (x - bias) / scale`
 *   - `x= y * scale + bias`
 *
 * ### Examples
 *
 * - Load image of specified url
 *
 *   ```ts
 *   let image = await WebDNN.Image.load('./cat.png');
 *   ```
 *
 * - Load image selected in file input and resize it into 224 x 224
 *
 *   ```ts
 *   let input = document.querySelector('input[type=file]');
 *   let image = await WebDNN.Image.load(input, { dstW: 224, dstH: 224 });
 *   ```
 *
 * - Load image data from canvas, normalize it into range `[-1, 1)`. In this case, normalized value `y` can be
 *   calculated from pixel value `x` as follows: `y = (x - 128) / 128`.
 *
 *   ```ts
 *   let canvas = document.getElementsByTagName('canvas')[0];
 *   let image = await WebDNN.Image.load(canvas, { bias: [128, 128, 128], scale: [128, 128, 128] });
 *   ```
 *
 * @param image please see above descriptions
 * @param options please see above descriptions.
 * @returns Created typed array
 */
export async function getImageArray(image: ImageSource,
                                    options: SourceRect & DestinationRect & ImageArrayOption = {}) {
    if (typeof image === 'string') {
        return getImageArrayFromDrawable(await loadImageByUrl(image), options);

    } else if (image instanceof HTMLInputElement) {
        return getImageArrayFromDrawable(await loadImageFromFileInput(image), options);

    } else if (image instanceof HTMLCanvasElement) {
        return getImageArrayFromCanvas(image, options)

    } else if (image instanceof HTMLImageElement || image instanceof HTMLVideoElement) {
        return getImageArrayFromDrawable(image, options);

        // FIXME: This feature is not supported for all web browsers.
        // } else if (image === null) {
        //     return getImageArrayFromDrawable(await loadImageByDialog(), options);

    } else throw TypeError('Failed to execute "getImageData(image, options)": "image" must be an instance of string,' +
        ' HTMLInputElement, HTMLCanvasElement, HTMLImageElement, or HTMLVideoElement object');
}

/**
 * Set image array data into canvas.
 *
 * ### Examples
 *
 * - Show DNN model's result
 *
 *   ```ts
 *   let runner = await WebDNN.load('./model');
 *   let output = runner.getOutputViews()[0];
 *
 *   await runner.run();
 *
 *   WebDNN.Image.setImageArrayToCanvas(output.toActual(), 256, 256, document.getElementById('canvas'))
 *   ```
 *
 * - Generally image generation model's result contains noise pixel at their edge because of convolution's padding.
 *   In follow example, these noise are cut off.
 *
 *   ```ts
 *   WebDNN.Image.setImageArrayToCanvas(output, 256, 256, canvas, {
 *      srcX: 16, srcY: 16, srcH: 256-16*2, srcW: 256-16*2, // Discard both ends 16px
 *      dstW: 256, dstH: 256  // Resize cropped image into original output size.
 *   });
 *   ```
 *
 * @param array array which contains image data
 * @param imageW width of image
 * @param imageH height of image. The length of `array` must be `imageW * imageH * (# of channels)`
 * @param canvas destination canvas
 * @param options please see above descriptions and descriptions in [[webdnn/image.getImageArray|getImageArray()]].
 */
export function setImageArrayToCanvas(array: Float32Array | Int32Array,
                                      imageW: number,
                                      imageH: number,
                                      canvas: HTMLCanvasElement,
                                      options: SourceRect & DestinationRect & ImageArrayOption = {}) {
    let {
        color = Color.RGB, order = Order.HWC,
        srcX = 0, srcY = 0, srcW = imageW, srcH = imageH,
        dstX = 0, dstY = 0, dstW = canvas.width, dstH = canvas.height,
        bias = [0, 0, 0], scale = [1, 1, 1]
    } = options;

    array = flatten(array);
    let data = new Uint8ClampedArray(srcW * srcH * 4);
    let biasR: number, biasG: number, biasB: number;
    let scaleR: number, scaleG: number, scaleB: number;

    switch (color) {
        case Color.RGB:
            [biasR, biasG, biasB] = bias;
            [scaleR, scaleG, scaleB] = scale;
            switch (order) {
                case Order.HWC:
                    for (let h = srcY; h < srcY + srcH; h++) {
                        for (let w = srcX; w < srcX + srcW; w++) {
                            data[(h * imageW + w) * 4 + 0] = array[(h * imageW + w) * 3 + 0] * scaleR + biasR;
                            data[(h * imageW + w) * 4 + 1] = array[(h * imageW + w) * 3 + 1] * scaleG + biasG;
                            data[(h * imageW + w) * 4 + 2] = array[(h * imageW + w) * 3 + 2] * scaleB + biasB;
                            data[(h * imageW + w) * 4 + 3] = 255;
                        }
                    }
                    break;

                case Order.CHW:
                    for (let h = srcY; h < srcY + srcH; h++) {
                        for (let w = srcX; w < srcX + srcW; w++) {
                            data[(h * imageW + w) * 4 + 0] = array[(0 * imageH + h) * imageW + w] * scaleR + biasR;
                            data[(h * imageW + w) * 4 + 1] = array[(1 * imageH + h) * imageW + w] * scaleG + biasG;
                            data[(h * imageW + w) * 4 + 2] = array[(2 * imageH + h) * imageW + w] * scaleB + biasB;
                            data[(h * imageW + w) * 4 + 3] = 255;
                        }
                    }
                    break;
            }
            break;

        case Color.BGR:
            [biasB, biasG, biasR] = bias;
            [scaleB, scaleG, scaleR] = scale;
            switch (order) {
                case Order.HWC:
                    for (let h = srcY; h < srcY + srcH; h++) {
                        for (let w = srcX; w < srcX + srcW; w++) {
                            data[(h * imageW + w) * 4 + 0] = array[(h * imageW + w) * 3 + 2] * scaleR + biasR;
                            data[(h * imageW + w) * 4 + 1] = array[(h * imageW + w) * 3 + 1] * scaleG + biasG;
                            data[(h * imageW + w) * 4 + 2] = array[(h * imageW + w) * 3 + 0] * scaleB + biasB;
                            data[(h * imageW + w) * 4 + 3] = 255;
                        }
                    }
                    break;

                case Order.CHW:
                    for (let h = srcY; h < srcY + srcH; h++) {
                        for (let w = srcX; w < srcX + srcW; w++) {
                            data[(h * imageW + w) * 4 + 0] = array[(2 * imageH + h) * imageW + w] * scaleR + biasR;
                            data[(h * imageW + w) * 4 + 1] = array[(1 * imageH + h) * imageW + w] * scaleG + biasG;
                            data[(h * imageW + w) * 4 + 2] = array[(0 * imageH + h) * imageW + w] * scaleB + biasB;
                            data[(h * imageW + w) * 4 + 3] = 255;
                        }
                    }
                    break;
            }
            break;

        case Color.GREY:
            [biasR, biasG, biasB] = bias;
            [scaleR, scaleG, scaleB] = scale;
            for (let h = srcY; h < srcY + srcH; h++) {
                for (let w = srcX; w < srcX + srcW; w++) {
                    data[(h * imageW + w) * 4 + 0] =
                        data[(h * imageW + w) * 4 + 1] =
                            data[(h * imageW + w) * 4 + 2] = array[h * imageW + w] * scaleR + biasR;
                    data[(h * imageW + w) * 4 + 3] = 255;
                }
            }
            break;
    }

    setImageDataToCanvas(new ImageData(data, srcW, srcH), canvas, {srcX, srcY, srcW, srcH, dstX, dstY, dstW, dstH});
}
