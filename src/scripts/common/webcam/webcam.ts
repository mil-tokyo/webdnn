const SHOCKWAVE_FLASH = 'Shockwave Flash';
const SHOCKWAVE_FLASH_AX = 'ShockwaveFlash.ShockwaveFlash';
const FLASH_MIME_TYPE = 'application/x-shockwave-flash';

declare function require(path: string): any;

class FlashError extends Error {
    constructor(message: string) {
        super(message);
    }
}

const protocol: string = location.protocol.match(/https/i) ? 'https' : 'http';
const flagIOS: boolean = /iPad|iPhone|iPod/.test(navigator.userAgent) && !('MSStream' in window);
let flagWebCamInitialized: boolean = false;
let flagFlashDetected: boolean = false;

let getUserMedia: typeof navigator.mediaDevices.getUserMedia | null;
let URL: typeof window.URL | null;

function getContext2D($canvas: HTMLCanvasElement) {
    let ctx = $canvas.getContext('2d');
    if (!ctx) throw new Error('CanvasRenderingContext2D initialization failed.');
    return ctx!;
}

interface FlashCustomHTMLObjectElement extends HTMLObjectElement {
    _snap: any
    _releaseCamera: any
}

function init() {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        getUserMedia = (constraints: MediaStreamConstraints) => navigator.mediaDevices.getUserMedia(constraints);
    } else if ('mozGetUserMedia' in navigator) {
        getUserMedia = (constraints: MediaStreamConstraints) => (navigator as any).mozGetUserMedia(constraints)
    } else if ('webkitGetUserMedia' in navigator) {
        getUserMedia = (constraints: MediaStreamConstraints) => (navigator as any).webkitGetUserMedia(constraints)
    }

    if ('URL' in window) {
        URL = window.URL;
    } else if ('webkitURL' in window) {
        URL = (window as any).webkitURL;
    } else if ('mozURL' in window) {
        URL = (window as any).mozURL;
    } else if ('msURL' in window) {
        URL = (window as any).msURL;
    }

    // Older versions of firefox (< 21) apparently claim support but user media does not actually work
    if (navigator.userAgent.match(/Firefox\D+(\d+)/) && parseInt(RegExp.$1, 10) < 21) getUserMedia = null;

    if (typeof navigator.plugins === 'object' &&
        typeof (navigator.plugins as any)[SHOCKWAVE_FLASH] === 'object' &&
        (navigator.plugins as any)[SHOCKWAVE_FLASH].description &&
        typeof navigator.mimeTypes === 'object' &&
        (navigator.mimeTypes as any)[FLASH_MIME_TYPE] &&
        (navigator.mimeTypes as any)[FLASH_MIME_TYPE].enabledPlugin) {

        flagFlashDetected = true;

    } else if ('ActiveXObject' in window) {
        try {
            let activeX = new (window as any).ActiveXObject(SHOCKWAVE_FLASH_AX);
            if (activeX && activeX.GetVariable('$version')) flagFlashDetected = true;
        }
        catch (e) { /* ActiveX is not supported */ }
    }

    flagWebCamInitialized = true;
}

function exifOrientation(binFile: ArrayBuffer) {
    let dataView = new DataView(binFile);
    if ((dataView.getUint8(0) != 0xFF) || (dataView.getUint8(1) != 0xD8)) {
        console.log('Not a valid JPEG file');
        return 0;
    }
    let offset = 2;
    let marker = null;
    while (offset < binFile.byteLength) {
        // find 0xFFE1 (225 marker)
        if (dataView.getUint8(offset) != 0xFF) {
            console.log('Not a valid marker at offset ' + offset + ', found: ' + dataView.getUint8(offset));
            return 0;
        }
        marker = dataView.getUint8(offset + 1);
        if (marker == 225) {
            offset += 4;
            let str = "";
            for (let n = 0; n < 4; n++) {
                str += String.fromCharCode(dataView.getUint8(offset + n));
            }
            if (str != 'Exif') {
                console.log('Not valid EXIF data found');
                return 0;
            }

            offset += 6; // tiffOffset
            let bigEnd = null;

            // test for TIFF validity and endianness
            if (dataView.getUint16(offset) == 0x4949) {
                bigEnd = false;
            } else if (dataView.getUint16(offset) == 0x4D4D) {
                bigEnd = true;
            } else {
                console.log("Not valid TIFF data! (no 0x4949 or 0x4D4D)");
                return 0;
            }

            if (dataView.getUint16(offset + 2, !bigEnd) != 0x002A) {
                console.log("Not valid TIFF data! (no 0x002A)");
                return 0;
            }

            let firstIFDOffset = dataView.getUint32(offset + 4, !bigEnd);
            if (firstIFDOffset < 0x00000008) {
                console.log("Not valid TIFF data! (First offset less than 8)", dataView.getUint32(offset + 4, !bigEnd));
                return 0;
            }

            // extract orientation data
            let dataStart = offset + firstIFDOffset;
            let entries = dataView.getUint16(dataStart, !bigEnd);
            for (let i = 0; i < entries; i++) {
                let entryOffset = dataStart + i * 12 + 2;
                if (dataView.getUint16(entryOffset, !bigEnd) == 0x0112) {
                    let valueType = dataView.getUint16(entryOffset + 2, !bigEnd);
                    let numValues = dataView.getUint32(entryOffset + 4, !bigEnd);
                    if (valueType != 3 && numValues != 1) {
                        console.log('Invalid EXIF orientation value type (' + valueType + ') or count (' + numValues + ')');
                        return 0;
                    }
                    let value = dataView.getUint16(entryOffset + 8, !bigEnd);
                    if (value < 1 || value > 8) {
                        console.log('Invalid EXIF orientation value (' + value + ')');
                        return 0;
                    }
                    return value;
                }
            }
        } else {
            offset += 2 + dataView.getUint16(offset + 2);
        }
    }
    return 0;
}

