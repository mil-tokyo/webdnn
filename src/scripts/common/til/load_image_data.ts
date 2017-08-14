enum HTMLVideoElementReadyState {
    HAVE_NOTHING = 0,
    HAVE_METADATA = 1,
    HAVE_CURRENT_DATA = 2,
    HAVE_FUTURE_DATA = 3,
    HAVE_ENOUGH_DATA = 4
}

/**
 * Load image data rendered in <canvas>.
 *
 * If any cross-origin contents are rendered on the canvas,
 * The canvas context is marked as 'Cross-origin-content-resource' and
 * loading the data is blocked. In this case, an error is thrown.
 *
 * @param $canvas canvas element
 * @returns {Promise<Uint8Array>}
 */
export function loadImageDataFromCanvas($canvas: HTMLCanvasElement): Uint8Array {
    const width = $canvas.width;
    const height = $canvas.height;
    let context = $canvas.getContext('2d');
    if (!context) throw Error('Failed to get canvas 2D context');
    let source = context.getImageData(0, 0, width, height).data;
    let destination = new Uint8Array(width * height * 3);

    for (let y = 0; y < height; y++) {
        for (let x = 0; x < width; x++) {
            destination[(y * width + x) * 3 + 0] = source[(y * width + x) * 4 + 0];
            destination[(y * width + x) * 3 + 1] = source[(y * width + x) * 4 + 1];
            destination[(y * width + x) * 3 + 2] = source[(y * width + x) * 4 + 2];
        }
    }

    return destination;
}

/**
 * Load an image from <video>
 *
 * If no data is loaded in the video element, an error is thrown.
 *
 * @param $video video element
 * @returns {UInt8Array}
 */
export function loadImageDataFromVideo($video: HTMLVideoElement): Uint8Array {
    if ($video.readyState == HTMLVideoElementReadyState.HAVE_NOTHING ||
        $video.readyState == HTMLVideoElementReadyState.HAVE_METADATA) throw Error('Video buffer is not loaded enough');

    const width = $video.videoWidth;
    const height = $video.videoHeight;

    let $canvas = document.createElement('canvas');
    $canvas.width = width;
    $canvas.height = height;

    let ctx = $canvas.getContext('2d');
    if (!ctx) throw Error('Failed to initialize CanvasRenderingContext2D');

    ctx.drawImage($video, 0, 0, width, height);
    return loadImageDataFromCanvas($canvas);
}

