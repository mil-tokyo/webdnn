/******/ (function(modules) { // webpackBootstrap
/******/ 	// The module cache
/******/ 	var installedModules = {};
/******/
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/
/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId]) {
/******/ 			return installedModules[moduleId].exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			i: moduleId,
/******/ 			l: false,
/******/ 			exports: {}
/******/ 		};
/******/
/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/
/******/ 		// Flag the module as loaded
/******/ 		module.l = true;
/******/
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/
/******/
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = modules;
/******/
/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = installedModules;
/******/
/******/ 	// identity function for calling harmony imports with the correct context
/******/ 	__webpack_require__.i = function(value) { return value; };
/******/
/******/ 	// define getter function for harmony exports
/******/ 	__webpack_require__.d = function(exports, name, getter) {
/******/ 		if(!__webpack_require__.o(exports, name)) {
/******/ 			Object.defineProperty(exports, name, {
/******/ 				configurable: false,
/******/ 				enumerable: true,
/******/ 				get: getter
/******/ 			});
/******/ 		}
/******/ 	};
/******/
/******/ 	// getDefaultExport function for compatibility with non-harmony modules
/******/ 	__webpack_require__.n = function(module) {
/******/ 		var getter = module && module.__esModule ?
/******/ 			function getDefault() { return module['default']; } :
/******/ 			function getModuleExports() { return module; };
/******/ 		__webpack_require__.d(getter, 'a', getter);
/******/ 		return getter;
/******/ 	};
/******/
/******/ 	// Object.prototype.hasOwnProperty.call
/******/ 	__webpack_require__.o = function(object, property) { return Object.prototype.hasOwnProperty.call(object, property); };
/******/
/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "";
/******/
/******/ 	// Load entry module and return exports
/******/ 	return __webpack_require__(__webpack_require__.s = 10);
/******/ })
/************************************************************************/
/******/ ([
/* 0 */
/***/ (function(module, exports) {

(function (i, s, o, g, r, a, m) {
	i['GoogleAnalyticsObject'] = r;
	i[r] = i[r] || function () {
			(i[r].q = i[r].q || []).push(arguments)
		}, i[r].l = 1 * new Date();
	a = s.createElement(o),
		m = s.getElementsByTagName(o)[0];
	a.async = 1;
	a.src = g;
	m.parentNode.insertBefore(a, m)
})(window, document, 'script', 'https://www.google-analytics.com/analytics.js', 'ga');

ga('create', 'UA-100057100-1', 'auto');
ga('send', 'pageview');


/***/ }),
/* 1 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

Object.defineProperty(exports, "__esModule", { value: true });
var progress_bar_1 = __webpack_require__(2);
var InitializingView = (function () {
    function InitializingView(base) {
        this.base = base;
        var message = base.querySelector('.InitializingView-Message');
        if (!message)
            throw Error('.InitializingView-Message not found');
        this.message = message;
        var progressBarInner = base.querySelector('.ProgressBar-Inner');
        if (!progressBarInner)
            throw Error('.ProgressBar-Inner not found');
        this.progressBar = new progress_bar_1.default(progressBarInner);
    }
    InitializingView.prototype.updateProgress = function (ratio) {
        this.progressBar.update(ratio);
    };
    InitializingView.prototype.updateMessage = function (message) {
        this.message.textContent = message;
    };
    InitializingView.prototype.remove = function () {
        if (this.base.parentNode) {
            this.base.parentNode.removeChild(this.base);
        }
    };
    return InitializingView;
}());
exports.default = InitializingView;


/***/ }),
/* 2 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

Object.defineProperty(exports, "__esModule", { value: true });
var ProgressBar = (function () {
    function ProgressBar(bar) {
        this.bar = bar;
    }
    ProgressBar.prototype.update = function (ratio) {
        this.bar.style.width = Math.min(Math.max(ratio, 0), 1) * 100 + "%";
    };
    return ProgressBar;
}());
exports.default = ProgressBar;


/***/ }),
/* 3 */,
/* 4 */,
/* 5 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var __extends = (this && this.__extends) || (function () {
    var extendStatics = Object.setPrototypeOf ||
        ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
        function (d, b) { for (var p in b) if (b.hasOwnProperty(p)) d[p] = b[p]; };
    return function (d, b) {
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
var SHOCKWAVE_FLASH = 'Shockwave Flash';
var SHOCKWAVE_FLASH_AX = 'ShockwaveFlash.ShockwaveFlash';
var FLASH_MIME_TYPE = 'application/x-shockwave-flash';
var FlashError = (function (_super) {
    __extends(FlashError, _super);
    function FlashError(message) {
        return _super.call(this, message) || this;
    }
    return FlashError;
}(Error));
var WebcamError = (function (_super) {
    __extends(WebcamError, _super);
    function WebcamError(message) {
        return _super.call(this, message) || this;
    }
    return WebcamError;
}(Error));
var protocol = location.protocol.match(/https/i) ? 'https' : 'http';
var flagIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !('MSStream' in window);
var flagWebCamInitialized = false;
var flagFlashDetected = false;
var getUserMedia;
var URL;
function init() {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        getUserMedia = function (constraints) { return navigator.mediaDevices.getUserMedia(constraints); };
    }
    else if ('mozGetUserMedia' in navigator) {
        getUserMedia = function (constraints) { return navigator.mozGetUserMedia(constraints); };
    }
    else if ('webkitGetUserMedia' in navigator) {
        getUserMedia = function (constraints) { return navigator.webkitGetUserMedia(constraints); };
    }
    if ('URL' in window) {
        URL = window.URL;
    }
    else if ('webkitURL' in window) {
        URL = window.webkitURL;
    }
    else if ('mozURL' in window) {
        URL = window.mozURL;
    }
    else if ('msURL' in window) {
        URL = window.msURL;
    }
    if (navigator.userAgent.match(/Firefox\D+(\d+)/)) {
        if (parseInt(RegExp.$1, 10) < 21)
            getUserMedia = null;
    }
    if (typeof navigator.plugins === 'object' &&
        typeof navigator.plugins[SHOCKWAVE_FLASH] === 'object' &&
        navigator.plugins[SHOCKWAVE_FLASH].description &&
        typeof navigator.mimeTypes === 'object' &&
        navigator.mimeTypes[FLASH_MIME_TYPE] &&
        navigator.mimeTypes[FLASH_MIME_TYPE].enabledPlugin) {
        flagFlashDetected = true;
    }
    else if ('ActiveXObject' in window) {
        try {
            var activeX = new window.ActiveXObject(SHOCKWAVE_FLASH_AX);
            if (activeX && activeX.GetVariable('$version'))
                flagFlashDetected = true;
        }
        catch (e) { }
    }
    flagWebCamInitialized = true;
}
function exifOrientation(binFile) {
    var dataView = new DataView(binFile);
    if ((dataView.getUint8(0) != 0xFF) || (dataView.getUint8(1) != 0xD8)) {
        console.log('Not a valid JPEG file');
        return 0;
    }
    var offset = 2;
    var marker = null;
    while (offset < binFile.byteLength) {
        if (dataView.getUint8(offset) != 0xFF) {
            console.log('Not a valid marker at offset ' + offset + ', found: ' + dataView.getUint8(offset));
            return 0;
        }
        marker = dataView.getUint8(offset + 1);
        if (marker == 225) {
            offset += 4;
            var str = "";
            for (var n = 0; n < 4; n++) {
                str += String.fromCharCode(dataView.getUint8(offset + n));
            }
            if (str != 'Exif') {
                console.log('Not valid EXIF data found');
                return 0;
            }
            offset += 6;
            var bigEnd = null;
            if (dataView.getUint16(offset) == 0x4949) {
                bigEnd = false;
            }
            else if (dataView.getUint16(offset) == 0x4D4D) {
                bigEnd = true;
            }
            else {
                console.log("Not valid TIFF data! (no 0x4949 or 0x4D4D)");
                return 0;
            }
            if (dataView.getUint16(offset + 2, !bigEnd) != 0x002A) {
                console.log("Not valid TIFF data! (no 0x002A)");
                return 0;
            }
            var firstIFDOffset = dataView.getUint32(offset + 4, !bigEnd);
            if (firstIFDOffset < 0x00000008) {
                console.log("Not valid TIFF data! (First offset less than 8)", dataView.getUint32(offset + 4, !bigEnd));
                return 0;
            }
            var dataStart = offset + firstIFDOffset;
            var entries = dataView.getUint16(dataStart, !bigEnd);
            for (var i = 0; i < entries; i++) {
                var entryOffset = dataStart + i * 12 + 2;
                if (dataView.getUint16(entryOffset, !bigEnd) == 0x0112) {
                    var valueType = dataView.getUint16(entryOffset + 2, !bigEnd);
                    var numValues = dataView.getUint32(entryOffset + 4, !bigEnd);
                    if (valueType != 3 && numValues != 1) {
                        console.log('Invalid EXIF orientation value type (' + valueType + ') or count (' + numValues + ')');
                        return 0;
                    }
                    var value = dataView.getUint16(entryOffset + 8, !bigEnd);
                    if (value < 1 || value > 8) {
                        console.log('Invalid EXIF orientation value (' + value + ')');
                        return 0;
                    }
                    return value;
                }
            }
        }
        else {
            offset += 2 + dataView.getUint16(offset + 2);
        }
    }
    return 0;
}
function fixOrientation(origObjURL, orientation, targetImg) {
    var img = new Image();
    img.addEventListener('load', function () {
        var canvas = document.createElement('canvas');
        var ctx = canvas.getContext('2d');
        if (!ctx)
            throw Error('null');
        if (orientation < 5) {
            canvas.width = img.width;
            canvas.height = img.height;
        }
        else {
            canvas.width = img.height;
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
        targetImg.src = canvas.toDataURL();
    }, false);
    img.src = origObjURL;
}
var defaultParams = {
    width: 0,
    height: 0,
    dest_width: 0,
    dest_height: 0,
    image_format: 'png',
    jpeg_quality: 90,
    enable_flash: true,
    force_flash: false,
    flagHorizontalFlip: false,
    fps: 30,
    upload_name: 'webcam',
    constraints: null,
    swfURL: '',
    noInterfaceFoundText: 'No supported webcam interface found.',
    unfreeze_snap: true,
    iosPlaceholderText: 'Click here to open camera.',
};
var WebCam = (function () {
    function WebCam(params) {
        var _this = this;
        this.previewCanvas = null;
        this.previewContext = null;
        this.flagUseUserMedia = false;
        this.flagNewUser = false;
        this.flagFlashMovieLoaded = false;
        this.flagFlashLive = false;
        this.video = null;
        this.container = null;
        this.peg = null;
        if (!flagWebCamInitialized)
            init();
        this.params = Object.assign({}, defaultParams, params);
        this.hooks = {};
        this.flagUserMedia = !this.params.force_flash && !!getUserMedia && !!window.URL;
        if (this.flagUserMedia) {
            this.onBeforeUnload = function () { return _this.reset(); };
            window.addEventListener('beforeunload', this.onBeforeUnload);
        }
    }
    WebCam.prototype.attach = function (container) {
        var _this = this;
        if (typeof (container) == 'string') {
            container = document.querySelector(container);
        }
        if (!container) {
            return this.dispatch('error', new WebcamError("Could not locate DOM element to attach to."));
        }
        this.container = container;
        this.container.innerHTML = '';
        var peg = document.createElement('div');
        container.appendChild(peg);
        this.peg = peg;
        if (!this.params.width)
            this.params.width = container.offsetWidth;
        if (!this.params.height)
            this.params.height = container.offsetHeight;
        if (!this.params.width || !this.params.height) {
            return this.dispatch('error', new WebcamError("No width and/or height for webcam.  Please call set() first, or attach to a visible element."));
        }
        if (!this.params.dest_width)
            this.params.dest_width = this.params.width;
        if (!this.params.dest_height)
            this.params.dest_height = this.params.height;
        if (typeof this.params.fps !== "number")
            this.params.fps = 30;
        var scaleX = this.params.width / this.params.dest_width;
        var scaleY = this.params.height / this.params.dest_height;
        if (this.flagUserMedia) {
            var video_1 = document.createElement('video');
            video_1.setAttribute('autoplay', 'autoplay');
            video_1.style.width = '' + this.params.dest_width + 'px';
            video_1.style.height = '' + this.params.dest_height + 'px';
            if ((scaleX != 1.0) || (scaleY != 1.0)) {
                this.container.style.overflow = 'hidden';
                video_1.style.transformOrigin = '0px 0px';
                video_1.style.transform = 'scaleX(' + scaleX + ') scaleY(' + scaleY + ')';
            }
            this.container.appendChild(video_1);
            this.video = video_1;
            getUserMedia({
                "audio": false,
                "video": true
            })
                .then(function (stream) {
                video_1.addEventListener('loadedmetadata', function () {
                    _this.flagFlashMovieLoaded = true;
                    _this.flagFlashLive = true;
                    _this.dispatch('load');
                    _this.dispatch('live');
                    _this.flip();
                });
                video_1.src = URL.createObjectURL(stream);
            })
                .catch(function (err) {
                if (_this.params.enable_flash && flagFlashDetected) {
                    setTimeout(function () {
                        _this.params.force_flash = true;
                        _this.attach(container);
                    }, 1);
                }
                else {
                    _this.dispatch('error', err);
                }
            });
        }
        else if (flagIOS) {
            var div_1 = document.createElement('div');
            div_1.id = this.container.id + '-ios_div';
            div_1.className = 'webcamjs-ios-placeholder';
            div_1.style.width = '' + this.params.width + 'px';
            div_1.style.height = '' + this.params.height + 'px';
            div_1.style.textAlign = 'center';
            div_1.style.display = 'table-cell';
            div_1.style.verticalAlign = 'middle';
            div_1.style.backgroundRepeat = 'no-repeat';
            div_1.style.backgroundSize = 'contain';
            div_1.style.backgroundPosition = 'center';
            var span = document.createElement('span');
            span.className = 'webcamjs-ios-text';
            span.innerHTML = this.params.iosPlaceholderText;
            div_1.appendChild(span);
            var img_1 = document.createElement('img');
            img_1.id = this.container.id + '-ios_img';
            img_1.style.width = '' + this.params.dest_width + 'px';
            img_1.style.height = '' + this.params.dest_height + 'px';
            img_1.style.display = 'none';
            div_1.appendChild(img_1);
            var input_1 = document.createElement('input');
            input_1.id = this.container.id + '-ios_input';
            input_1.setAttribute('type', 'file');
            input_1.setAttribute('accept', 'image/*');
            input_1.setAttribute('capture', 'camera');
            input_1.addEventListener('change', function (event) {
                if (!input_1 || !input_1.files)
                    return;
                if (input_1.files.length > 0 && input_1.files[0].type.indexOf('image/') == 0) {
                    var objURL_1 = URL.createObjectURL(input_1.files[0]);
                    var image_1 = new Image();
                    image_1.addEventListener('load', function () {
                        var canvas = document.createElement('canvas');
                        canvas.width = _this.params.dest_width;
                        canvas.height = _this.params.dest_height;
                        var ctx = canvas.getContext('2d');
                        if (!ctx)
                            throw Error('null');
                        var ratio = Math.min(image_1.width / _this.params.dest_width, image_1.height / _this.params.dest_height);
                        var sw = _this.params.dest_width * ratio;
                        var sh = _this.params.dest_height * ratio;
                        var sx = (image_1.width - sw) / 2;
                        var sy = (image_1.height - sh) / 2;
                        ctx.drawImage(image_1, sx, sy, sw, sh, 0, 0, _this.params.dest_width, _this.params.dest_height);
                        var dataURL = canvas.toDataURL();
                        img_1.src = dataURL;
                        div_1.style.backgroundImage = "url('" + dataURL + "')";
                    }, false);
                    var fileReader_1 = new FileReader();
                    fileReader_1.addEventListener('load', function (e) {
                        var orientation = exifOrientation(fileReader_1.result);
                        if (orientation > 1) {
                            fixOrientation(objURL_1, orientation, image_1);
                        }
                        else {
                            image_1.src = objURL_1;
                        }
                    }, false);
                    var xhr_1 = new XMLHttpRequest();
                    xhr_1.open("GET", objURL_1, true);
                    xhr_1.responseType = "blob";
                    xhr_1.onload = function () {
                        if (xhr_1.status == 200 || xhr_1.status === 0) {
                            fileReader_1.readAsArrayBuffer(xhr_1.response);
                        }
                    };
                    xhr_1.send();
                }
            }, false);
            input_1.style.display = 'none';
            container.appendChild(input_1);
            div_1.addEventListener('click', function () {
                input_1.style.display = 'block';
                input_1.focus();
                input_1.click();
                input_1.style.display = 'none';
            }, false);
            container.appendChild(div_1);
            this.flagFlashMovieLoaded = true;
            this.flagFlashLive = true;
        }
        else if (this.params.enable_flash && flagFlashDetected) {
            window['Webcam'] = this;
            var div = document.createElement('div');
            div.innerHTML = this.getSWFHTML();
            container.appendChild(div);
        }
        else {
            this.dispatch('error', new WebcamError(this.params.noInterfaceFoundText));
        }
        container.style.width = '' + this.params.width + 'px';
        container.style.height = '' + this.params.height + 'px';
    };
    WebCam.prototype.reset = function () {
        if (this.flagPreviewIsActive)
            this.unfreeze();
        this.unflip();
        if (this.flagUseUserMedia) {
            this.video = null;
        }
        if (this.flagUseUserMedia && this.flagFlashMovieLoaded && !flagIOS) {
            var movie = this.getMovie();
            if (movie && '_releaseCamera' in movie)
                movie._releaseCamera();
        }
        if (this.container) {
            this.container.innerHTML = '';
            this.container = null;
        }
        this.flagFlashMovieLoaded = false;
        this.flagFlashLive = false;
    };
    WebCam.prototype.on = function (type, callback) {
        if (!(type in this.hooks))
            this.hooks[type] = [];
        this.hooks[type].push(callback);
    };
    WebCam.prototype.dispatch = function (type) {
        var args = [];
        for (var _i = 1; _i < arguments.length; _i++) {
            args[_i - 1] = arguments[_i];
        }
        if (type in this.hooks) {
            var handlers = this.hooks[type];
            for (var i = 0; i < handlers.length; i++) {
                handlers[i].apply(this, args);
            }
        }
        else {
            if (type !== 'error')
                return;
            throw args[0];
        }
    };
    WebCam.prototype.getSWFHTML = function () {
        var _this = this;
        var html = '';
        if (!flagFlashDetected) {
            this.dispatch('error', new FlashError("Adobe Flash Player not found. Please install from get.adobe.com/flashplayer and try again."));
            return '';
        }
        if (window.localStorage && localStorage.getItem('visited')) {
            this.flagNewUser = true;
            localStorage.setItem('visited', '1');
        }
        var flashVars = Object.keys(this.params)
            .map(function (key) { return key + "=" + encodeURIComponent(_this.params[key]); })
            .join('&');
        html += "<object classid=\"clsid:d27cdb6e-ae6d-11cf-96b8-444553540000\" type=\"application/x-shockwave-flash\" codebase=\"" + protocol + "://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=9,0,0,0\" width=\"" + this.params.width + "\" height=\"" + this.params.height + "\" id=\"webcam_movie_obj\" align=\"middle\"><param name=\"wmode\" value=\"opaque\" /><param name=\"allowScriptAccess\" value=\"always\" /><param name=\"allowFullScreen\" value=\"false\" /><param name=\"movie\" value=\"" + this.params.swfURL + "\" /><param name=\"loop\" value=\"false\" /><param name=\"menu\" value=\"false\" /><param name=\"quality\" value=\"best\" /><param name=\"bgcolor\" value=\"#ffffff\" /><param name=\"flashvars\" value=\"" + flashVars + "\" /><embed id=\"webcam_movie_embed\" src=\"" + this.params.swfURL + "\" wmode=\"opaque\" loop=\"false\" menu=\"false\" quality=\"best\" bgcolor=\"#ffffff\" width=\"" + this.params.width + "\" height=\"" + this.params.height + "\"name=\"webcam_movie_embed\" align=\"middle\" allowScriptAccess=\"always\" allowFullScreen=\"false\" type=\"application/x-shockwave-flash\" pluginspage=\"http://www.macromedia.com/go/getflashplayer\"flashvars=\"" + flashVars + "\"></embed></object>";
        return html;
    };
    WebCam.prototype.getMovie = function () {
        if (!this.flagFlashMovieLoaded)
            return this.dispatch('error', new FlashError("Flash Movie is not loaded yet"));
        var movie;
        movie = document.getElementById('webcam_movie_obj');
        if (!movie || !movie._snap)
            movie = document.getElementById('webcam_movie_embed');
        if (!movie)
            this.dispatch('error', new FlashError("Cannot locate Flash movie in DOM"));
        return movie;
    };
    WebCam.prototype.freeze = function () {
        var _this = this;
        if (this.flagPreviewIsActive)
            this.unfreeze();
        this.unflip();
        var finalWidth = this.params.dest_width;
        var finalHeight = this.params.dest_height;
        this.previewCanvas = document.createElement('canvas');
        this.previewCanvas.width = finalWidth;
        this.previewCanvas.height = finalHeight;
        this.previewContext = this.previewCanvas.getContext('2d');
        var scaleX = this.params.width / this.params.dest_width;
        var scaleY = this.params.height / this.params.dest_height;
        if ((scaleX != 1.0) || (scaleY != 1.0)) {
            this.previewCanvas.style.transformOrigin = '0px 0px';
            this.previewCanvas.style.transform = 'scaleX(' + scaleX + ') scaleY(' + scaleY + ')';
        }
        this.snap(function () {
            if (!_this.previewCanvas || !_this.container)
                return;
            _this.previewCanvas.style.position = 'relative';
            _this.previewCanvas.style.left = '' + _this.container.scrollLeft + 'px';
            _this.previewCanvas.style.top = '' + _this.container.scrollTop + 'px';
            _this.container.insertBefore(_this.previewCanvas, _this.peg);
            _this.container.style.overflow = 'hidden';
            _this.flagPreviewIsActive = true;
        }, this.previewCanvas);
    };
    WebCam.prototype.unfreeze = function () {
        if (!this.flagPreviewIsActive)
            return;
        if (this.container && this.previewCanvas)
            this.container.removeChild(this.previewCanvas);
        this.previewContext = null;
        this.previewCanvas = null;
        this.flagPreviewIsActive = false;
        this.flip();
    };
    WebCam.prototype.flip = function () {
        if (!this.params.flagHorizontalFlip)
            return;
        if (this.container)
            this.container.style.transform = 'scaleX(-1)';
    };
    WebCam.prototype.unflip = function () {
        if (!this.params.flagHorizontalFlip)
            return;
        if (this.container)
            this.container.style.transform = 'scaleX(1)';
    };
    WebCam.prototype.savePreview = function (userCallback, userCanvas) {
        if (userCallback === void 0) { userCallback = null; }
        if (userCanvas === void 0) { userCanvas = null; }
        if (!this.previewCanvas)
            return;
        if (!userCallback)
            return this.dispatch('error', new WebcamError("Please provide a callback function or canvas to snap()"));
        if (userCanvas) {
            var userContext = userCanvas.getContext('2d');
            if (userContext)
                userContext.drawImage(this.previewCanvas, 0, 0);
        }
        userCallback(userCanvas ?
            null :
            this.previewCanvas.toDataURL('image/png', this.params.jpeg_quality / 100), this.previewCanvas, this.previewContext);
        if (this.params.unfreeze_snap)
            this.unfreeze();
    };
    WebCam.prototype.snap = function (userCallback, userCanvas) {
        var _this = this;
        if (userCallback === void 0) { userCallback = null; }
        if (userCanvas === void 0) { userCanvas = null; }
        if (!this.flagFlashMovieLoaded)
            return this.dispatch('error', new WebcamError("Webcam is not loaded yet"));
        if (!userCallback)
            return this.dispatch('error', new WebcamError("Please provide a callback function or canvas to snap()"));
        if (this.flagPreviewIsActive)
            return this.savePreview(userCallback, userCanvas);
        var canvas = document.createElement('canvas');
        canvas.width = this.params.dest_width;
        canvas.height = this.params.dest_height;
        var context = canvas.getContext('2d');
        if (!context)
            throw Error('Context2D Initialization Failed.');
        if (this.params.flagHorizontalFlip) {
            context.translate(this.params.dest_width, 0);
            context.scale(-1, 1);
        }
        var image;
        var onLoadHandler = function () {
            if (image && image.src && image.width && image.height) {
                if (context)
                    context.drawImage(image, 0, 0, _this.params.dest_width, _this.params.dest_height);
            }
            if (userCanvas) {
                var userContext = userCanvas.getContext('2d');
                if (!userContext)
                    throw Error('null');
                userContext.drawImage(canvas, 0, 0);
            }
            userCallback(userCanvas ? null : canvas.toDataURL('image/png', _this.params.jpeg_quality / 100), canvas, context);
        };
        if (getUserMedia) {
            if (!this.video)
                throw Error('video is null');
            context.drawImage(this.video, 0, 0, this.params.dest_width, this.params.dest_height);
            onLoadHandler();
        }
        else if (flagIOS) {
            if (!this.container)
                return;
            var div_2 = document.getElementById(this.container.id + '-ios_div');
            var input_2 = document.getElementById(this.container.id + '-ios_input');
            image = document.getElementById(this.container.id + '-ios_img');
            if (!div_2 || !image || !input_2)
                throw Error('null');
            var onLoadHandlerIOS_1 = function () {
                onLoadHandler.call(image);
                image.removeEventListener('load', onLoadHandlerIOS_1);
                div_2.style.backgroundImage = 'none';
                image.removeAttribute('src');
                input_2.value = '';
            };
            if (!input_2.value) {
                image.addEventListener('load', onLoadHandlerIOS_1);
                input_2.style.display = 'block';
                input_2.focus();
                input_2.click();
                input_2.style.display = 'none';
            }
            else {
                onLoadHandlerIOS_1();
            }
        }
        else {
            image = new Image();
            image.onload = onLoadHandler;
            image.src = 'data:image/png;base64,' + this.getMovie()._snap();
        }
        return null;
    };
    WebCam.prototype.flashNotify = function (type, message) {
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
    };
    return WebCam;
}());
exports.default = WebCam;


/***/ }),
/* 6 */,
/* 7 */
/***/ (function(module, exports) {

// removed by extract-text-webpack-plugin

/***/ }),
/* 8 */,
/* 9 */,
/* 10 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : new P(function (resolve) { resolve(result.value); }).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (_) try {
            if (f = 1, y && (t = y[op[0] & 2 ? "return" : op[0] ? "throw" : "next"]) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [0, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
Object.defineProperty(exports, "__esModule", { value: true });
__webpack_require__(7);
__webpack_require__(0);
var initializing_view_1 = __webpack_require__(1);
var webcam_1 = __webpack_require__(5);
var KEY_WEBGPU_LAST_STATUS = 'webgpu_last_status';
var KEY_FLAG_WEBGPU_DISABLED_ALERT = 'flag_webgpu_disabled_alert';
var NUM_RANDOM_IMAGE = 6;
var State;
(function (State) {
    State[State["INITIALIZING"] = 0] = "INITIALIZING";
    State[State["STAND_BY"] = 1] = "STAND_BY";
    State[State["RUNNING"] = 2] = "RUNNING";
    State[State["ERROR"] = 3] = "ERROR";
})(State || (State = {}));
var App = new (function () {
    function class_1() {
        this.state = State.INITIALIZING;
        this.lastStatus = '';
    }
    class_1.prototype.initialize = function () {
        return __awaiter(this, void 0, void 0, function () {
            var _this = this;
            var select, availability, option, option, runButton, launchView, dataSourceSelect, cameraContainer, sampleContainer, initializingViewBase, initializingView, inputCanvas, inputCtx, outputCanvas, outputCtx;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        select = document.getElementById('backend');
                        if (!select)
                            throw Error('#backend is not found.');
                        this.backendSelect = select;
                        availability = WebDNN.getBackendAvailability();
                        if (availability.status['webgpu']) {
                            this.lastStatus = localStorage.getItem(KEY_WEBGPU_LAST_STATUS) || 'none';
                            switch (this.lastStatus) {
                                case 'none':
                                    break;
                                case 'running':
                                case 'crashed':
                                    availability.status['webgpu'] = false;
                                    localStorage.setItem(KEY_WEBGPU_LAST_STATUS, 'crashed');
                                    console.warn('This browser supports WebGPU. However, it was crashed at last execution with WebGPU. Therefore, WebDNN disabled WebGPU backend temporally.');
                                    if (!localStorage.getItem(KEY_FLAG_WEBGPU_DISABLED_ALERT)) {
                                        alert('This browser supports WebGPU. However, it was crashed at last execution with WebGPU. \n\nTherefore, WebDNN disabled WebGPU backend temporally.');
                                        localStorage.setItem(KEY_FLAG_WEBGPU_DISABLED_ALERT, '1');
                                    }
                                    break;
                                case 'completed':
                                    break;
                            }
                        }
                        if (!availability.status['webgpu']) {
                            option = document.querySelector('option[value="webgpu"]');
                            if (option)
                                option.disabled = true;
                            select.value = 'webassembly';
                        }
                        if (!availability.status['webassembly']) {
                            option = document.querySelector('option[value="webassembly"]');
                            if (option)
                                option.disabled = true;
                            throw Error('This browser does not support either WebGPU nor WebAssembly/asm.js backends');
                        }
                        select.addEventListener('change', function () { return _this.onBackendSelectChange(); });
                        runButton = document.getElementById('runButton');
                        if (!runButton)
                            throw Error('#runButton is not found.');
                        this.runButton = runButton;
                        this.runButton.addEventListener('click', function () { return App.onPlayButtonClick(); });
                        launchView = document.getElementById('launchView');
                        if (launchView && launchView.parentNode) {
                            launchView.parentNode.removeChild(launchView);
                            launchView = null;
                        }
                        dataSourceSelect = document.getElementById('dataSource');
                        if (!dataSourceSelect)
                            throw Error('#dataSource is not found');
                        this.dataSourceSelect = dataSourceSelect;
                        dataSourceSelect.addEventListener('change', function () { return _this.onDataSourceSelectChange(); });
                        cameraContainer = document.getElementById('cameraContainer');
                        if (!cameraContainer)
                            throw Error('#cameraContainer is not found');
                        this.cameraContainer = cameraContainer;
                        sampleContainer = document.getElementById('sampleContainer');
                        if (!sampleContainer)
                            throw Error('#sampleContainer is not found');
                        this.sampleContainer = sampleContainer;
                        initializingViewBase = document.getElementById('initializingView');
                        if (!initializingViewBase)
                            throw Error('#initializingView is not found');
                        initializingView = new initializing_view_1.default(initializingViewBase);
                        initializingView.updateMessage('Load model data');
                        this.runners = {};
                        return [4, this.initBackendAsync(this.backendSelect.value, function (loaded, total) { return initializingView.updateProgress(loaded / total); })];
                    case 1:
                        _a.sent();
                        inputCanvas = document.getElementById('inputCanvas');
                        if (!inputCanvas)
                            throw Error('#inputCanvas is not found');
                        this.inputCanvas = inputCanvas;
                        this.w = inputCanvas.width;
                        this.h = inputCanvas.height;
                        inputCtx = inputCanvas.getContext('2d');
                        if (!inputCtx)
                            throw Error('Canvas initialization failed');
                        this.inputCtx = inputCtx;
                        outputCanvas = document.getElementById('outputCanvas');
                        if (!outputCanvas)
                            throw Error('#outputCanvas is not found');
                        outputCtx = outputCanvas.getContext('2d');
                        if (!outputCtx)
                            throw Error('Canvas initialization failed');
                        this.outputCtx = outputCtx;
                        return [4, this.updateDataSource()];
                    case 2:
                        _a.sent();
                        initializingView.remove();
                        return [2];
                }
            });
        });
    };
    class_1.prototype.onDataSourceSelectChange = function () {
        this.updateDataSource();
    };
    class_1.prototype.onBackendSelectChange = function () {
        this.initBackendAsync(this.backendSelect.value);
    };
    class_1.prototype.onPlayButtonClick = function () {
        return __awaiter(this, void 0, void 0, function () {
            var _a;
            return __generator(this, function (_b) {
                switch (_b.label) {
                    case 0:
                        _a = this.state;
                        switch (_a) {
                            case State.STAND_BY: return [3, 1];
                            case State.RUNNING: return [3, 3];
                        }
                        return [3, 5];
                    case 1: return [4, this.setState(State.RUNNING)];
                    case 2:
                        _b.sent();
                        return [3, 6];
                    case 3: return [4, this.setState(State.STAND_BY)];
                    case 4:
                        _b.sent();
                        return [3, 6];
                    case 5: return [3, 6];
                    case 6: return [2];
                }
            });
        });
    };
    class_1.prototype.initBackendAsync = function (backend, callback) {
        return __awaiter(this, void 0, void 0, function () {
            var _a, _b;
            return __generator(this, function (_c) {
                switch (_c.label) {
                    case 0: return [4, this.setState(State.INITIALIZING)];
                    case 1:
                        _c.sent();
                        return [4, WebDNN.init([backend])];
                    case 2:
                        _c.sent();
                        if (!(backend in this.runners)) return [3, 3];
                        this.runner = this.runners[backend];
                        return [3, 5];
                    case 3:
                        this.runner = this.runners[backend] = WebDNN.gpu.createDescriptorRunner();
                        return [4, this.runner.load('./models/neural_style_transfer', callback)];
                    case 4:
                        _c.sent();
                        _c.label = 5;
                    case 5:
                        _a = this;
                        return [4, this.runner.getInputViews()];
                    case 6:
                        _a.inputView = (_c.sent())[0];
                        _b = this;
                        return [4, this.runner.getOutputViews()];
                    case 7:
                        _b.outputView = (_c.sent())[0];
                        return [4, this.setState(State.STAND_BY)];
                    case 8:
                        _c.sent();
                        return [2];
                }
            });
        });
    };
    class_1.prototype.updateDataSource = function () {
        return __awaiter(this, void 0, void 0, function () {
            var _a;
            return __generator(this, function (_b) {
                switch (_b.label) {
                    case 0:
                        this.dataSource = this.dataSourceSelect.value;
                        this.sampleContainer.style.display = this.dataSource == 'sample' ? 'block' : 'none';
                        this.cameraContainer.style.display = (this.dataSource == 'video' || this.dataSource == 'photo') ?
                            'block' :
                            'none';
                        _a = this.dataSource;
                        switch (_a) {
                            case 'photo': return [3, 1];
                            case 'video': return [3, 1];
                            case 'sample': return [3, 5];
                        }
                        return [3, 9];
                    case 1: return [4, this.setState(State.INITIALIZING)];
                    case 2:
                        _b.sent();
                        return [4, this.initializeCamera()];
                    case 3:
                        _b.sent();
                        return [4, this.setState(State.STAND_BY)];
                    case 4:
                        _b.sent();
                        return [3, 9];
                    case 5: return [4, this.setState(State.INITIALIZING)];
                    case 6:
                        _b.sent();
                        this.finalizeCamera();
                        return [4, this.loadSampleImageToPreview()];
                    case 7:
                        _b.sent();
                        return [4, this.setState(State.STAND_BY)];
                    case 8:
                        _b.sent();
                        return [3, 9];
                    case 9: return [2];
                }
            });
        });
    };
    class_1.prototype.initializeCamera = function () {
        var _this = this;
        return new Promise(function (resolve) {
            _this.webcam = new webcam_1.default({
                width: 192,
                height: 144,
                fps: 60,
                flip_horiz: false,
                image_format: 'png',
                force_flash: false,
                swfURL: '/webdnn/webcam.swf',
                unfreeze_snap: _this.dataSource == 'video'
            });
            _this.webcam.on('live', resolve);
            _this.webcam.on('error', function (err) {
                console.error(err);
                _this.setMessage(err);
                _this.setState(State.ERROR);
            });
            _this.webcam.attach('#cameraContainer');
        });
    };
    class_1.prototype.finalizeCamera = function () {
        if (this.webcam)
            this.webcam.reset();
    };
    class_1.prototype.loadSampleImageToPreview = function () {
        return __awaiter(this, void 0, void 0, function () {
            var randomImageIndex, url, image;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        randomImageIndex = Math.floor(Math.random() * NUM_RANDOM_IMAGE);
                        url = "./assets/images/" + randomImageIndex + ".png";
                        image = new Image();
                        return [4, new Promise(function (resolve) {
                                image.onload = function () { return resolve(image); };
                                image.src = url;
                            })];
                    case 1:
                        _a.sent();
                        this.inputCtx.drawImage(image, 0, 0, image.width, image.height, 0, 0, this.inputCtx.canvas.width, this.inputCtx.canvas.height);
                        return [2];
                }
            });
        });
    };
    class_1.prototype.setState = function (state) {
        return __awaiter(this, void 0, void 0, function () {
            var _this = this;
            var _a;
            return __generator(this, function (_b) {
                switch (_b.label) {
                    case 0:
                        this.state = state;
                        _a = state;
                        switch (_a) {
                            case State.INITIALIZING: return [3, 1];
                            case State.STAND_BY: return [3, 2];
                            case State.RUNNING: return [3, 3];
                            case State.ERROR: return [3, 5];
                        }
                        return [3, 6];
                    case 1:
                        this.setMessage('Initializing...');
                        this.runButton.textContent = 'Initializing...';
                        this.runButton.disabled = true;
                        return [3, 6];
                    case 2:
                        this.setMessage("Ready(backend: " + this.runner.backend + ")");
                        this.runButton.textContent = 'Run';
                        this.runButton.disabled = false;
                        return [3, 6];
                    case 3:
                        this.setMessage('Processing...');
                        this.runButton.disabled = true;
                        return [4, this.transfer()];
                    case 4:
                        _b.sent();
                        if (this.dataSource == 'video') {
                            this.setMessage('Running');
                            this.runButton.textContent = 'Stop';
                            this.runButton.disabled = false;
                        }
                        else {
                            setTimeout(function () { return _this.setState(State.STAND_BY); });
                        }
                        return [3, 6];
                    case 5:
                        this.runButton.textContent = 'Error';
                        this.runButton.disabled = true;
                        return [3, 6];
                    case 6: return [2];
                }
            });
        });
    };
    class_1.prototype.transfer = function () {
        return __awaiter(this, void 0, void 0, function () {
            var _this = this;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        if (this.state !== State.RUNNING)
                            return [2];
                        return [4, this.getImageData()];
                    case 1:
                        _a.sent();
                        if (this.runner.backend === 'webgpu' && this.lastStatus === 'none') {
                            localStorage.setItem(KEY_WEBGPU_LAST_STATUS, 'running');
                            this.lastStatus = 'running';
                        }
                        return [4, this.runner.run()];
                    case 2:
                        _a.sent();
                        if (this.runner.backend === 'webgpu' && this.lastStatus === 'running') {
                            localStorage.setItem(KEY_WEBGPU_LAST_STATUS, 'completed');
                            this.lastStatus = 'completed';
                        }
                        this.setImageData();
                        if (this.dataSource == 'video')
                            requestAnimationFrame(function () { return _this.transfer(); });
                        return [2];
                }
            });
        });
    };
    class_1.prototype.getImageData = function () {
        return __awaiter(this, void 0, void 0, function () {
            var _this = this;
            var w, h, pixelData, y, x;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        w = this.w;
                        h = this.h;
                        if (!(this.dataSource == 'photo')) return [3, 2];
                        return [4, new Promise(function (resolve) {
                                _this.webcam.freeze();
                                _this.webcam.snap(resolve, _this.inputCanvas);
                            })];
                    case 1:
                        _a.sent();
                        return [3, 4];
                    case 2:
                        if (!(this.dataSource == 'video')) return [3, 4];
                        return [4, new Promise(function (resolve) {
                                _this.webcam.snap(resolve, _this.inputCanvas);
                            })];
                    case 3:
                        _a.sent();
                        _a.label = 4;
                    case 4:
                        pixelData = this.inputCtx.getImageData(0, 0, w, h).data;
                        for (y = 0; y < h; y++) {
                            for (x = 0; x < w; x++) {
                                this.inputView[(y * w + x) * 3] = pixelData[(y * w + x) * 4];
                                this.inputView[(y * w + x) * 3 + 1] = pixelData[(y * w + x) * 4 + 1];
                                this.inputView[(y * w + x) * 3 + 2] = pixelData[(y * w + x) * 4 + 2];
                            }
                        }
                        return [2];
                }
            });
        });
    };
    class_1.prototype.setImageData = function () {
        var w = this.w;
        var h = this.h;
        var imageData = new ImageData(w, h);
        for (var y = 0; y < h; y++) {
            for (var x = 0; x < w; x++) {
                imageData.data[(y * w + x) * 4] = this.outputView[(y * w + x) * 3];
                imageData.data[(y * w + x) * 4 + 1] = this.outputView[(y * w + x) * 3 + 1];
                imageData.data[(y * w + x) * 4 + 2] = this.outputView[(y * w + x) * 3 + 2];
                imageData.data[(y * w + x) * 4 + 3] = 255;
            }
        }
        this.outputCtx.putImageData(imageData, 0, 0);
    };
    class_1.prototype.setMessage = function (message) {
        var $message = document.getElementById('message');
        if (!$message)
            return;
        $message.textContent = message;
    };
    return class_1;
}());
window.onload = function () {
    WebDNN.registerTransformDelegate(function (url) {
        var ma = url.match(/([^/]+)(?:\?.*)?$/);
        if (ma) {
            return "https://mil-tokyo.github.io/webdnn-data/models/neural_style_transfer/" + ma[1] + "?raw=true";
        }
        else {
            return url;
        }
    });
    var runAppButton = document.getElementById('runAppButton');
    if (!runAppButton)
        throw Error('#runAppButton is not found');
    runAppButton.addEventListener('click', function () { return App.initialize(); });
    if (location.search == '?run=1') {
        App.initialize();
    }
};


/***/ })
/******/ ]);