function fixOrientation(origObjURL: string, orientation: number, targetImg: HTMLImageElement) {
    let img = new Image();
    img.addEventListener('load', () => {
        let canvas = document.createElement('canvas');
        let ctx = canvas.getContext('2d');
        if (!ctx) throw Error('null');

        if (orientation < 5) {
            canvas.width = img.width;
            canvas.height = img.height;

        } else {
            //noinspection JSSuspiciousNameCombination
            canvas.width = img.height;
            //noinspection JSSuspiciousNameCombination
            canvas.height = img.width;
        }

        switch (orientation) {
            case 2:
                ctx.transform(-1, 0, 0, 1, img.width, 0);
                break;
            case 3:
                ctx.transform(-1, 0, 0, -1, img.width, img.height);
                break;
            case 4:
                ctx.transform(1, 0, 0, -1, 0, img.height);
                break;
            case 5:
                ctx.transform(0, 1, 1, 0, 0, 0);
                break;
            case 6:
                ctx.transform(0, 1, -1, 0, img.height, 0);
                break;
            case 7:
                ctx.transform(0, -1, -1, 0, img.height, img.width);
                break;
            case 8:
                ctx.transform(0, -1, 1, 0, 0, img.width);
                break;
        }

        ctx.drawImage(img, 0, 0);
        // pass rotated image data to the target image container
        targetImg.src = canvas.toDataURL();
    }, false);
    // start transformation by load event
    img.src = origObjURL;
}

let defaultParams: { [key: string]: any } = {
    width: 0,
    height: 0,
    destWidth: 0,         // size of captured image
    destHeight: 0,        // these default to width/height
    imageFormat: 'png',  // image format (may be jpeg or png)
    jpegQuality: 90,      // jpeg image quality from 0 (worst) to 100 (best)
    flagFlashEnable: true,    // enable flash fallback,
    flagForceFlash: false,    // force flash mode,
    fps: 30,               // camera frames per second
    constraints: null,     // custom user media constraints,
    swfURL: require('./webcam.swf'),            // URI to webcam.swf movie (defaults to the js location)
    flagUnfreezeSnap: true,    // Whether to unfreeze the camera after snap (defaults to true)
};

export default class WebCam {
    private $container: HTMLElement | null = null;
    private $peg: HTMLDivElement | null = null;
    private $previewCanvas: HTMLCanvasElement | null = null;
    private previewContext: CanvasRenderingContext2D | null = null;
    private $video: HTMLVideoElement | null = null;
    private onFlashLive: (() => any) | null;
    private onFlashError: ((err: Error) => any) | null;
    flagFlashMovieLoaded: boolean = false;
    flagFlashLive: boolean = false;
    flagPreviewIsActive: boolean;
    flagUserMedia: boolean;
    flagUseUserMedia: boolean = false;
    onBeforeUnload: () => void;
    params: typeof defaultParams;

    constructor(params: typeof defaultParams) {
        if (!flagWebCamInitialized) init();

        this.params = Object.assign({}, defaultParams, params);
        this.flagUserMedia = !this.params.flagForceFlash && !!getUserMedia && !!window.URL;
        if (this.flagUserMedia) {
            this.onBeforeUnload = () => this.reset();
            window.addEventListener('beforeunload', this.onBeforeUnload);
        }
    }

