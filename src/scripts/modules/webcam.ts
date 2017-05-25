const SHOCKWAVE_FLASH = 'Shockwave Flash';
const SHOCKWAVE_FLASH_AX = 'ShockwaveFlash.ShockwaveFlash';
const FLASH_MIME_TYPE = 'application/x-shockwave-flash';

class FlashError extends Error {
    constructor(message: string) {
        super(message);
    }
}

class WebcamError extends Error {
    constructor(message: string) {
        super(message);
    }
}

type Callback = (...args: any[]) => void

const protocol: string = location.protocol.match(/https/i) ? 'https' : 'http';
const flagIOS: boolean = /iPad|iPhone|iPod/.test(navigator.userAgent) && !('MSStream' in window);
let flagWebCamInitialized: boolean = false;
let flagFlashDetected: boolean = false;

let getUserMedia: typeof navigator.mediaDevices.getUserMedia | null;
let URL: typeof window.URL | null;

interface FlashCustomHTMLObjectElement extends HTMLObjectElement {
    _snap: any
    _releaseCamera: any
}

interface MozNavigator extends Navigator {
    mozGetUserMedia: typeof navigator.mediaDevices.getUserMedia;
}

interface WebKitNavigator extends Navigator {
    webkitGetUserMedia: typeof navigator.mediaDevices.getUserMedia;
}

interface WebkitWindow extends Window {
    webkitURL: typeof window.URL
}

interface MozWindow extends Window {
    mozURL: typeof window.URL
}

interface MSWindow extends Window {
    msURL: typeof window.URL
    ActiveXObject: { new(name: string): any }
}

interface MyPluginArray extends PluginArray {
    [name: string]: any
}

interface MyMimeTypes extends MimeTypeArray {
    [name: string]: any
}

interface MyWindow extends Window {
    'Webcam': WebCam
}

