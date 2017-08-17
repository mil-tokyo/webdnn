/**
 * @module webdnn/image
 */
/** Don't Remove This comment block */

import { getContext2D } from "./canvas";

/**
 * The rectangle of source position of image
 */
export interface SourceRect {
    srcX?: number,
    srcY?: number,
    srcW?: number,
    srcH?: number,
}

/**
 * The rectangle of destination position of image
 */
export interface DestinationRect {
    dstX?: number,
    dstY?: number,
    dstW?: number,
    dstH?: number
}

/**
 * @protected
 */
export function getImageDataFromCanvas(canvas: HTMLCanvasElement,
                                       options: SourceRect & DestinationRect = {}): ImageData {
    let {
        srcX = 0, srcY = 0, srcW = canvas.width, srcH = canvas.height,
        dstX = 0, dstY = 0
    } = options;
    let {dstW = srcW, dstH = srcH} = options;

    let imageData = getContext2D(canvas).getImageData(srcX, srcY, srcW, srcH);

    if (dstX !== 0 || dstY !== 0 || srcW !== dstW || srcH !== dstH) {
        imageData = cropAndResizeImageData(imageData, {dstX, dstY, dstW, dstH});
    }

    return imageData;
}


/**
 * @protected
 */
export function getImageDataFromDrawable(drawable: HTMLVideoElement | HTMLImageElement,
                                         options: SourceRect & DestinationRect = {}): ImageData {

    let srcW: number, srcH: number;

    if (drawable instanceof HTMLVideoElement) {
        srcW = drawable.videoWidth;
        srcH = drawable.videoHeight;

    } else if (drawable instanceof HTMLImageElement) {
        srcW = drawable.naturalWidth;
        srcH = drawable.naturalHeight;

    } else throw TypeError('Failed to execute "getImageDataFromDrawable(drawable, options)": "drawable" must be an instanceof HTMLVideoElement or HTMLImageElement');

    let {
        srcX = 0, srcY = 0,
        dstX = 0, dstY = 0, dstW = srcW, dstH = srcH
    } = options;
    let canvas = document.createElement('canvas');
    canvas.width = dstX + dstW;
    canvas.height = dstY + dstH;

    let context = getContext2D(canvas);
    context.drawImage(drawable, srcX, srcY, srcW, srcH, dstX, dstY, dstW, dstH);
    return context.getImageData(0, 0, dstX + dstW, dstY + dstH);
}

/**
 * Source rectangle of source image is cropped and then copied into destination rectangle of new image data
 *
 * @param {ImageData} src
 * @param {SourceRect & DestinationRect} options
 * @returns {ImageData}
 * @protected
 */
function cropAndResizeImageData(src: ImageData,
                                options: SourceRect & DestinationRect = {}) {
    let {
        srcX = 0, srcY = 0, srcW = src.width, srcH = src.height,
        dstX = 0, dstY = 0
    } = options;
    let {dstW = srcW, dstH = srcH} = options;

    let canvas1 = document.createElement('canvas');
    canvas1.width = srcW;
    canvas1.height = srcH;
    let context1 = getContext2D(canvas1);
    context1.putImageData(src, -srcX, -srcY);

    let canvas2 = document.createElement('canvas');
    canvas2.width = dstX + dstW;
    canvas2.height = dstY + dstH;
    let context2 = getContext2D(canvas2);
    context2.drawImage(canvas1, 0, 0, srcW, srcH, dstX, dstY, dstW, dstH);

    return context2.getImageData(0, 0, dstX + dstW, dstY + dstH);
}

/**
 * Return canvas `ImageData` object with specified scale.
 *
 * @param {HTMLCanvasElement | HTMLVideoElement | HTMLImageElement} image
 * @param [options] Options
 * @param {number} [options.srcX=0] left position of input clipping rect
 * @param {number} [options.srcY=0] top position of input clipping rect
 * @param {number} [options.srcW=canvas.width] width of input clipping rect
 * @param {number} [options.srcH=canvas.height] height of input clipping rect
 * @param {number} [options.dstW=options.srcW] width of output
 * @param {number} [options.dstH=options.srcH] height of output
 * @returns {ImageData}
 * @protected
 */
export function getImageData(image: HTMLCanvasElement | HTMLVideoElement | HTMLImageElement,
                             options: SourceRect & DestinationRect = {}): ImageData {
    if (image instanceof HTMLCanvasElement) {
        return getImageDataFromCanvas(image, options)

    } else if (image instanceof HTMLVideoElement || image instanceof HTMLImageElement) {
        return getImageDataFromDrawable(image, options);

    } else throw TypeError('Failed to execute "getImageData(image, options)": "image" must be an instance of HTMLCanvasElement, HTMLVideoElement, or HTMLImageElement');
}


/**
 * @protected
 */
export function setImageDataToCanvas(imageData: ImageData,
                                     canvas: HTMLCanvasElement,
                                     options: SourceRect & DestinationRect = {}) {
    let {
        srcX = 0, srcY = 0, srcW = imageData.width, srcH = imageData.height,
        dstX = 0, dstY = 0
    } = options;
    let {dstW = srcW, dstH = srcH} = options;

    if (srcX !== 0 || srcY !== 0 || srcW !== dstW || srcH !== dstH) {
        imageData = cropAndResizeImageData(imageData, {srcX, srcY, srcW, srcH, dstW, dstH});
    }

    getContext2D(canvas).putImageData(imageData, dstX, dstY);
}