    async attachAsync($container: HTMLElement | string): Promise<void> {
        if (typeof($container) == 'string') $container = document.querySelector($container) as HTMLElement;
        if (!$container) throw new Error("Could not locate DOM element to attach to.");
        this.$container = $container;
        this.$container.innerHTML = '';

        // insert "peg" so we can insert our preview canvas adjacent to it later on
        let $peg = document.createElement('div');
        $container.appendChild($peg);
        this.$peg = $peg;

        // set width/height if not already set
        if (!this.params.width) this.params.width = $container.offsetWidth;
        if (!this.params.height) this.params.height = $container.offsetHeight;
        if (!this.params.width || !this.params.height) throw new Error("No width and/or height for webcam.  Please call set() first, or attach to a visible element.");

        // set defaults for destWidth / destHeight if not set
        if (!this.params.destWidth) this.params.destWidth = this.params.width;
        if (!this.params.destHeight) this.params.destHeight = this.params.height;

        // check for default fps
        if (typeof this.params.fps !== "number") this.params.fps = 30;

        // adjust scale if destWidth or destHeight is different
        let scaleX = this.params.width / this.params.destWidth;
        let scaleY = this.params.height / this.params.destHeight;

        if (this.flagUserMedia && !this.params.flagForceFlash) {
            let $video = document.createElement('video') as HTMLVideoElement;
            $video.setAttribute('autoplay', 'autoplay');
            $video.style.width = `${this.params.destWidth}px`;
            $video.style.height = `${this.params.destHeight}px`;
            if ((scaleX != 1.0) || (scaleY != 1.0)) {
                this.$container.style.overflow = 'hidden';
                $video.style.transformOrigin = '0px 0px';
                $video.style.transform = 'scaleX(' + scaleX + ') scaleY(' + scaleY + ')';
            }
            this.$video = $video;
            this.$container.appendChild($video);

            try {
                let stream: MediaStream = await getUserMedia!({
                    'audio': false,
                    'video': true
                });

                return await (new Promise<void>((resolve, reject) => {
                    $video.addEventListener('loadedmetadata', () => {
                        this.flagFlashMovieLoaded = true;
                        this.flagFlashLive = true;

                        resolve();
                    });
                    $video.addEventListener('error', err => reject(err));
                    $video.srcObject = stream;
                }));

            } catch (err) {
                if (this.$container && flagFlashDetected) {
                    console.warn('This browser supports WebRTC, but initialization is failed.');
                    console.warn(err);
                    console.warn('WebCam.ts retries initialization with flash fallback.');
                    this.params.flagForceFlash = true;
                    return this.attachAsync(this.$container);

                } else {
                    throw err;
                }
            }

        } else if (flagIOS) {
            let $div = document.createElement('div') as HTMLDivElement;
            $div.id = this.$container.id + '-ios_div';
            $div.style.width = '' + this.params.width + 'px';
            $div.style.height = '' + this.params.height + 'px';
            $div.style.textAlign = 'center';
            $div.style.display = 'table-cell';
            $div.style.verticalAlign = 'middle';
            $div.style.backgroundRepeat = 'no-repeat';
            $div.style.backgroundSize = 'contain';
            $div.style.backgroundPosition = 'center';

            let $span = document.createElement('span') as HTMLSpanElement;
            $span.id = this.$container.id + '-ios_span';
            $span.innerHTML = 'Tap here to open camera.';
            $div.appendChild($span);

            let $img = document.createElement('img') as HTMLImageElement;
            $img.id = this.$container.id + '-ios_$img';
            $img.style.width = '' + this.params.destWidth + 'px';
            $img.style.height = '' + this.params.destHeight + 'px';
            $img.style.display = 'none';
            $div.appendChild($img);

            let $input = document.createElement('input') as HTMLInputElement;
            $input.id = this.$container.id + '-ios_$input';
            $input.setAttribute('type', 'file');
            $input.setAttribute('accept', 'image/*');
            $input.setAttribute('capture', 'camera');

            // add input listener to load the selected image
            $input.addEventListener('change', () => {
                if (!$input || !$input.files) return;
                if ($input.files.length > 0 && $input.files[0].type.indexOf('image/') == 0) {
                    let objURL = URL!.createObjectURL($input.files[0]);

                    // load image with auto scale and crop
                    let image = new Image();
                    image.addEventListener('load', () => {
                        let $canvas = document.createElement('canvas');
                        $canvas.width = this.params.destWidth;
                        $canvas.height = this.params.destHeight;
                        let ctx = $canvas.getContext('2d');
                        if (!ctx) throw Error('Canvas initialization is failed.');

                        let ratio = Math.min(image.width / this.params.destWidth, image.height / this.params.destHeight);
                        let sw = this.params.destWidth * ratio;
                        let sh = this.params.destHeight * ratio;
                        let sx = (image.width - sw) / 2;
                        let sy = (image.height - sh) / 2;
                        ctx.drawImage(image, sx, sy, sw, sh, 0, 0, this.params.destWidth, this.params.destHeight);

                        let dataURL = $canvas.toDataURL();
                        $img.src = dataURL;
                        $div.style.backgroundImage = "url('" + dataURL + "')";
                    }, false);

                    // read EXIF data
                    let fileReader = new FileReader();
                    fileReader.addEventListener('load', () => {
                        let orientation = exifOrientation(fileReader.result);
                        if (orientation > 1) {
                            // image need to rotate (see comments on fixOrientation method for more information)
                            // transform image and load to image object
                            fixOrientation(objURL, orientation, image);
                        } else {
                            image.src = objURL;
                        }
                    }, false);

                    // Convert image data to blob format
                    let xhr = new XMLHttpRequest();
                    xhr.open("GET", objURL, true);
                    xhr.responseType = "blob";
                    xhr.onload = () => {
                        if (xhr.status == 200 || xhr.status === 0) {
                            fileReader.readAsArrayBuffer(xhr.response);
                        }
                    };
                    xhr.send();
                }
            }, false);
            $input.style.display = 'none';
            $container.appendChild($input);

            // make div clickable for open camera interface
            $div.addEventListener('click', () => {
                $input.style.display = 'block';
                $input.focus();
                $input.click();
                $input.style.display = 'none';
            }, false);
            $container.appendChild($div);

            this.flagFlashMovieLoaded = true;
            this.flagFlashLive = true;

        } else if (this.params.flagFlashEnable && flagFlashDetected) {
            (window as any)['Webcam'] = this;
            let $div = document.createElement('div');

            return await new Promise<void>((resolve, reject) => {
                this.onFlashLive = () => {
                    this.onFlashLive = this.onFlashError = null;
                    resolve();
                };
                this.onFlashError = (err: Error) => {
                    this.onFlashLive = this.onFlashError = null;
                    reject(err);
                };

                $div.innerHTML = this.getSWFHTML();
                this.$container!.appendChild($div);
            });

        } else {
            throw new Error('No WebCam interface is detected.');
        }

        $container.style.width = '' + this.params.width + 'px';
        $container.style.height = '' + this.params.height + 'px';
    }

