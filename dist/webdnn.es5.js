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
/*
MIT License

Copyright (c) 2017 Machine Intelligence Laboratory (The University of Tokyo)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/
/// <reference path="../graph_descriptor/graph_descriptor.ts" />
var WebDNN;
(function (WebDNN) {
    /**
     * `DescriptorRunner` executes computation based on `GraphDescriptor`.
     */
    var DescriptorRunner = (function () {
        function DescriptorRunner() {
            this.descriptor = null;
            this.ignoreCache = false;
        }
        return DescriptorRunner;
    }());
    WebDNN.DescriptorRunner = DescriptorRunner;
})(WebDNN || (WebDNN = {}));
///<reference path="../descriptor_runner/descriptor_runner.ts" />
var WebDNN;
(function (WebDNN) {
    var GPUInterface = (function () {
        function GPUInterface(option) {
        }
        return GPUInterface;
    }());
    WebDNN.GPUInterface = GPUInterface;
})(WebDNN || (WebDNN = {}));
var WebDNN;
(function (WebDNN) {
    /**
     * Abstract buffer interface. Read/write transactions are regarded as asynchronous operation.
     */
    var Buffer = (function () {
        function Buffer(byteLength, backed) {
            this.byteLength = byteLength;
            this.backed = backed;
        }
        return Buffer;
    }());
    WebDNN.Buffer = Buffer;
})(WebDNN || (WebDNN = {}));
/// <reference path="./buffer.ts" />
var WebDNN;
(function (WebDNN) {
    var BufferWebGPU = (function (_super) {
        __extends(BufferWebGPU, _super);
        function BufferWebGPU(byteLength) {
            var _this = _super.call(this, byteLength, 'webgpu') || this;
            if (byteLength == 0) {
                byteLength = 4; //0 length buffer causes error
            }
            _this.buffer = BufferWebGPU.webgpuHandler.createBuffer(new Uint8Array(byteLength));
            _this.bufferView = new Uint8Array(_this.buffer.contents);
            return _this;
        }
        // async: there may be platforms synchronization is needed before writing
        BufferWebGPU.prototype.write = function (src, dst_offset) {
            return __awaiter(this, void 0, void 0, function () {
                var viewSameType;
                return __generator(this, function (_a) {
                    switch (_a.label) {
                        case 0: return [4 /*yield*/, BufferWebGPU.webgpuHandler.sync()];
                        case 1:
                            _a.sent();
                            viewSameType = new src.constructor(this.bufferView.buffer);
                            viewSameType.set(src, dst_offset);
                            return [2 /*return*/];
                    }
                });
            });
        };
        BufferWebGPU.prototype.read = function (dst, src_offset, length) {
            if (src_offset === void 0) { src_offset = 0; }
            return __awaiter(this, void 0, void 0, function () {
                var dst_constructor, viewSameType;
                return __generator(this, function (_a) {
                    switch (_a.label) {
                        case 0:
                            if (!dst) {
                                throw new Error('dst cannot be null');
                            }
                            return [4 /*yield*/, BufferWebGPU.webgpuHandler.sync()];
                        case 1:
                            _a.sent();
                            if (this.byteLength === 0) {
                                // nothing to read
                                return [2 /*return*/];
                            }
                            dst_constructor = dst.constructor;
                            viewSameType = new dst_constructor(this.bufferView.buffer, this.bufferView.byteOffset + src_offset * dst_constructor.BYTES_PER_ELEMENT, length);
                            if (length === undefined) {
                                length = viewSameType.length - src_offset;
                            }
                            dst.set(viewSameType);
                            return [2 /*return*/];
                    }
                });
            });
        };
        BufferWebGPU.init = function (webgpuHandler) {
            this.webgpuHandler = webgpuHandler;
        };
        BufferWebGPU.prototype.getWriteView = function (offset, length, number_type) {
            var viewSameType = new number_type(this.bufferView.buffer, this.bufferView.byteOffset + offset * number_type.BYTES_PER_ELEMENT, length);
            return viewSameType;
        };
        BufferWebGPU.prototype.getReadView = function (offset, length, number_type) {
            var viewSameType = new number_type(this.bufferView.buffer, this.bufferView.byteOffset + offset * number_type.BYTES_PER_ELEMENT, length);
            return viewSameType;
        };
        BufferWebGPU.prototype.syncWriteViews = function () {
            return __awaiter(this, void 0, void 0, function () {
                return __generator(this, function (_a) {
                    return [2 /*return*/];
                });
            });
        };
        BufferWebGPU.prototype.syncReadViews = function () {
            return __awaiter(this, void 0, void 0, function () {
                return __generator(this, function (_a) {
                    switch (_a.label) {
                        case 0: 
                        // if the user awaits promise from final kernel execution, this function call is not needed.
                        return [4 /*yield*/, BufferWebGPU.webgpuHandler.sync()];
                        case 1:
                            // if the user awaits promise from final kernel execution, this function call is not needed.
                            _a.sent();
                            return [2 /*return*/];
                    }
                });
            });
        };
        return BufferWebGPU;
    }(WebDNN.Buffer));
    WebDNN.BufferWebGPU = BufferWebGPU;
})(WebDNN || (WebDNN = {}));
/// <reference path="./buffer/buffer_webgpu.ts" />
var WebDNN;
(function (WebDNN) {
    var WebGPUHandler = (function () {
        function WebGPUHandler() {
        }
        WebGPUHandler.prototype.init = function () {
            return __awaiter(this, void 0, void 0, function () {
                return __generator(this, function (_a) {
                    // asynchronous operation may be added in future
                    if (!WebGPUHandler.isBrowserSupported) {
                        throw new Error('This browser does not support WebGPU');
                    }
                    this.context = document.createElement('canvas').getContext('webgpu'); //force cast
                    this.commandQueue = this.context.createCommandQueue();
                    this.pipelineStates = new Map();
                    return [2 /*return*/];
                });
            });
        };
        WebGPUHandler.prototype.createBuffer = function (arrayBuffer) {
            return this.context.createBuffer(arrayBuffer);
        };
        WebGPUHandler.prototype.loadKernel = function (librarySource, namespace) {
            if (namespace === void 0) { namespace = ''; }
            var library = this.context.createLibrary(librarySource);
            for (var _i = 0, _a = library.functionNames; _i < _a.length; _i++) {
                var name_1 = _a[_i];
                var kernelFunction = library.functionWithName(name_1);
                var pipelineStates = this.context.createComputePipelineState(kernelFunction);
                this.pipelineStates.set(namespace + '.' + name_1, pipelineStates);
            }
        };
        WebGPUHandler.prototype.createCommandBuffer = function () {
            return this.commandQueue.createCommandBuffer();
        };
        WebGPUHandler.prototype.getPipelineStateByName = function (name) {
            var state = this.pipelineStates.get(name);
            if (!state) {
                throw TypeError("Kernel function \"" + name + "\" is not loaded.");
            }
            return state;
        };
        WebGPUHandler.prototype.executeSinglePipelineState = function (name, threadgroupsPerGrid, threadsPerThreadgroup, buffers, getCompletedPromise) {
            var commandBuffer = this.createCommandBuffer();
            var commandEncoder = commandBuffer.createComputeCommandEncoder();
            commandEncoder.setComputePipelineState(this.getPipelineStateByName(name));
            for (var i = 0; i < buffers.length; i++) {
                var buffer = buffers[i];
                var wgbuf = void 0;
                if (buffer instanceof WebDNN.BufferWebGPU) {
                    wgbuf = buffer.buffer;
                }
                else {
                    // cannot perform (buffer instanceof WebGPUBuffer) currently
                    wgbuf = buffer;
                }
                commandEncoder.setBuffer(wgbuf, 0, i);
            }
            commandEncoder.dispatch(threadgroupsPerGrid, threadsPerThreadgroup);
            commandEncoder.endEncoding();
            var promise = null;
            if (getCompletedPromise) {
                promise = commandBuffer.completed;
            }
            commandBuffer.commit();
            return promise;
        };
        WebGPUHandler.prototype.sync = function () {
            return __awaiter(this, void 0, void 0, function () {
                var commandBuffer, commandEncoder, promise;
                return __generator(this, function (_a) {
                    commandBuffer = this.createCommandBuffer();
                    commandEncoder = commandBuffer.createComputeCommandEncoder();
                    commandEncoder.setComputePipelineState(this.getPipelineStateByName('basic.sync'));
                    commandEncoder.dispatch({
                        width: 1,
                        height: 1,
                        depth: 1
                    }, {
                        width: 1,
                        height: 1,
                        depth: 1
                    });
                    commandEncoder.endEncoding();
                    promise = commandBuffer.completed;
                    commandBuffer.commit();
                    return [2 /*return*/, promise];
                });
            });
        };
        return WebGPUHandler;
    }());
    WebDNN.WebGPUHandler = WebGPUHandler;
    WebGPUHandler.isBrowserSupported = 'WebGPURenderingContext' in window && 'WebGPUComputeCommandEncoder' in window;
})(WebDNN || (WebDNN = {}));
///<reference path="./weight_decoder.ts" />
var WebDNN;
(function (WebDNN) {
    var WeightDecoderRaw = (function () {
        function WeightDecoderRaw() {
        }
        WeightDecoderRaw.prototype.decode = function (data, memory_layout) {
            return __awaiter(this, void 0, void 0, function () {
                return __generator(this, function (_a) {
                    return [2 /*return*/, new Float32Array(data.buffer, data.byteOffset, data.byteLength / 4)];
                });
            });
        };
        return WeightDecoderRaw;
    }());
    WebDNN.WeightDecoderRaw = WeightDecoderRaw;
})(WebDNN || (WebDNN = {}));
///<reference path="./weight_decoder_raw.ts" />
///<reference path="./weight_decoder.ts" />
var WebDNN;
(function (WebDNN) {
    var WeightDecoderEightbit = (function () {
        function WeightDecoderEightbit() {
        }
        WeightDecoderEightbit.prototype.decode = function (data, memory_layout) {
            return __awaiter(this, void 0, void 0, function () {
                var dst, data_view, src_offset, dst_offset, body_size, scale, scaled_table, i, src_data_view, inflate, decompressed, dec_size, s;
                return __generator(this, function (_a) {
                    dst = new Float32Array(memory_layout.total_size);
                    data_view = new DataView(data.buffer, data.byteOffset);
                    src_offset = 0;
                    while (src_offset < data.length) {
                        dst_offset = data_view.getInt32(src_offset, true);
                        src_offset += 4;
                        body_size = data_view.getInt32(src_offset, true);
                        src_offset += 4;
                        scale = data_view.getFloat32(src_offset, true);
                        src_offset += 8;
                        scaled_table = new Float32Array(256);
                        for (i = 0; i < 256; i++) {
                            scaled_table[i] = WeightDecoderEightbit.decode_table[i & 0x7F] * scale * (i < 128 ? 1.0 : -1.0);
                        }
                        src_data_view = new Uint8Array(data.buffer, data.byteOffset + src_offset, body_size);
                        inflate = new Zlib.Inflate(src_data_view);
                        decompressed = inflate.decompress();
                        dec_size = decompressed.length;
                        for (s = 0; s < dec_size; s++) {
                            dst[dst_offset++] = scaled_table[decompressed[s]];
                        }
                        src_offset += body_size;
                    }
                    return [2 /*return*/, dst];
                });
            });
        };
        return WeightDecoderEightbit;
    }());
    WeightDecoderEightbit.decode_table = [0.0, 2.750000021e-06, 7.249999726e-06, 1.875000089e-05, 3.624999954e-05, 5.874999624e-05, 8.624999464e-05,
        1.437500032e-04, 2.312500001e-04, 3.187500115e-04, 4.062500084e-04, 5.187499919e-04, 6.562499912e-04,
        7.937499322e-04, 9.312499315e-04, 1.218750025e-03, 1.656249980e-03, 2.093750052e-03, 2.531250007e-03,
        2.968749963e-03, 3.406249918e-03, 3.843750106e-03, 4.281249829e-03, 4.843750037e-03, 5.531250034e-03,
        6.218749564e-03, 6.906249560e-03, 7.593749557e-03, 8.281249553e-03, 8.968749084e-03, 9.656248614e-03,
        1.109374966e-02, 1.328125037e-02, 1.546875015e-02, 1.765624993e-02, 1.984374970e-02, 2.203124948e-02,
        2.421874925e-02, 2.640625089e-02, 2.859375067e-02, 3.078125045e-02, 3.296874836e-02, 3.515625000e-02,
        3.734375164e-02, 3.953124955e-02, 4.171875119e-02, 4.390624911e-02, 4.671875015e-02, 5.015625060e-02,
        5.359374732e-02, 5.703124776e-02, 6.046874821e-02, 6.390624493e-02, 6.734374911e-02, 7.078124583e-02,
        7.421874255e-02, 7.765624672e-02, 8.109374344e-02, 8.453124017e-02, 8.796874434e-02, 9.140624106e-02,
        9.484373778e-02, 9.828124195e-02, 1.054687500e-01, 1.164062470e-01, 1.273437440e-01, 1.382812560e-01,
        1.492187530e-01, 1.601562500e-01, 1.710937470e-01, 1.820312440e-01, 1.929687560e-01, 2.039062530e-01,
        2.148437500e-01, 2.257812470e-01, 2.367187440e-01, 2.476562560e-01, 2.585937381e-01, 2.695312500e-01,
        2.804687619e-01, 2.914062440e-01, 3.023437560e-01, 3.132812381e-01, 3.242187500e-01, 3.351562619e-01,
        3.460937440e-01, 3.570312560e-01, 3.679687381e-01, 3.789062500e-01, 3.898437619e-01, 4.007812440e-01,
        4.117187560e-01, 4.226562381e-01, 4.335937500e-01, 4.445312619e-01, 4.585937560e-01, 4.757812321e-01,
        4.929687381e-01, 5.101562142e-01, 5.273437500e-01, 5.445312262e-01, 5.617187023e-01, 5.789062381e-01,
        5.960937142e-01, 6.132812500e-01, 6.304687262e-01, 6.476562023e-01, 6.648437381e-01, 6.820312142e-01,
        6.992186904e-01, 7.164062262e-01, 7.335937023e-01, 7.507811785e-01, 7.679687142e-01, 7.851561904e-01,
        8.023436666e-01, 8.195312023e-01, 8.367186785e-01, 8.539061546e-01, 8.710936904e-01, 8.882811666e-01,
        9.054686427e-01, 9.226561785e-01, 9.398436546e-01, 9.570311308e-01, 9.742186666e-01, 9.914061427e-01, 1.0,
    ];
    WebDNN.WeightDecoderEightbit = WeightDecoderEightbit;
})(WebDNN || (WebDNN = {}));
///<reference path="./weight_decoder.ts" />
///<reference path="./weight_decoder_raw.ts" />
///<reference path="./weight_decoder_eightbit.ts" />
var WebDNN;
(function (WebDNN) {
    function get_weight_decoder(name) {
        switch (name) {
            case 'raw':
                return new WebDNN.WeightDecoderRaw();
            case 'eightbit':
                return new WebDNN.WeightDecoderEightbit();
            default:
                throw new Error('Unknown weight encoding');
        }
    }
    WebDNN.get_weight_decoder = get_weight_decoder;
})(WebDNN || (WebDNN = {}));
var WebDNN;
(function (WebDNN) {
    var util;
    (function (util) {
        var NOT_SCHEDULED = -1;
        /**
         *  Schedule function which is called too much frequently.
         */
        var DispatchScheduler = (function () {
            function DispatchScheduler() {
                this.scheduledCallbackId = NOT_SCHEDULED;
            }
            /**
             * Register scheduled function. If already other function is scheduled, it is canceled and dispatcher will dispatch only
             * function which is registered at last.
             * @param fn scheduled function
             */
            DispatchScheduler.prototype.request = function (fn) {
                var _this = this;
                this.fn = fn;
                if (this.scheduledCallbackId == NOT_SCHEDULED) {
                    this.scheduledCallbackId = requestAnimationFrame(function () { return _this.forceDispatch(); });
                }
            };
            /**
             * Dispatch scheduled function just now. If no function is scheduled, dispatcher do nothing.
             */
            DispatchScheduler.prototype.forceDispatch = function () {
                if (this.scheduledCallbackId == NOT_SCHEDULED)
                    return;
                this.cancel();
                this.fn();
            };
            /**
             * Cancel scheduled function. If no function is scheduled, dispatcher do nothing.
             */
            DispatchScheduler.prototype.cancel = function () {
                if (this.scheduledCallbackId == NOT_SCHEDULED)
                    return;
                cancelAnimationFrame(this.scheduledCallbackId);
                this.scheduledCallbackId = NOT_SCHEDULED;
            };
            return DispatchScheduler;
        }());
        util.DispatchScheduler = DispatchScheduler;
    })(util = WebDNN.util || (WebDNN.util = {}));
})(WebDNN || (WebDNN = {}));
/// <reference path="./util/dispatch_scheduler.ts" />
var transformDelegate = function (url) { return url; };
/**
 * Fetch delegate function.
 * Every fetch call in WebDNN is delegated to this function.
 * As default, `window.fetch` is set.
 * @type {(input:RequestInfo, init?:RequestInit)=>Promise<Response>}
 */
