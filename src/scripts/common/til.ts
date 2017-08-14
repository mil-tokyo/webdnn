// /**
//  * Load an image from <img>
//  *
//  * If no data is loaded in the image element, an error is thrown.
//  *
//  * @param $img video element
//  * @returns {Promise<Int32Array>}
//  */
// async function loadFromImage($img: HTMLImageElement): Promise<Int32Array> {
//     if (!$img.complete) throw Error('Loading image is not completed');
//     const width = $img.naturalWidth;
//     const height = $img.naturalHeight;
//
//     let $canvas = document.createElement('canvas');
//     $canvas.width = width;
//     $canvas.height = height;
//
//     let ctx = $canvas.getContext('2d');
//     if (!ctx) throw Error('Failed to initialize CanvasRenderingContext2D');
//
//     ctx.drawImage($img, 0, 0, width, height);
//     return loadFromCanvas($canvas);
// }
//
// enum HTMLVideoElementReadyState {
//     HAVE_NOTHING = 0,
//     HAVE_METADATA = 1,
//     HAVE_CURRENT_DATA = 2,
//     HAVE_FUTURE_DATA = 3,
//     HAVE_ENOUGH_DATA = 4
// }
//
// /**
//  * Load an image rendered in <canvas>.
//  *
//  * If any cross-origin contents are rendered on the canvas,
//  * The canvas context is marked as 'Cross-origin-content-resource' and
//  * loading the data is blocked. In this case, an error is thrown.
//  *
//  * @param $canvas canvas element
//  * @returns {Promise<Int32Array>}
//  */
// function loadFromCanvas($canvas: HTMLCanvasElement): Promise<Int32Array> {
//     const width = $canvas.width;
//     const height = $canvas.height;
//     let context = $canvas.getContext('2d');
//     if (!context) throw Error('Failed to get canvas 2D context');
//     let source = context.getImageData(0, 0, width, height).data;
//     let destination = new Int32Array(width * height * 3);
//
//     for (let y = 0; y < height; y++) {
//         for (let x = 0; x < width; x++) {
//             destination[(y * width + x) * 3 + 0] = source[(y * width + x) * 4 + 0];
//             destination[(y * width + x) * 3 + 1] = source[(y * width + x) * 4 + 1];
//             destination[(y * width + x) * 3 + 2] = source[(y * width + x) * 4 + 2];
//         }
//     }
//
//     return Promise.resolve(destination);
// }
//
// /**
//  * Load an image of selected in <input type=file>.
//  *
//  * If no image file is selected, an error is thrown.
//  *
//  * @param $input file input element
//  * @returns {Promise<HTMLImageElement>}
//  */
// async function loadFromFileInput($input: HTMLInputElement): Promise<HTMLImageElement> {
//     if (!$input.files || !$input.files[0]) throw Error('No file is selected.');
//     return loadByUrl(URL.createObjectURL($input.files[0]));
// }
//
// /**
//  * Pick an image by dialog, and load selected image.
//  *
//  * In current web standard, the cancel event of the dialog cannot be handled.
//  * Therefore even if user cancel the instruction, no error is thrown and the promise is still pending.
//  * However, when the dialog is re-opened and an image is picked, the previous promise is rejected and
//  * new promise is resolved.
//  *
//  * @returns {Promise<HTMLImageElement>}
//  */
// let lastPromiseRejectHandler: (() => any) | null = null;
//
// async function loadByDialog(): Promise<HTMLImageElement> {
//     if (lastPromiseRejectHandler) lastPromiseRejectHandler();
//
//     let $input = document.createElement('input');
//     $input.type = 'file';
//     $input.multiple = false;
//     $input.accept = 'image/*';
//     $input.style.visibility = 'hidden';
//     $input.style.position = 'absolute';
//     document.body.appendChild($input);
//
//     return new Promise<HTMLImageElement>((resolve, reject) => {
//         $input.onchange = async () => {
//             let $img = await loadFromFileInput($input);
//             document.body.removeChild($input);
//
//             resolve($img);
//         };
//         lastPromiseRejectHandler = () => reject(Error('File loading is canceled'));
//         $input.click();
//     });
// }
//
// /**
//  * Load image of specified url.
//  * @param url the image url
//  * @returns {Promise<HTMLImageElement>}
//  */
// async function loadByUrl(url: string): Promise<HTMLImageElement> {
//     let $img = document.createElement('img');
//     return new Promise<HTMLImageElement>((resolve, reject) => {
//         $img.onerror = reject;
//         $img.onload = () => resolve($img);
//         $img.src = url;
//     });
// }
//
// /**
//  * Draw image data in array buffer into canvas.
//  * @param $canvas <canvas> element
//  * @param source array buffer
//  * @param width image width(default: $canvas.width)
//  * @param height image height(default: $canvas.height)
//  */
// function drawImageArray($canvas: HTMLCanvasElement, source: Float32Array,
//                         width: number = $canvas.width, height: number = $canvas.height) {
//     let destination = new ImageData(width, height);
//     let destinationData = destination.data;
//
//     for (let y = 0; y < height; y++) {
//         for (let x = 0; x < width; x++) {
//             destinationData[(y * width + x) * 4 + 0] = source[(y * width + x) * 3 + 0];
//             destinationData[(y * width + x) * 4 + 1] = source[(y * width + x) * 3 + 1];
//             destinationData[(y * width + x) * 4 + 2] = source[(y * width + x) * 3 + 2];
//             destinationData[(y * width + x) * 4 + 3] = 255;
//         }
//     }
//
//     let context = $canvas.getContext('2d');
//     if (!context) throw Error('Failed to get canvas 2D context');
//     context.putImageData(destination, 0, 0);
// }
//
// const TIL = {
//     loadFromImage,
//     loadFromVideo,
//     loadFromCanvas,
//     loadFromFileInput,
//     loadByDialog,
//     loadByUrl,
//     drawImageArray
// };
//
// export default TIL