    reset() {
        if (this.flagPreviewIsActive) this.unfreeze();
        if (this.flagUseUserMedia) this.$video = null;

        if (this.flagUseUserMedia && this.flagFlashMovieLoaded && !flagIOS) {
            let movie = this.getMovie();
            if (movie && '_releaseCamera' in movie) movie._releaseCamera();
        }

        if (this.$container) {
            this.$container.innerHTML = '';
            this.$container = null;
        }

        this.flagFlashMovieLoaded = false;
        this.flagFlashLive = false;
    }

    getSWFHTML() {
        if (!flagFlashDetected) throw new FlashError('Adobe Flash Player not found. Please install from get.adobe.com/flashplayer and try again.');

        let flashVars = Object.keys(this.params)
            .map(key => `${key}=${encodeURIComponent(this.params[key])}`)
            .join('&');

        return `<object classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000" type="application/x-shockwave-flash" codebase="${protocol}://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=9,0,0,0" width="${this.params.width}" height="${this.params.height}" id="webcam_movie_obj" align="middle"><param name="wmode" value="opaque" /><param name="allowScriptAccess" value="always" /><param name="allowFullScreen" value="false" /><param name="movie" value="${this.params.swfURL}" /><param name="loop" value="false" /><param name="menu" value="false" /><param name="quality" value="best" /><param name="bgcolor" value="#ffffff" /><param name="flashvars" value="${flashVars}" /><embed id="webcam_movie_embed" src="${this.params.swfURL}" wmode="opaque" loop="false" menu="false" quality="best" bgcolor="#ffffff" width="${this.params.width}" height="${this.params.height}" name="webcam_movie_embed" align="middle" allowScriptAccess="always" allowFullScreen="false" type="application/x-shockwave-flash" pluginspage="http://www.macromedia.com/go/getflashplayer" flashvars="${flashVars}"></embed></object>`;
    }

    getMovie() {
        if (!this.flagFlashMovieLoaded) throw new FlashError('Flash Movie is not loaded yet');

        let movie: FlashCustomHTMLObjectElement | null;

        movie = document.getElementById('webcam_movie_obj') as FlashCustomHTMLObjectElement;
        if (!movie || !movie._snap) movie = document.getElementById('webcam_movie_embed') as FlashCustomHTMLObjectElement;
        if (!movie) throw new FlashError('Cannot locate Flash movie in DOM');

        return movie;
    }

