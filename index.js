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
/******/ 	return __webpack_require__(__webpack_require__.s = 9);
/******/ })
/************************************************************************/
/******/ ({

/***/ 0:
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

/***/ 6:
/***/ (function(module, exports) {

// removed by extract-text-webpack-plugin

/***/ }),

/***/ 9:
/***/ (function(module, exports, __webpack_require__) {

"use strict";

Object.defineProperty(exports, "__esModule", { value: true });
__webpack_require__(6);
__webpack_require__(0);
var DENSITY = 5000;
var MIN_VX = 0.1;
var MIN_VY = 0.1;
var MAX_VX = 0.3;
var MAX_VY = 0.3;
var PROXIMITY = 100;
var DOT_COLOR = 'rgba(214, 230, 255, 1)';
var LINE_COLOR = 'rgba(214, 230, 255, 0.4)';
var LINE_WIDTH = 0.5;
var RADIUS_HALF = 2;
var PI2 = Math.PI * 2;
var ParticleGround = (function () {
    function ParticleGround(container) {
        var _this = this;
        this.particles = [];
        this.container = container;
        this.canvas = document.createElement('canvas');
        this.canvas.width = this.container.offsetWidth;
        this.canvas.height = this.container.offsetHeight;
        this.canvas.style.display = 'block';
        this.container.insertBefore(this.canvas, this.container.firstChild);
        var ctx = this.canvas.getContext('2d');
        if (!ctx)
            throw Error('Canvas Initialization Failed.');
        this.ctx = ctx;
        this.ctx.fillStyle = DOT_COLOR;
        this.ctx.strokeStyle = LINE_COLOR;
        this.ctx.lineWidth = LINE_WIDTH;
        var numParticles = Math.round((this.canvas.width * this.canvas.height) / DENSITY);
        for (var i = 0; i < numParticles; i++) {
            this.particles.push({
                x: Math.ceil(Math.random() * this.canvas.width),
                y: Math.ceil(Math.random() * this.canvas.height),
                vx: ((MAX_VX - MIN_VX) * Math.random() + MIN_VX) * (Math.random() >= 0.5 ? +1 : -1),
                vy: ((MAX_VY - MIN_VY) * Math.random() + MIN_VY) * (Math.random() >= 0.5 ? +1 : -1),
            });
        }
        window.addEventListener('resize', function () { return _this.resizeHandler(); });
        this.update();
    }
    ParticleGround.prototype.update = function () {
        var _this = this;
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        var containerWidth = this.container.offsetWidth;
        var containerHeight = this.container.offsetHeight;
        for (var i = 0; i < this.particles.length; i++) {
            var p = this.particles[i];
            if (p.x + p.vx > containerWidth || p.x + p.vx < 0)
                p.vx = -p.vx;
            if (p.y + p.vy > containerHeight || p.y + p.vy < 0)
                p.vy = -p.vy;
            p.x += p.vx;
            p.y += p.vy;
        }
        for (var i = 0; i < this.particles.length; i++) {
            var p1 = this.particles[i];
            this.ctx.beginPath();
            this.ctx.arc(p1.x, p1.y, RADIUS_HALF, 0, PI2, true);
            this.ctx.closePath();
            this.ctx.fill();
            this.ctx.beginPath();
            for (var j = i; j < this.particles.length; j++) {
                var p2 = this.particles[j];
                var dx = p1.x - p2.x;
                var dy = p2.y - p2.y;
                if (Math.sqrt((dx * dx) + (dy * dy)) < PROXIMITY) {
                    this.ctx.moveTo(p1.x, p1.y);
                    this.ctx.lineTo(p2.x, p2.y);
                }
            }
            this.ctx.stroke();
            this.ctx.closePath();
        }
        requestAnimationFrame(function () { return _this.update(); });
    };
    ParticleGround.prototype.resizeHandler = function () {
        var containerWidth = this.canvas.width = this.container.offsetWidth;
        var containerHeight = this.canvas.height = this.container.offsetHeight;
        this.ctx.fillStyle = DOT_COLOR;
        this.ctx.strokeStyle = LINE_COLOR;
        this.ctx.lineWidth = LINE_WIDTH;
        for (var i = this.particles.length - 1; i >= 0; i--) {
            if (this.particles[i].x > containerWidth || this.particles[i].y > containerHeight) {
                this.particles.splice(i, 1);
            }
        }
        var numParticles = Math.round((this.canvas.width * this.canvas.height) / DENSITY);
        while (this.particles.length < numParticles) {
            this.particles.push({
                x: Math.ceil(Math.random() * this.canvas.width),
                y: Math.ceil(Math.random() * this.canvas.height),
                vx: ((MAX_VX - MIN_VX) * Math.random() + MIN_VX) * (Math.random() >= 0.5 ? +1 : -1),
                vy: ((MAX_VY - MIN_VY) * Math.random() + MIN_VY) * (Math.random() >= 0.5 ? +1 : -1),
            });
        }
        if (this.particles.length > numParticles) {
            this.particles.splice(numParticles);
        }
    };
    return ParticleGround;
}());
window.onload = function () {
    var availability = {
        'webgpu': ('WebGPUComputeCommandEncoder' in window),
        'webassembly': ('Worker' in window),
        'fallback': true
    };
    for (var _i = 0, _a = ['webgpu', 'webassembly', 'fallback']; _i < _a.length; _i++) {
        var backend = _a[_i];
        for (var _b = 0, _c = Array.from(document.querySelectorAll(".Compatibility-ThisBrowserTable .Compatibility-" + backend)); _b < _c.length; _b++) {
            var node = _c[_b];
            node.classList.remove('Compatibility-checking');
            var statusNode = node.querySelector('.Compatibility-Status');
            if (availability[backend]) {
                node.classList.add('Compatibility-supported');
                node.classList.remove('Compatibility-not_supported');
                if (statusNode)
                    statusNode.textContent = 'Supported';
            }
            else {
                node.classList.remove('Compatibility-supported');
                node.classList.add('Compatibility-not_supported');
                if (statusNode)
                    statusNode.textContent = 'Not supported';
            }
        }
    }
    var IS_ES2017 = true;
    try {
        eval('(() => { async function test(){return Promise.resolve());} })();');
    }
    catch (e) {
        IS_ES2017 = false;
    }
    var iframes = document.querySelectorAll('iframe');
    for (var i = 0; i < iframes.length; i++) {
        var iframe = iframes[i];
        var baseUrl = iframe.dataset['src'];
        if (!baseUrl)
            throw Error('baseUrl is not found');
        iframe.src = IS_ES2017 ? baseUrl : baseUrl.replace('.html', '.es5.html');
    }
    var splash = document.getElementById('splash');
    if (!splash)
        throw Error('#splash is not found.');
    new ParticleGround(splash);
    if ('serviceWorker' in navigator)
        navigator.serviceWorker.register('/webdnn/sw.js');
};


/***/ })

/******/ });