var fetchDelegate = window.fetch;
var WebDNN;
(function (WebDNN) {
    /**
     * Register delegate function for transform url
     * @param url url which will be transformed
     */
    function transformUrl(url) {
        return transformDelegate(url);
    }
    WebDNN.transformUrl = transformUrl;
    /**
     * Register delegate function for transform url
     * @param delegate delegate function
     */
    function registerTransformDelegate(delegate) {
        transformDelegate = delegate;
    }
    WebDNN.registerTransformDelegate = registerTransformDelegate;
    /**
     * Register delegate function for fetch
     * @param delegate delegate function
     */
    function registerFetchDelegate(delegate) {
        fetchDelegate = delegate;
    }
    WebDNN.registerFetchDelegate = registerFetchDelegate;
    /**
     * Fetch function. WebDNN API use this fetch function instead of original fetch function.
     * @param input Requested url
     * @param init Additional information about fetch
     * @returns Response
     */
    function fetch(input, init) {
        return fetchDelegate(input, init);
    }
    WebDNN.fetch = fetch;
    /**
     * Read `Response.body` stream as ArrayBuffer. This function provide progress information by callback.
     * @param res Response object
     * @param callback Callback function.
     * @returns ArrayBuffer
     */
    function readArrayBufferProgressively(res, callback) {
        if (!callback || !res.body)
            return res.arrayBuffer();
        var contentLength = res.headers.get('Content-Length');
        if (!contentLength)
            return res.arrayBuffer();
        var total = parseInt(contentLength);
        var buffer = new Uint8Array(total);
        var loaded = 0;
        var reader = res.body.getReader();
        var callbackScheduler = new WebDNN.util.DispatchScheduler();
        function accumulateLoadedSize(chunk) {
            buffer.set(chunk.value, loaded);
            loaded += chunk.value.length;
            if (callback) {
                callbackScheduler.request(function () { return callback(loaded, total); });
            }
            if (loaded == total) {
                callbackScheduler.forceDispatch();
                return buffer.buffer;
            }
            else {
                return reader.read().then(accumulateLoadedSize);
            }
        }
        return reader.read().then(accumulateLoadedSize);
    }
    WebDNN.readArrayBufferProgressively = readArrayBufferProgressively;
})(WebDNN || (WebDNN = {}));
/// <reference path="./graph_descriptor.ts" />
/// <reference path="../buffer/buffer_webgpu.ts" />
/// <reference path="../webgpu_handler.ts" />
/// <reference path="./descriptor_runner.ts" />
/// <reference path="../decoder/get_weight_decoder.ts" />
/// <reference path="../fetch.ts" />
/// <reference path="../graph_descriptor/graph_descriptor_webgpu.ts" />
var WebDNN;
(function (WebDNN) {
    var DescriptorRunnerWebGPU = (function (_super) {
        __extends(DescriptorRunnerWebGPU, _super);
        function DescriptorRunnerWebGPU(gpuHandler) {
            var _this = _super.call(this) || this;
            _this.gpuHandler = gpuHandler;
            _this.backendName = 'webgpu';
            return _this;
        }
        DescriptorRunnerWebGPU.prototype.load = function (directory, progressCallback) {
            return __awaiter(this, void 0, void 0, function () {
                var graph_url, graph_fetch, _a, weight_url, weights_data_ab, _b;
                return __generator(this, function (_c) {
                    switch (_c.label) {
                        case 0:
                            graph_url = directory + "/graph_" + this.backendName + ".json";
                            if (this.ignoreCache) {
                                graph_url += '?t=' + Date.now();
                            }
                            graph_url = WebDNN.transformUrl(graph_url);
                            return [4 /*yield*/, WebDNN.fetch(graph_url)];
                        case 1:
                            graph_fetch = _c.sent();
                            if (!graph_fetch.ok) {
                                throw new Error(graph_url + " cannot be loaded");
                            }
                            _a = this;
                            return [4 /*yield*/, graph_fetch.json()];
                        case 2:
                            _a.descriptor = _c.sent();
                            return [4 /*yield*/, this.compile()];
                        case 3:
                            _c.sent();
                            weight_url = directory + "/weight_" + this.backendName + ".bin";
                            if (this.ignoreCache) {
                                weight_url += '?t=' + Date.now();
                            }
                            weight_url = WebDNN.transformUrl(weight_url);
                            _b = WebDNN.readArrayBufferProgressively;
                            return [4 /*yield*/, WebDNN.fetch(weight_url, progressCallback)];
                        case 4: return [4 /*yield*/, _b.apply(void 0, [_c.sent(), progressCallback])];
                        case 5:
                            weights_data_ab = _c.sent();
                            return [4 /*yield*/, this.loadWeights(new Uint8Array(weights_data_ab))];
                        case 6:
                            _c.sent();
                            return [2 /*return*/];
                    }
                });
            });
        };
        DescriptorRunnerWebGPU.prototype.setDescriptor = function (descriptor) {
            this.descriptor = descriptor;
        };
        DescriptorRunnerWebGPU.prototype.compile = function () {
            return __awaiter(this, void 0, void 0, function () {
                var i, exec_info, buf;
                return __generator(this, function (_a) {
                    switch (_a.label) {
                        case 0:
                            if (!this.descriptor)
                                throw new Error('Descriptor is not loaded');
                            this.gpuHandler.loadKernel(this.descriptor.kernel_source, 'descriptor');
                            this.dataBuffer = new WebDNN.BufferWebGPU(this.descriptor.memory_layout.total_size * Float32Array.BYTES_PER_ELEMENT);
                            this.metaBuffers = [];
                            i = 0;
                            _a.label = 1;
                        case 1:
                            if (!(i < this.descriptor.exec_infos.length)) return [3 /*break*/, 4];
                            exec_info = this.descriptor.exec_infos[i];
                            buf = new WebDNN.BufferWebGPU(exec_info.meta_buffer.length * Float32Array.BYTES_PER_ELEMENT);
                            return [4 /*yield*/, buf.write(new Uint8Array(exec_info.meta_buffer))];
                        case 2:
                            _a.sent();
                            this.metaBuffers.push(buf);
                            _a.label = 3;
                        case 3:
                            i++;
                            return [3 /*break*/, 1];
                        case 4: return [2 /*return*/];
                    }
                });
            });
        };
        DescriptorRunnerWebGPU.prototype.loadWeights = function (data) {
            return __awaiter(this, void 0, void 0, function () {
                var decoder, _a, _b;
                return __generator(this, function (_c) {
                    switch (_c.label) {
                        case 0:
                            if (!this.descriptor)
                                throw new Error('Descriptor is not loaded');
                            if (!this.dataBuffer)
                                throw new Error('Data buffer is not initialized');
                            decoder = WebDNN.get_weight_decoder(this.descriptor.weight_encoding);
                            _b = (_a = this.dataBuffer).write;
                            return [4 /*yield*/, decoder.decode(data, this.descriptor.memory_layout)];
                        case 1: return [4 /*yield*/, _b.apply(_a, [_c.sent()])];
                        case 2:
                            _c.sent();
                            return [2 /*return*/];
                    }
                });
            });
        };
        DescriptorRunnerWebGPU.prototype.getInputViews = function () {
            return __awaiter(this, void 0, void 0, function () {
                var views, i, var_alloc;
                return __generator(this, function (_a) {
                    if (this.inputViews)
                        return [2 /*return*/, this.inputViews];
                    if (!this.descriptor)
                        throw new Error('Descriptor is not loaded');
                    if (!this.dataBuffer)
                        throw new Error('Data buffer is not initialized');
                    views = [];
                    for (i = 0; i < this.descriptor.inputs.length; i++) {
                        var_alloc = this.descriptor.memory_layout.allocations[this.descriptor.inputs[i]];
                        views.push(this.dataBuffer.getWriteView(var_alloc.offset, var_alloc.size, Float32Array));
                    }
                    this.inputViews = views;
                    return [2 /*return*/, views];
                });
            });
        };
        DescriptorRunnerWebGPU.prototype.getOutputViews = function () {
            return __awaiter(this, void 0, void 0, function () {
                var views, i, var_alloc;
                return __generator(this, function (_a) {
                    if (this.outputViews)
                        return [2 /*return*/, this.outputViews];
                    if (!this.descriptor)
                        throw new Error('Descriptor is not loaded');
                    if (!this.dataBuffer)
                        throw new Error('Data buffer is not initialized');
                    views = [];
                    for (i = 0; i < this.descriptor.outputs.length; i++) {
                        var_alloc = this.descriptor.memory_layout.allocations[this.descriptor.outputs[i]];
                        views.push(this.dataBuffer.getReadView(var_alloc.offset, var_alloc.size, Float32Array));
                    }
                    this.outputViews = views;
                    return [2 /*return*/, views];
                });
            });
        };
        DescriptorRunnerWebGPU.prototype.run = function () {
            return __awaiter(this, void 0, void 0, function () {
                var dataBuffer, metaBuffers, records, totalElapsedTime_1, i, exec_info, start, elapsedTime, summary, complete_promise, i, exec_info, is_last;
                return __generator(this, function (_a) {
                    switch (_a.label) {
                        case 0:
                            if (!this.descriptor)
                                throw new Error('Descriptor is not loaded');
                            if (!this.inputViews || !this.outputViews)
                                throw new Error('getInputViews and getOutputViews must be called prior to run');
                            if (!this.dataBuffer)
                                throw new Error('Data buffer is not initialized');
                            if (!this.metaBuffers)
                                throw new Error('Meta buffer is not initialized');
                            dataBuffer = this.dataBuffer;
                            metaBuffers = this.metaBuffers;
                            if (!window['PROFILE']) return [3 /*break*/, 5];
                            records = [];
                            totalElapsedTime_1 = 0;
                            i = 0;
                            _a.label = 1;
                        case 1:
                            if (!(i < this.descriptor.exec_infos.length)) return [3 /*break*/, 4];
                            exec_info = this.descriptor.exec_infos[i];
                            start = performance.now();
                            return [4 /*yield*/, this.gpuHandler.executeSinglePipelineState('descriptor.' + exec_info.entry_func_name, exec_info.threadgroups_per_grid, exec_info.threads_per_thread_group, [dataBuffer, metaBuffers[i]], true)];
                        case 2:
                            _a.sent();
                            elapsedTime = performance.now() - start;
                            records.push({
                                'Kernel': exec_info.entry_func_name,
                                'Elapsed time [ms]': elapsedTime
                            });
                            totalElapsedTime_1 += elapsedTime;
                            _a.label = 3;
                        case 3:
                            i++;
                            return [3 /*break*/, 1];
                        case 4:
                            summary = Array.from(Object.values(records.reduce(function (summary, record) {
                                if (!(record['Kernel'] in summary)) {
                                    summary[record['Kernel']] = {
                                        'Kernel': record['Kernel'],
                                        'Count': 0,
                                        'Elapsed time [ms]': 0,
                                    };
                                }
                                summary[record['Kernel']]['Count']++;
                                summary[record['Kernel']]['Elapsed time [ms]'] += record['Elapsed time [ms]'];
                                return summary;
                            }, {})));
                            summary.forEach(function (record) { return record['Ratio [%]'] = (record['Elapsed time [ms]'] / totalElapsedTime_1).toFixed(2); });
                            console.table(records);
                            console.table(summary);
                            return [3 /*break*/, 7];
                        case 5:
                            complete_promise = null;
                            for (i = 0; i < this.descriptor.exec_infos.length; i++) {
                                exec_info = this.descriptor.exec_infos[i];
                                is_last = i == this.descriptor.exec_infos.length - 1;
                                complete_promise = this.gpuHandler.executeSinglePipelineState('descriptor.' + exec_info.entry_func_name, exec_info.threadgroups_per_grid, exec_info.threads_per_thread_group, [dataBuffer, metaBuffers[i]], is_last);
                            }
                            return [4 /*yield*/, complete_promise];
                        case 6:
                            _a.sent(); //wait to finish final kernel
                            _a.label = 7;
                        case 7: return [2 /*return*/];
                    }
                });
            });
        };
        return DescriptorRunnerWebGPU;
    }(WebDNN.DescriptorRunner));
    WebDNN.DescriptorRunnerWebGPU = DescriptorRunnerWebGPU;
})(WebDNN || (WebDNN = {}));
/// <reference path="../descriptor_runner/descriptor_runner_webgpu.ts" />
var WebDNN;
(function (WebDNN) {
    var GPUInterfaceWebGPU = (function (_super) {
        __extends(GPUInterfaceWebGPU, _super);
        function GPUInterfaceWebGPU(option) {
            var _this = _super.call(this, option) || this;
            _this.backendName = 'webgpu';
            if (!WebDNN.WebGPUHandler.isBrowserSupported) {
                throw new Error('WebGPU is not supported on this browser');
            }
            return _this;
        }
        GPUInterfaceWebGPU.prototype.init = function () {
            return __awaiter(this, void 0, void 0, function () {
                return __generator(this, function (_a) {
                    switch (_a.label) {
                        case 0:
                            // initialize webgpu, build kernels
                            this.shaderLanguage = 'metal';
                            this.webgpuHandler = new WebDNN.WebGPUHandler();
                            return [4 /*yield*/, this.webgpuHandler.init()];
                        case 1:
                            _a.sent();
                            WebDNN.BufferWebGPU.init(this.webgpuHandler);
                            this.init_basic_kernels();
                            return [2 /*return*/];
                    }
                });
            });
        };
        GPUInterfaceWebGPU.prototype.init_basic_kernels = function () {
            this.webgpuHandler.loadKernel('kernel void sync(){}', 'basic');
        };
        GPUInterfaceWebGPU.prototype.createDescriptorRunner = function () {
            return new WebDNN.DescriptorRunnerWebGPU(this.webgpuHandler);
        };
        return GPUInterfaceWebGPU;
    }(WebDNN.GPUInterface));
    WebDNN.GPUInterfaceWebGPU = GPUInterfaceWebGPU;
})(WebDNN || (WebDNN = {}));
/// <reference path="./graph_descriptor.ts" />
/// <reference path="../webgpu_handler.ts" />
/// <reference path="./descriptor_runner.ts" />
/// <reference path="../decoder/get_weight_decoder.ts" />
/// <reference path="../fetch.ts" />
/// <reference path="../graph_descriptor/graph_descriptor_webassembly.ts" />
var WebDNN;
(function (WebDNN) {
    var DescriptorRunnerWebassembly = (function (_super) {
        __extends(DescriptorRunnerWebassembly, _super);
        function DescriptorRunnerWebassembly() {
            var _this = _super !== null && _super.apply(this, arguments) || this;
            _this.backendName = 'webassembly';
            _this.worker_promise_reject_func = null;
            _this.worker_initial_error = null;
            return _this;
        }
        DescriptorRunnerWebassembly.prototype.load = function (directory, progressCallback) {
            return __awaiter(this, void 0, void 0, function () {
                var graph_url, graph_fetch, _a, kernel_backend, worker_entry_js_path, weight_url, weights_data_ab, _b;
                return __generator(this, function (_c) {
                    switch (_c.label) {
                        case 0:
                            graph_url = directory + "/graph_" + this.backendName + ".json";
                            if (this.ignoreCache) {
                                graph_url += '?t=' + Date.now();
                            }
                            graph_url = WebDNN.transformUrl(graph_url);
                            return [4 /*yield*/, WebDNN.fetch(graph_url)];
                        case 1:
                            graph_fetch = _c.sent();
                            if (!graph_fetch.ok) {
                                throw new Error(graph_url + " cannot be loaded");
                            }
                            _a = this;
                            return [4 /*yield*/, graph_fetch.json()];
                        case 2:
                            _a.descriptor = _c.sent();
                            kernel_backend = typeof WebAssembly === 'object' ? 'webassembly' : 'asmjs';
                            worker_entry_js_path = directory + "/kernels_" + kernel_backend + ".js";
                            if (this.ignoreCache) {
                                worker_entry_js_path += '?t=' + Date.now();
                            }
                            worker_entry_js_path = WebDNN.transformUrl(worker_entry_js_path);
                            this.worker_entry_js_path = worker_entry_js_path;
                            return [4 /*yield*/, this.compile()];
                        case 3:
                            _c.sent();
                            weight_url = directory + "/weight_" + this.backendName + ".bin";
                            if (this.ignoreCache) {
                                weight_url += '?t=' + Date.now();
                            }
                            weight_url = WebDNN.transformUrl(weight_url);
                            _b = WebDNN.readArrayBufferProgressively;
                            return [4 /*yield*/, WebDNN.fetch(weight_url)];
                        case 4: return [4 /*yield*/, _b.apply(void 0, [_c.sent(), progressCallback])];
                        case 5:
                            weights_data_ab = _c.sent();
                            return [4 /*yield*/, this.loadWeights(new Uint8Array(weights_data_ab))];
                        case 6:
                            _c.sent();
                            return [2 /*return*/];
                    }
                });
            });
        };
        DescriptorRunnerWebassembly.prototype.setDescriptor = function (descriptor) {
            this.descriptor = descriptor;
        };
        DescriptorRunnerWebassembly.prototype.compile = function () {
            var _this = this;
            var worker = new Worker(this.worker_entry_js_path);
            worker.onerror = function (event) {
                console.error(event);
                // console.error('Worker Exception: ' + event.message);
                if (_this.worker_promise_reject_func) {
                    _this.worker_promise_reject_func(event);
                }
                else {
                    _this.worker_initial_error = event;
                }
            };
            var promise = new Promise(function (resolve, reject) {
                // occurs when this.worker_entry_js_path is 404
                if (_this.worker_initial_error)
                    return reject(_this.worker_initial_error);
                _this.worker_promise_reject_func = reject;
                worker.onmessage = function (event) {
                    if (event.data === 0) {
                        resolve();
                    }
                    else {
                        console.error(event.data);
                        worker.terminate();
                        reject(new Error(event.data));
                    }
                };
            });
            this.worker = worker;
            return promise;
        };
        DescriptorRunnerWebassembly.prototype.loadWeights = function (weightsData) {
            return __awaiter(this, void 0, void 0, function () {
                var _this = this;
                var decoder, weight_data, worker, promise;
                return __generator(this, function (_a) {
                    switch (_a.label) {
                        case 0:
                            if (!this.descriptor)
                                throw new Error('Descriptor is not loaded');
                            if (!this.worker)
                                throw new Error('Worker is not initialized');
                            decoder = WebDNN.get_weight_decoder(this.descriptor.weight_encoding);
                            return [4 /*yield*/, decoder.decode(weightsData, this.descriptor.memory_layout)];
                        case 1:
                            weight_data = _a.sent();
                            worker = this.worker;
                            promise = new Promise(function (resolve, reject) {
                                _this.worker_promise_reject_func = reject;
                                worker.onmessage = function (event) {
                                    if (event.data === 0) {
                                        resolve();
                                    }
                                    else {
                                        console.log(event.data);
                                        worker.terminate();
                                        reject(new Error(event.data));
                                    }
                                };
                                worker.postMessage({ type: 'weight', data: weight_data });
                            });
                            return [2 /*return*/, promise];
                    }
                });
            });
        };
        DescriptorRunnerWebassembly.prototype.getInputViews = function () {
            return __awaiter(this, void 0, void 0, function () {
                var views, i, var_alloc;
                return __generator(this, function (_a) {
                    if (this.inputViews)
                        return [2 /*return*/, this.inputViews];
                    if (!this.descriptor)
                        throw new Error('Descriptor is not loaded');
                    views = [];
                    for (i = 0; i < this.descriptor.inputs.length; i++) {
                        var_alloc = this.descriptor.memory_layout.allocations[this.descriptor.inputs[i]];
                        views.push(new Float32Array(var_alloc.size));
                    }
                    this.inputViews = views;
                    return [2 /*return*/, views];
                });
            });
        };
        DescriptorRunnerWebassembly.prototype.getOutputViews = function () {
            return __awaiter(this, void 0, void 0, function () {
                var views, i, var_alloc;
                return __generator(this, function (_a) {
                    if (this.outputViews)
                        return [2 /*return*/, this.outputViews];
                    if (!this.descriptor)
                        throw new Error('Descriptor is not loaded');
                    views = [];
                    for (i = 0; i < this.descriptor.outputs.length; i++) {
                        var_alloc = this.descriptor.memory_layout.allocations[this.descriptor.outputs[i]];
                        views.push(new Float32Array(var_alloc.size));
                    }
                    this.outputViews = views;
                    return [2 /*return*/, views];
                });
            });
        };
        DescriptorRunnerWebassembly.prototype.run = function () {
            return __awaiter(this, void 0, void 0, function () {
                var _this = this;
                var descriptor, worker, inputViews, outputViews, promise;
                return __generator(this, function (_a) {
                    if (!this.descriptor)
                        throw new Error('Descriptor is not loaded');
                    if (!this.inputViews || !this.outputViews)
                        throw new Error('getInputViews and getOutputViews must be called prior to run');
                    if (!this.worker)
                        throw new Error('Worker is not initialized');
                    descriptor = this.descriptor;
                    worker = this.worker;
                    inputViews = this.inputViews;
                    outputViews = this.outputViews;
                    promise = new Promise(function (resolve, reject) {
                        // TODO: better way not to generate function on every run
                        _this.worker_promise_reject_func = reject;
                        worker.onmessage = function (event) {
                            if (Array.isArray(event.data)) {
                                for (var i = 0; i < event.data.length; i++) {
                                    outputViews[i].set(event.data[i]);
                                }
                                resolve();
                            }
                            else {
                                console.log(event.data);
                                worker.terminate();
                                reject(new Error(event.data));
                            }
                        };
                        var inputs = [];
                        for (var i = 0; i < descriptor.inputs.length; i++) {
                            var var_alloc = descriptor.memory_layout.allocations[descriptor.inputs[i]];
                            inputs.push({ offset: var_alloc.offset, size: var_alloc.size, data: inputViews[i] });
                        }
                        var outputs = [];
                        for (var i = 0; i < descriptor.outputs.length; i++) {
                            var var_alloc = descriptor.memory_layout.allocations[descriptor.outputs[i]];
                            outputs.push({ offset: var_alloc.offset, size: var_alloc.size });
                        }
                        worker.postMessage({ type: 'run', inputs: inputs, outputs: outputs });
                    });
                    return [2 /*return*/, promise];
                });
            });
        };
        return DescriptorRunnerWebassembly;
    }(WebDNN.DescriptorRunner));
    WebDNN.DescriptorRunnerWebassembly = DescriptorRunnerWebassembly;
})(WebDNN || (WebDNN = {}));
/// <reference path="./gpu_interface.ts" />
/// <reference path="../descriptor_runner/descriptor_runner_webassembly.ts" />
var WebDNN;
(function (WebDNN) {
    var GPUInterfaceWebassembly = (function (_super) {
        __extends(GPUInterfaceWebassembly, _super);
        function GPUInterfaceWebassembly(option) {
            var _this = _super.call(this) || this;
            _this.backendName = 'webassembly';
            if (typeof Worker === 'undefined') {
                throw new Error('WebWorker is needed for WebAssembly backend');
            }
            if (typeof WebAssembly !== 'object') {
                console.warn('WebAssembly is not supported on this browser, trying to use asm.js code');
            }
            return _this;
        }
        GPUInterfaceWebassembly.prototype.init = function () {
            return __awaiter(this, void 0, void 0, function () {
                return __generator(this, function (_a) {
                    return [2 /*return*/];
                });
            });
        };
        GPUInterfaceWebassembly.prototype.createDescriptorRunner = function () {
            return new WebDNN.DescriptorRunnerWebassembly();
        };
        return GPUInterfaceWebassembly;
    }(WebDNN.GPUInterface));
    WebDNN.GPUInterfaceWebassembly = GPUInterfaceWebassembly;
})(WebDNN || (WebDNN = {}));
/// <reference path="./graph_descriptor.ts" />
///<reference path="../fetch.ts" />
///<reference path="../graph_descriptor/graph_descriptor_fallback.ts" />
var WebDNN;
(function (WebDNN) {
    var DescriptorRunnerFallback = (function (_super) {
        __extends(DescriptorRunnerFallback, _super);
        function DescriptorRunnerFallback() {
            var _this = _super !== null && _super.apply(this, arguments) || this;
            _this.backendName = 'fallback';
            return _this;
        }
        DescriptorRunnerFallback.prototype.load = function (directory, progressCallback) {
            return __awaiter(this, void 0, void 0, function () {
                var graph_url, graph_fetch, _a, weight_url, weights_data_ab, _b;
                return __generator(this, function (_c) {
                    switch (_c.label) {
                        case 0:
                            graph_url = directory + "/graph_" + this.backendName + ".json";
                            if (this.ignoreCache) {
                                graph_url += '?t=' + Date.now();
                            }
                            graph_url = WebDNN.transformUrl(graph_url);
                            return [4 /*yield*/, WebDNN.fetch(graph_url)];
                        case 1:
                            graph_fetch = _c.sent();
                            if (!graph_fetch.ok) {
                                throw new Error(graph_url + " cannot be loaded");
                            }
                            _a = this;
                            return [4 /*yield*/, graph_fetch.json()];
                        case 2:
                            _a.descriptor = _c.sent();
                            return [4 /*yield*/, this.compile()];
                        case 3:
                            _c.sent();
                            weight_url = directory + "/weight_" + this.backendName + ".bin";
                            if (this.ignoreCache) {
                                weight_url += '?t=' + Date.now();
                            }
                            weight_url = WebDNN.transformUrl(weight_url);
                            _b = WebDNN.readArrayBufferProgressively;
                            return [4 /*yield*/, WebDNN.fetch(weight_url)];
                        case 4: return [4 /*yield*/, _b.apply(void 0, [_c.sent(), progressCallback])];
                        case 5:
                            weights_data_ab = _c.sent();
                            return [4 /*yield*/, this.loadWeights(new Uint8Array(weights_data_ab))];
                        case 6:
                            _c.sent();
                            return [2 /*return*/];
                    }
                });
            });
        };
        DescriptorRunnerFallback.prototype.setDescriptor = function (descriptor) {
            this.descriptor = descriptor;
        };
        DescriptorRunnerFallback.prototype.compile = function () {
            return __awaiter(this, void 0, void 0, function () {
                var descriptor, weight_name_alloc, name_2, alloc, variable_name_alloc, name_3, alloc;
                return __generator(this, function (_a) {
                    if (!this.descriptor)
                        throw new Error('Descriptor is not loaded');
                    descriptor = this.descriptor;
                    this.compileKernel();
                    this.rawWeightArray = new Float32Array(descriptor.weight_allocation.total_size);
                    weight_name_alloc = descriptor.weight_allocation.allocations;
                    this.weightArrays = new Map();
                    for (name_2 in weight_name_alloc) {
                        alloc = weight_name_alloc[name_2];
                        this.weightArrays.set(name_2, new Float32Array(this.rawWeightArray.buffer, alloc.offset * Float32Array.BYTES_PER_ELEMENT, alloc.size));
                    }
                    this.variableArrays = new Map();
                    variable_name_alloc = descriptor.variable_allocation.allocations;
                    for (name_3 in variable_name_alloc) {
                        alloc = variable_name_alloc[name_3];
                        this.variableArrays.set(name_3, new Float32Array(alloc.size));
                    }
                    return [2 /*return*/];
                });
            });
        };
        DescriptorRunnerFallback.prototype.compileKernel = function () {
            if (!this.descriptor)
                throw new Error('Descriptor is not loaded');
            var dnn_fallback_kernel = null;
            eval(this.descriptor.kernel_source);
            this.kernelObj = dnn_fallback_kernel;
        };
        DescriptorRunnerFallback.prototype.loadWeights = function (weightsData) {
            return __awaiter(this, void 0, void 0, function () {
                var decoder, _a, _b;
                return __generator(this, function (_c) {
                    switch (_c.label) {
                        case 0:
                            if (!this.descriptor)
                                throw new Error('Descriptor is not loaded');
                            if (!this.rawWeightArray)
                                throw new Error('Weight array is not loaded');
                            decoder = WebDNN.get_weight_decoder(this.descriptor.weight_encoding);
                            _b = (_a = this.rawWeightArray).set;
                            return [4 /*yield*/, decoder.decode(weightsData, this.descriptor.weight_allocation)];
                        case 1:
                            _b.apply(_a, [_c.sent()]);
                            return [2 /*return*/];
                    }
                });
            });
        };
        DescriptorRunnerFallback.prototype.run = function () {
            return __awaiter(this, void 0, void 0, function () {
                var descriptor, variableArrays, weightArrays, run_entry_date, last_progress_date, i, current_date, elapsed_ms, exec_info, input_arrays, output_arrays, weight_arrays;
                return __generator(this, function (_a) {
                    switch (_a.label) {
                        case 0:
                            if (!this.descriptor)
                                throw new Error('Descriptor is not loaded');
                            if (!this.variableArrays || !this.weightArrays)
                                throw new Error('Variable map is not initialized');
                            if (!this.inputViews || !this.outputViews)
                                throw new Error('getInputViews and getOutputViews must be called prior to run');
                            descriptor = this.descriptor;
                            variableArrays = this.variableArrays;
                            weightArrays = this.weightArrays;
                            run_entry_date = Date.now();
                            last_progress_date = Date.now();
                            i = 0;
                            _a.label = 1;
                        case 1:
                            if (!(i < this.descriptor.exec_infos.length)) return [3 /*break*/, 5];
                            current_date = Date.now();
                            if (!(current_date - last_progress_date >= 1000)) return [3 /*break*/, 3];
                            elapsed_ms = current_date - run_entry_date;
                            console.log("Processed " + i + "/" + this.descriptor.exec_infos.length + " kernels in " + elapsed_ms + " ms");
                            last_progress_date = current_date;
                            return [4 /*yield*/, this.wait_to_display()];
                        case 2:
                            _a.sent();
                            _a.label = 3;
                        case 3:
                            exec_info = this.descriptor.exec_infos[i];
                            input_arrays = exec_info.inputs.map(function (name) { return variableArrays.get(name); });
                            output_arrays = exec_info.outputs.map(function (name) { return variableArrays.get(name); });
                            weight_arrays = exec_info.weights.map(function (name) { return weightArrays.get(name); });
                            this.kernelObj[exec_info.entry_func_name](input_arrays, output_arrays, weight_arrays, exec_info.call_option);
                            _a.label = 4;
                        case 4:
                            i++;
                            return [3 /*break*/, 1];
                        case 5:
                            console.log("Processed " + this.descriptor.exec_infos.length + "/" + this.descriptor.exec_infos.length + " kernels in " + (Date.now() - run_entry_date) + " ms");
                            return [2 /*return*/];
                    }
                });
            });
        };
        DescriptorRunnerFallback.prototype.wait_to_display = function () {
            return __awaiter(this, void 0, void 0, function () {
                return __generator(this, function (_a) {
                    // let console.log to be displayed, and prevent freeze
                    return [2 /*return*/, new Promise(function (resolve, reject) {
                            setTimeout(resolve, 10);
                        })];
                });
            });
        };
        DescriptorRunnerFallback.prototype.getInputViews = function () {
            return __awaiter(this, void 0, void 0, function () {
                var variableArrays, views;
                return __generator(this, function (_a) {
                    if (!this.descriptor)
                        throw new Error('Descriptor is not loaded');
                    if (!this.variableArrays)
                        throw new Error('Variable map is not initialized');
                    if (this.inputViews)
                        return [2 /*return*/, this.inputViews];
                    variableArrays = this.variableArrays;
                    views = this.descriptor.inputs.map(function (name) { return variableArrays.get(name); });
                    this.inputViews = views;
                    return [2 /*return*/, views];
                });
            });
        };
        DescriptorRunnerFallback.prototype.getOutputViews = function () {
            return __awaiter(this, void 0, void 0, function () {
                var variableArrays, views;
                return __generator(this, function (_a) {
                    if (!this.descriptor)
                        throw new Error('Descriptor is not loaded');
                    if (!this.variableArrays)
                        throw new Error('Variable map is not initialized');
                    if (this.outputViews)
                        return [2 /*return*/, this.outputViews];
                    variableArrays = this.variableArrays;
                    views = this.descriptor.outputs.map(function (name) { return variableArrays.get(name); });
                    this.outputViews = views;
                    return [2 /*return*/, views];
                });
            });
        };
        return DescriptorRunnerFallback;
    }(WebDNN.DescriptorRunner));
    WebDNN.DescriptorRunnerFallback = DescriptorRunnerFallback;
})(WebDNN || (WebDNN = {}));
/// <reference path="../descriptor_runner/descriptor_runner_fallback.ts" />
var WebDNN;
(function (WebDNN) {
    var GPUInterfaceFallback = (function (_super) {
        __extends(GPUInterfaceFallback, _super);
        function GPUInterfaceFallback() {
            var _this = _super !== null && _super.apply(this, arguments) || this;
            _this.backendName = 'fallback';
            return _this;
        }
        GPUInterfaceFallback.prototype.init = function (option) {
            return __awaiter(this, void 0, void 0, function () {
                return __generator(this, function (_a) {
                    return [2 /*return*/];
                });
            });
        };
        GPUInterfaceFallback.prototype.createDescriptorRunner = function () {
            return new WebDNN.DescriptorRunnerFallback();
        };
        return GPUInterfaceFallback;
    }(WebDNN.GPUInterface));
    WebDNN.GPUInterfaceFallback = GPUInterfaceFallback;
})(WebDNN || (WebDNN = {}));
///<reference path="./gpu_interface/gpu_interface.ts" />
///<reference path="./gpu_interface/gpu_interface_webgpu.ts" />
///<reference path="./gpu_interface/gpu_interface_webassembly.ts" />
///<reference path="./gpu_interface/gpu_interface_fallback.ts" />
var WebDNN;
(function (WebDNN) {
    WebDNN.backends = {
        'webgpu': WebDNN.GPUInterfaceWebGPU,
        'webassembly': WebDNN.GPUInterfaceWebassembly,
        'fallback': WebDNN.GPUInterfaceFallback,
    };
    WebDNN.backendName = 'none';
    function initBackend(backendName, option) {
        return __awaiter(this, void 0, void 0, function () {
            var gpu, ex_1;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        if (!(backendName in WebDNN.backends))
                            throw new Error("Unknown backend: \"" + backendName + "\"");
                        _a.label = 1;
                    case 1:
                        _a.trys.push([1, 3, , 4]);
                        gpu = new WebDNN.backends[backendName](option);
                        return [4 /*yield*/, gpu.init()];
                    case 2:
                        _a.sent();
                        return [3 /*break*/, 4];
                    case 3:
                        ex_1 = _a.sent();
                        console.warn("Failed to initialize " + backendName + " backend: " + ex_1);
                        return [2 /*return*/, false];
                    case 4:
                        WebDNN.gpu = gpu;
                        WebDNN.backendName = backendName;
                        return [2 /*return*/, true];
                }
            });
        });
    }
    function init(backendOrder, backendOptions) {
        if (backendOptions === void 0) { backendOptions = {}; }
        return __awaiter(this, void 0, void 0, function () {
            var backendName_1;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        if (!backendOrder) {
                            backendOrder = ['webgpu', 'webassembly'];
                        }
                        else if (typeof backendOrder === 'string') {
                            backendOrder = [backendOrder];
                        }
                        backendOrder = backendOrder.slice();
                        if (backendOrder.indexOf('fallback') === -1)
                            backendOrder.concat(['fallback']);
                        _a.label = 1;
                    case 1:
                        if (!(backendOrder.length > 0)) return [3 /*break*/, 3];
                        backendName_1 = backendOrder.shift();
                        return [4 /*yield*/, initBackend(backendName_1, backendOptions[backendName_1])];
                    case 2:
                        if (_a.sent())
                            return [2 /*return*/, WebDNN.backendName];
                        return [3 /*break*/, 1];
                    case 3: throw new Error('No backend is available');
                }
            });
        });
    }
    WebDNN.init = init;
    /**
     * Prepare backend interface and load model data at once. Internally calls init().
     * @param directory URL of directory that contains graph descriptor files (e.g. graph_fallback.json)
     * @param initOption Initialize option
     * @return Interface to input/output data and run the model.
     */
    function prepareAll(directory, initOption) {
        if (initOption === void 0) { initOption = {}; }
        return __awaiter(this, void 0, void 0, function () {
            var backendOrder, backendOptions, backendName_2, runner, ex_2, inputViews, outputViews;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        backendOrder = initOption.backendOrder;
                        if (!backendOrder) {
                            backendOrder = ['webgpu', 'webassembly'];
                        }
                        else if (typeof backendOrder === 'string') {
                            backendOrder = [backendOrder];
                        }
                        backendOrder = backendOrder.slice();
                        if (backendOrder.indexOf('fallback') === -1)
                            backendOrder.concat(['fallback']);
                        backendOptions = initOption.backendOptions || {};
                        _a.label = 1;
                    case 1:
                        if (!(backendOrder.length > 0)) return [3 /*break*/, 9];
                        backendName_2 = backendOrder.shift();
                        return [4 /*yield*/, initBackend(backendName_2, backendOptions[backendName_2])];
                    case 2:
                        if (!(_a.sent()))
                            return [3 /*break*/, 1];
                        runner = WebDNN.gpu.createDescriptorRunner();
                        _a.label = 3;
                    case 3:
                        _a.trys.push([3, 5, , 6]);
                        return [4 /*yield*/, runner.load(directory, initOption.progressCallback)];
                    case 4:
                        _a.sent();
                        return [3 /*break*/, 6];
                    case 5:
                        ex_2 = _a.sent();
                        console.warn("Model loading failed for " + backendName_2 + " backend. Trying next backend: " + ex_2.message);
                        return [3 /*break*/, 6];
                    case 6: return [4 /*yield*/, runner.getInputViews()];
                    case 7:
                        inputViews = _a.sent();
                        return [4 /*yield*/, runner.getOutputViews()];
                    case 8:
                        outputViews = _a.sent();
                        return [2 /*return*/, {
                                backendName: backendName_2,
                                inputViews: inputViews,
                                outputViews: outputViews,
                                run: runner.run.bind(runner)
                            }];
                    case 9: throw new Error('No backend is available');
                }
            });
        });
    }
    WebDNN.prepareAll = prepareAll;
})(WebDNN || (WebDNN = {}));
var WebDNN;
(function (WebDNN) {
    var Math;
    (function (Math) {
        /**
         * Return indices of the top-K largest samples.
         * @param arr array
         * @param k number of indices
         * @returns {number[]} indices of top-K largest samples
         */
        function argmax(arr, k) {
            if (k === void 0) { k = 1; }
            var stack = [[0, arr.length]];
            var workspace = {};
            while (stack.length > 0) {
                var fromTo = stack.shift(), from = fromTo[0], to = fromTo[1], pivot = arr[to - 1], left = from, right = to - 2, tmp = void 0;
                if (from >= to)
                    continue;
                while (true) {
                    while (arr[left] > pivot && left <= right)
                        left++;
                    while (arr[right] <= pivot && left <= right)
                        right--;
                    if (left >= right)
                        break;
                    tmp = arr[left] || left;
                    arr[left] = arr[right] || right;
                    arr[right] = tmp;
                    tmp = workspace[left] || left;
                    workspace[left] = workspace[right] || right;
                    workspace[right] = tmp;
                }
                if (left != to - 1) {
                    arr[to - 1] = arr[left];
                    arr[left] = pivot;
                    tmp = workspace[to - 1] || to - 1;
                    workspace[to - 1] = workspace[left] || left;
                    workspace[left] = tmp;
                }
                stack.unshift([from, left]);
                if (left + 1 < k)
                    stack.unshift([left + 1, to]);
            }
            var result = [];
            for (var i = 0; i < k; i++) {
                result.push(i in workspace ? workspace[i] : i);
            }
            return result;
        }
        Math.argmax = argmax;
        /**
         * Return indices of the top-K smallest samples.
         * @param arr array
         * @param k number of indices
         * @returns {number[]} indices of top-K smallest samples
         */
        function argmin(arr, k) {
            if (k === void 0) { k = 1; }
            var stack = [[0, arr.length]];
            var workspace = {};
            while (stack.length > 0) {
                var fromTo = stack.shift(), from = fromTo[0], to = fromTo[1], pivot = arr[to - 1], left = from, right = to - 2, tmp = void 0;
                if (from >= to)
                    continue;
                while (true) {
                    while (arr[left] < pivot && left <= right)
                        left++;
                    while (arr[right] >= pivot && left <= right)
                        right--;
                    if (left >= right)
                        break;
                    tmp = arr[left] || left;
                    arr[left] = arr[right] || right;
                    arr[right] = tmp;
                    tmp = workspace[left] || left;
                    workspace[left] = workspace[right] || right;
                    workspace[right] = tmp;
                }
                if (left != to - 1) {
                    arr[to - 1] = arr[left];
                    arr[left] = pivot;
                    tmp = workspace[to - 1] || to - 1;
                    workspace[to - 1] = workspace[left] || left;
                    workspace[left] = tmp;
                }
                stack.unshift([from, left]);
                if (left + 1 < k)
                    stack.unshift([left + 1, to]);
            }
            var result = [];
            for (var i = 0; i < k; i++) {
                result.push(i in workspace ? workspace[i] : i);
            }
            return result;
        }
        Math.argmin = argmin;
    })(Math = WebDNN.Math || (WebDNN.Math = {}));
})(WebDNN || (WebDNN = {}));
var WebDNN;
(function (WebDNN) {
    function getBackendAvailabilityWebGPU() {
        return 'WebGPUComputeCommandEncoder' in window;
    }
    function getBackendAvailabilityWebAssembly() {
        return 'Worker' in window;
    }
    function getBackendAvailabilityFallback() {
        return true;
    }
    /**
     * Check backend availability
     * @returns List of backend availability and default selected backend order
     */
    function getBackendAvailability() {
        var status = {
            'webgpu': getBackendAvailabilityWebGPU(),
            'webassembly': getBackendAvailabilityWebAssembly(),
            'fallback': getBackendAvailabilityFallback()
        };
        var order = ['webgpu', 'webassembly', 'fallback'].filter(function (backend) { return status[backend]; });
        return {
            status: status,
            defaultOrder: order
        };
    }
    WebDNN.getBackendAvailability = getBackendAvailability;
})(WebDNN || (WebDNN = {}));
//# sourceMappingURL=webdnn.es5.js.map