    async freezeAsync() {
        if (!this.$container) throw new Error('$container is null.');
        if (this.flagPreviewIsActive) this.unfreeze();

        let $previewCanvas: HTMLCanvasElement;

        if (!this.$previewCanvas) {
            let finalWidth = this.params.destWidth;
            let finalHeight = this.params.destHeight;

            $previewCanvas = document.createElement('canvas');
            $previewCanvas.width = finalWidth;
            $previewCanvas.height = finalHeight;

            let scaleX = this.params.width / this.params.destWidth;
            let scaleY = this.params.height / this.params.destHeight;
            if ((scaleX != 1.0) || (scaleY != 1.0)) {
                $previewCanvas.style.transformOrigin = '0px 0px';
                $previewCanvas.style.transform = 'scaleX(' + scaleX + ') scaleY(' + scaleY + ')';
            }

            this.$previewCanvas = $previewCanvas;
        } else {
            $previewCanvas = this.$previewCanvas;
        }

        // copy camera source into preview canvas
        if (getUserMedia) {
            if (!this.$video) throw Error('video is null');
            getContext2D(this.$previewCanvas).drawImage(this.$video, 0, 0, this.params.destWidth, this.params.destHeight);

        } else if (flagIOS) {
            if (!this.$container) throw Error('Not initialized yet');

            let div = document.getElementById(this.$container.id + '-ios_div') as HTMLDivElement;
            let input = document.getElementById(this.$container.id + '-ios_input') as HTMLInputElement;
            let image = document.getElementById(this.$container.id + '-ios_img') as HTMLImageElement;
            if (!div || !image || !input) throw Error('null');

            if (!input.value) {
                // No image selected yet, activate input field
                await new Promise<void>((resolve, reject) => {
                    image.onload = () => {
                        getContext2D($previewCanvas).drawImage(image, 0, 0, this.params.destWidth, this.params.destHeight);
                        resolve();
                    };
                    image.onerror = err => reject(err);

                    input.style.display = 'block';
                    input.focus();
                    input.click();
                    input.style.display = 'none';

                    div.style.backgroundImage = 'none';
                    image.removeAttribute('src');
                    input.value = '';
                });

            } else {
                // Image already selected
                getContext2D($previewCanvas).drawImage(image, 0, 0, this.params.destWidth, this.params.destHeight);

                div.style.backgroundImage = 'none';
                image.removeAttribute('src');
                input.value = '';
            }

        } else {
            let image = new Image();
            await new Promise<void>((resolve, reject) => {
                image.onload = () => {
                    getContext2D($previewCanvas).drawImage(image, 0, 0, this.params.destWidth, this.params.destHeight);
                    resolve();
                };
                image.onerror = err => reject(err);
                image.src = 'data:image/png;base64,' + this.getMovie()!._snap();
            });
        }

        this.$previewCanvas.style.position = 'relative';
        this.$previewCanvas.style.left = '' + this.$container.scrollLeft + 'px';
        this.$previewCanvas.style.top = '' + this.$container.scrollTop + 'px';
        this.$container.insertBefore(this.$previewCanvas, this.$peg);
        this.$container.style.overflow = 'hidden';

        this.flagPreviewIsActive = true;
    }

    unfreeze() {
        if (!this.flagPreviewIsActive) return;

        if (this.$container && this.$previewCanvas) this.$container.removeChild(this.$previewCanvas);
        this.previewContext = null;
        this.$previewCanvas = null;

        this.flagPreviewIsActive = false;
    }

    async snapAsync($canvas: HTMLCanvasElement) {
        if (!this.flagFlashMovieLoaded) throw new Error("Webcam is not loaded yet");
        if (!this.flagPreviewIsActive) await this.freezeAsync();
        if (!this.$previewCanvas) throw new Error("PreviewCanvas is null");

        getContext2D($canvas).drawImage(this.$previewCanvas, 0, 0);

        if (!this.params.flagFleezeWhenSnapped) this.unfreeze();
    }

    flashNotify(type: string, message: string) {
        switch (type) {
            case 'flashLoadComplete':
                this.flagFlashMovieLoaded = true;
                break;

            case 'cameraLive':
                this.flagFlashLive = true;
                if (this.onFlashLive) this.onFlashLive();
                break;

            case 'error':
                if (this.onFlashError) this.onFlashError(new FlashError(message));
                break;

            default:
                break;
        }
    }
}