function init() {
    // Setup getUserMedia, with polyfill for older browsers
    // Adapted from: https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        getUserMedia = (constraints: MediaStreamConstraints) => navigator.mediaDevices.getUserMedia(constraints);
    } else if ('mozGetUserMedia' in navigator) {
        getUserMedia = (constraints: MediaStreamConstraints) => (navigator as MozNavigator).mozGetUserMedia(constraints)
    } else if ('webkitGetUserMedia' in navigator) {
        getUserMedia = (constraints: MediaStreamConstraints) => (navigator as WebKitNavigator).webkitGetUserMedia(constraints)
    }

    if ('URL' in window) {
        URL = window.URL;
    } else if ('webkitURL' in window) {
        URL = (window as WebkitWindow).webkitURL;
    } else if ('mozURL' in window) {
        URL = (window as MozWindow).mozURL;
    } else if ('msURL' in window) {
        URL = (window as MSWindow).msURL;
    }

    // Older versions of firefox (< 21) apparently claim support but user media does not actually work
    if (navigator.userAgent.match(/Firefox\D+(\d+)/)) {
        if (parseInt(RegExp.$1, 10) < 21) getUserMedia = null;
    }

    if (typeof navigator.plugins === 'object' &&
        typeof (navigator.plugins as MyPluginArray)[SHOCKWAVE_FLASH] === 'object' &&
        (navigator.plugins as MyPluginArray)[SHOCKWAVE_FLASH].description &&
        typeof navigator.mimeTypes === 'object' &&
        (navigator.mimeTypes as MyMimeTypes)[FLASH_MIME_TYPE] &&
        (navigator.mimeTypes as MyMimeTypes)[FLASH_MIME_TYPE].enabledPlugin) {

        flagFlashDetected = true;

    } else if ('ActiveXObject' in window) {
        try {
            let activeX = new (window as MSWindow).ActiveXObject(SHOCKWAVE_FLASH_AX);
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
    dest_width: 0,         // size of captured image
    dest_height: 0,        // these default to width/height
    image_format: 'png',  // image format (may be jpeg or png)
    jpeg_quality: 90,      // jpeg image quality from 0 (worst) to 100 (best)
    enable_flash: true,    // enable flash fallback,
    force_flash: false,    // force flash mode,
    flagHorizontalFlip: false,     // flip image horiz (mirror mode)
    fps: 30,               // camera frames per second
    upload_name: 'webcam', // name of file in upload post data
    constraints: null,     // custom user media constraints,
    swfURL: '',            // URI to webcam.swf movie (defaults to the js location)
    noInterfaceFoundText: 'No supported webcam interface found.',
    unfreeze_snap: true,    // Whether to unfreeze the camera after snap (defaults to true)
    iosPlaceholderText: 'Click here to open camera.',
};

export default class WebCam {
    hooks: { [type: string]: ((...args: any[]) => any)[] };
    flagPreviewIsActive: boolean;
    previewCanvas: HTMLCanvasElement | null = null;
    previewContext: CanvasRenderingContext2D | null = null;
    onBeforeUnload: () => void;
    flagUseUserMedia: boolean = false;
    flagNewUser: boolean = false;
    flagFlashMovieLoaded: boolean = false;
    flagFlashLive: boolean = false;
    video: HTMLVideoElement | null = null;
    container: HTMLElement | null = null;
    params: typeof defaultParams;
    peg: HTMLDivElement | null = null;
    flagUserMedia: boolean;


    constructor(params: typeof defaultParams) {
        if (!flagWebCamInitialized) init();

        this.params = Object.assign({}, defaultParams, params);
        this.hooks = {};
        this.flagUserMedia = !this.params.force_flash && !!getUserMedia && !!window.URL;
        if (this.flagUserMedia) {
            this.onBeforeUnload = () => this.reset();
            window.addEventListener('beforeunload', this.onBeforeUnload);
        }
    }

    attach(container: HTMLElement | string) {
        if (typeof(container) == 'string') {
            container = document.querySelector(container) as HTMLElement;
        }
        if (!container) {
            return this.dispatch('error', new WebcamError("Could not locate DOM element to attach to."));
        }
        this.container = container;
        this.container.innerHTML = '';

        // insert "peg" so we can insert our preview canvas adjacent to it later on
        let peg = document.createElement('div');
        container.appendChild(peg);
        this.peg = peg;

        // set width/height if not already set
        if (!this.params.width) this.params.width = container.offsetWidth;
        if (!this.params.height) this.params.height = container.offsetHeight;

        // make sure we have a nonzero width and height at this point
        if (!this.params.width || !this.params.height) {
            return this.dispatch('error', new WebcamError("No width and/or height for webcam.  Please call set() first, or attach to a visible element."));
        }

        // set defaults for dest_width / dest_height if not set
        if (!this.params.dest_width) this.params.dest_width = this.params.width;
        if (!this.params.dest_height) this.params.dest_height = this.params.height;

        // check for default fps
        if (typeof this.params.fps !== "number") this.params.fps = 30;

        // adjust scale if dest_width or dest_height is different
        let scaleX = this.params.width / this.params.dest_width;
        let scaleY = this.params.height / this.params.dest_height;

        if (this.flagUserMedia) {
            // setup webcam video container
            let video = document.createElement('video') as HTMLVideoElement;
            video.setAttribute('autoplay', 'autoplay');
            video.style.width = '' + this.params.dest_width + 'px';
            video.style.height = '' + this.params.dest_height + 'px';

            if ((scaleX != 1.0) || (scaleY != 1.0)) {
                this.container.style.overflow = 'hidden';
                video.style.transformOrigin = '0px 0px';
                video.style.transform = 'scaleX(' + scaleX + ') scaleY(' + scaleY + ')';
            }

            // add video element to dom
            this.container.appendChild(video);
            this.video = video;

            getUserMedia!({
                "audio": false,
                "video": true
            })
                .then((stream: MediaStream) => {
                    video.addEventListener('loadedmetadata', () => {
                        this.flagFlashMovieLoaded = true;
                        this.flagFlashLive = true;
                        this.dispatch('load');
                        this.dispatch('live');
                        this.flip();
                    });
                    video.src = URL!.createObjectURL(stream); //| stream
                })
                .catch((err: Error) => {
                    if (this.params.enable_flash && flagFlashDetected) {
                        setTimeout(() => {
                            this.params.force_flash = true;
                            this.attach(container);
                        }, 1);
                    } else {
                        this.dispatch('error', err);
                    }
                });
        } else if (flagIOS) {
            let div = document.createElement('div') as HTMLDivElement;
            div.id = this.container.id + '-ios_div';
            div.className = 'webcamjs-ios-placeholder';
            div.style.width = '' + this.params.width + 'px';
            div.style.height = '' + this.params.height + 'px';
            div.style.textAlign = 'center';
            div.style.display = 'table-cell';
            div.style.verticalAlign = 'middle';
            div.style.backgroundRepeat = 'no-repeat';
            div.style.backgroundSize = 'contain';
            div.style.backgroundPosition = 'center';

            let span = document.createElement('span') as HTMLSpanElement;
            span.className = 'webcamjs-ios-text';
            span.innerHTML = this.params.iosPlaceholderText;
            div.appendChild(span);

            let img = document.createElement('img') as HTMLImageElement;
            img.id = this.container.id + '-ios_img';
            img.style.width = '' + this.params.dest_width + 'px';
            img.style.height = '' + this.params.dest_height + 'px';
            img.style.display = 'none';
            div.appendChild(img);

            let input = document.createElement('input') as HTMLInputElement;
            input.id = this.container.id + '-ios_input';
            input.setAttribute('type', 'file');
            input.setAttribute('accept', 'image/*');
            input.setAttribute('capture', 'camera');

            // add input listener to load the selected image
            input.addEventListener('change', (event: Event) => {
                if (!input || !input.files) return;
                if (input.files.length > 0 && input.files[0].type.indexOf('image/') == 0) {
                    let objURL = URL!.createObjectURL(input.files[0]);

                    // load image with auto scale and crop
                    let image = new Image();
                    image.addEventListener('load', () => {
                        let canvas = document.createElement('canvas');
                        canvas.width = this.params.dest_width;
                        canvas.height = this.params.dest_height;
                        let ctx = canvas.getContext('2d');
                        if (!ctx) throw Error('null');

                        // crop and scale image for final size
                        let ratio = Math.min(image.width / this.params.dest_width, image.height / this.params.dest_height);
                        let sw = this.params.dest_width * ratio;
                        let sh = this.params.dest_height * ratio;
                        let sx = (image.width - sw) / 2;
                        let sy = (image.height - sh) / 2;
                        ctx.drawImage(image, sx, sy, sw, sh, 0, 0, this.params.dest_width, this.params.dest_height);

                        let dataURL = canvas.toDataURL();
                        img.src = dataURL;
                        div.style.backgroundImage = "url('" + dataURL + "')";
                    }, false);

                    // read EXIF data
                    let fileReader = new FileReader();
                    fileReader.addEventListener('load', (e: Event) => {
                        let orientation = exifOrientation(fileReader.result);
                        if (orientation > 1) {
                            // image need to rotate (see comments on fixOrientation method for more information)
                            // transform image and load to image object
                            fixOrientation(objURL, orientation, image);
                        } else {
                            // load image data to image object
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

            input.style.display = 'none';
            container.appendChild(input);
            // make div clickable for open camera interface
            div.addEventListener('click', () => {
                // no global callback definied for snapshot, load image and wait for external snap method call
                input.style.display = 'block';
                input.focus();
                input.click();
                input.style.display = 'none';
            }, false);
            container.appendChild(div);
            this.flagFlashMovieLoaded = true;
            this.flagFlashLive = true;
        } else if (this.params.enable_flash && flagFlashDetected) {
            // flash fallback
            (window as MyWindow)['Webcam'] = this; // needed for flash-to-js interface
            let div = document.createElement('div');
            div.innerHTML = this.getSWFHTML();
            container.appendChild(div);
        } else {
            this.dispatch('error', new WebcamError(this.params.noInterfaceFoundText));
        }

        // setup final crop for live preview
        // no crop, set size to desired
        container.style.width = '' + this.params.width + 'px';
        container.style.height = '' + this.params.height + 'px';
    }

    reset() {
        if (this.flagPreviewIsActive) this.unfreeze();

        this.unflip();

        if (this.flagUseUserMedia) {
            this.video = null;
        }

        if (this.flagUseUserMedia && this.flagFlashMovieLoaded && !flagIOS) {
            let movie = this.getMovie();
            if (movie && '_releaseCamera' in movie) movie._releaseCamera();
        }

        if (this.container) {
            this.container.innerHTML = '';
            this.container = null;
        }

        this.flagFlashMovieLoaded = false;
        this.flagFlashLive = false;
    }

    on(type: string, callback: (...args: any[]) => any) {
        if (!(type in this.hooks)) this.hooks[type] = [];
        this.hooks[type].push(callback);
    }

    dispatch(type: string, ...args: any[]) {
        if (type in this.hooks) {
            let handlers = this.hooks[type];

            for (let i = 0; i < handlers.length; i++) {
                handlers[i].apply(this, args);
            }
        } else {
            if (type !== 'error') return;

            throw (args[0] as Error);
        }
    }

    getSWFHTML() {
        let html: string = '';

        if (!flagFlashDetected) {
            this.dispatch('error', new FlashError("Adobe Flash Player not found. Please install from get.adobe.com/flashplayer and try again."));
            return '';
        }

        if (window.localStorage && localStorage.getItem('visited')) {
            this.flagNewUser = true;
            localStorage.setItem('visited', '1');
        }

        let flashVars = Object.keys(this.params)
            .map(key => `${key}=${encodeURIComponent(this.params[key])}`)
            .join('&');

        // construct object/embed tag
        html += `<object classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000" 
                         type="application/x-shockwave-flash"
                         codebase="${protocol}://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=9,0,0,0"
                         width="${this.params.width}"
                         height="${this.params.height}"
                         id="webcam_movie_obj"
                         align="middle">
                         <param name="wmode" value="opaque" />
                         <param name="allowScriptAccess" value="always" />
                         <param name="allowFullScreen" value="false" />
                         <param name="movie" value="${this.params.swfURL}" />
                         <param name="loop" value="false" />
                         <param name="menu" value="false" />
                         <param name="quality" value="best" />
                         <param name="bgcolor" value="#ffffff" />
                         <param name="flashvars" value="${flashVars}" />
                         <embed id="webcam_movie_embed"
                                src="${this.params.swfURL}" 
                                wmode="opaque" 
                                loop="false" 
                                menu="false"
                                quality="best" 
                                bgcolor="#ffffff" 
                                width="${this.params.width}" 
                                height="${this.params.height}"
                                name="webcam_movie_embed" 
                                align="middle" 
                                allowScriptAccess="always" 
                                allowFullScreen="false" 
                                type="application/x-shockwave-flash" 
                                pluginspage="http://www.macromedia.com/go/getflashplayer"
                                flashvars="${flashVars}">
                          </embed>
                     </object>`;

        return html;
    }

    getMovie() {
        // get reference to movie object/embed in DOM
        if (!this.flagFlashMovieLoaded) return this.dispatch('error', new FlashError("Flash Movie is not loaded yet"));

        let movie: FlashCustomHTMLObjectElement | null;

        movie = document.getElementById('webcam_movie_obj') as FlashCustomHTMLObjectElement;
        if (!movie || !movie._snap) movie = document.getElementById('webcam_movie_embed') as FlashCustomHTMLObjectElement;
        if (!movie) this.dispatch('error', new FlashError("Cannot locate Flash movie in DOM"));

        return movie;
    }

    freeze() {
        if (this.flagPreviewIsActive) this.unfreeze();


        this.unflip();

        let finalWidth = this.params.dest_width;
        let finalHeight = this.params.dest_height;

        this.previewCanvas = document.createElement('canvas');
        this.previewCanvas.width = finalWidth;
        this.previewCanvas.height = finalHeight;
        this.previewContext = this.previewCanvas.getContext('2d');

        let scaleX = this.params.width / this.params.dest_width;
        let scaleY = this.params.height / this.params.dest_height;
        if ((scaleX != 1.0) || (scaleY != 1.0)) {
            this.previewCanvas.style.transformOrigin = '0px 0px';
            this.previewCanvas.style.transform = 'scaleX(' + scaleX + ') scaleY(' + scaleY + ')';
        }

        // take snapshot, but fire our own callback
        this.snap(() => {
            if (!this.previewCanvas || !this.container) return;
            this.previewCanvas.style.position = 'relative';
            this.previewCanvas.style.left = '' + this.container.scrollLeft + 'px';
            this.previewCanvas.style.top = '' + this.container.scrollTop + 'px';

            this.container.insertBefore(this.previewCanvas, this.peg);
            this.container.style.overflow = 'hidden';

            // set flag for user capture (use preview)
            this.flagPreviewIsActive = true;
        }, this.previewCanvas);
    }

    unfreeze() {
        if (!this.flagPreviewIsActive) return;

        if (this.container && this.previewCanvas) this.container.removeChild(this.previewCanvas);
        this.previewContext = null;
        this.previewCanvas = null;

        this.flagPreviewIsActive = false;
        this.flip();
    }

    flip() {
        if (!this.params.flagHorizontalFlip) return;

        if (this.container) this.container.style.transform = 'scaleX(-1)';
    }

    unflip() {
        if (!this.params.flagHorizontalFlip) return;

        if (this.container) this.container.style.transform = 'scaleX(1)';
    }

    savePreview(userCallback: Callback | null = null, userCanvas: HTMLCanvasElement | null = null) {
        if (!this.previewCanvas) return;

        if (!userCallback) return this.dispatch('error', new WebcamError("Please provide a callback function or canvas to snap()"));

        // render to user canvas if desired
        if (userCanvas) {
            let userContext = userCanvas.getContext('2d');
            if (userContext) userContext.drawImage(this.previewCanvas, 0, 0);
        }

        // fire user callback if desired
        userCallback(
            userCanvas ?
            null :
            this.previewCanvas.toDataURL('image/png', this.params.jpeg_quality / 100),
            this.previewCanvas,
            this.previewContext
        );

        // remove preview
        if (this.params.unfreeze_snap) this.unfreeze();
    }

    snap(userCallback: Callback | null = null, userCanvas: HTMLCanvasElement | null = null) {

        if (!this.flagFlashMovieLoaded) return this.dispatch('error', new WebcamError("Webcam is not loaded yet"));

        if (!userCallback) return this.dispatch('error', new WebcamError("Please provide a callback function or canvas to snap()"));

        if (this.flagPreviewIsActive) return this.savePreview(userCallback, userCanvas);

        let canvas = document.createElement('canvas');
        canvas.width = this.params.dest_width;
        canvas.height = this.params.dest_height;

        let context = canvas.getContext('2d');
        if (!context) throw Error('Context2D Initialization Failed.');

        if (this.params.flagHorizontalFlip) {
            context.translate(this.params.dest_width, 0);
            context.scale(-1, 1);
        }

        let image: HTMLImageElement;

        // create inline function, called after image load (flash) or immediately (native)
        let onLoadHandler = () => {
            if (image && image.src && image.width && image.height) {
                if (context) context.drawImage(image, 0, 0, this.params.dest_width, this.params.dest_height);
            }

            if (userCanvas) {
                let userContext = userCanvas.getContext('2d');
                if (!userContext) throw Error('null');
                userContext.drawImage(canvas, 0, 0);
            }

            // fire user callback if desired
            userCallback(
                userCanvas ? null : canvas.toDataURL('image/png', this.params.jpeg_quality / 100),
                canvas,
                context
            );
        };

        // grab image frame from userMedia or flash movie
        if (getUserMedia) {
            if (!this.video) throw Error('video is null');
            context.drawImage(this.video, 0, 0, this.params.dest_width, this.params.dest_height);
            onLoadHandler();

        } else if (flagIOS) {
            if (!this.container) return;

            let div = document.getElementById(this.container.id + '-ios_div') as HTMLDivElement;
            let input = document.getElementById(this.container.id + '-ios_input') as HTMLInputElement;
            image = document.getElementById(this.container.id + '-ios_img') as HTMLImageElement;
            if (!div || !image || !input) throw Error('null');

            let onLoadHandlerIOS = () => {
                onLoadHandler.call(image);
                image.removeEventListener('load', onLoadHandlerIOS);
                div.style.backgroundImage = 'none';
                image.removeAttribute('src');
                input.value = '';
            };

            if (!input.value) {
                // No image selected yet, activate input field
                image.addEventListener('load', onLoadHandlerIOS);
                input.style.display = 'block';
                input.focus();
                input.click();
                input.style.display = 'none';

            } else {
                // Image already selected
                onLoadHandlerIOS();
            }

        } else {
            // flash fallback
            image = new Image();
            image.onload = onLoadHandler;
            image.src = 'data:image/png;base64,' + this.getMovie()!._snap();
        }

        return null;
    }

    flashNotify(type: string, message: string) {
        switch (type) {
            case 'flashLoadComplete':
                this.flagFlashMovieLoaded = true;
                this.dispatch('load');
                break;

            case 'cameraLive':
                this.flagFlashLive = true;
                this.dispatch('live');
                break;

            case 'error':
                this.dispatch('error', new FlashError(message));
                break;

            default:
                break;
        }
    }
}
