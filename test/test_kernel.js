///<reference path="../dist/webdnn.d.ts" />
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
var assert = new (function () {
    function class_1() {
        this.EPS = 1e-4;
    }
    class_1.prototype.equal = function (expected, real, description) {
        if (expected !== real)
            throw Error((description ? description + ': ' : '') + "(expected: " + expected + ") != (real: " + real + ")");
    };
    class_1.prototype.floatEqual = function (expected, real, description) {
        if (Math.abs(expected - real) / ((!isFinite(expected) || expected == 0) ? 1 : expected) >= this.EPS) {
            throw Error((description ? description + ': ' : '') + "(expected: " + expected + ") != (real: " + real + ")");
        }
    };
    class_1.prototype.floatArrayEqual = function (expected, real, description) {
        for (var i = 0; i < expected.length; i++) {
            try {
                this.floatEqual(expected[i], real[i]);
            }
            catch (e) {
                throw Error((description ? description + ': ' : '') + "(expected[" + i + "]: " + expected[i] + ") != (real[" + i + "]: " + real[i] + ")");
            }
        }
    };
    return class_1;
}());
//noinspection JSUnusedGlobalSymbols
var TestRunner = new (function () {
    function class_2() {
        this.testCases = [];
        this.results = [];
        this.currentTestCaseIndex = 0;
    }
    class_2.prototype.setup = function () {
        return __awaiter(this, void 0, void 0, function () {
            var masterJSONUrl, res, _a;
            return __generator(this, function (_b) {
                switch (_b.label) {
                    case 0:
                        masterJSONUrl = document.getElementById('masterJSONUrl').value;
                        return [4 /*yield*/, fetch(masterJSONUrl)];
                    case 1:
                        res = _b.sent();
                        _a = this;
                        return [4 /*yield*/, res.json()];
                    case 2:
                        _a.testCases = _b.sent();
                        this.rootUrl = masterJSONUrl.split('/').slice(0, masterJSONUrl.split('/').length - 1).join('/') + '/';
                        this.results = [];
                        this.currentTestCaseIndex = 0;
                        console.groupCollapsed('Setup');
                        console.log('- TestRunner loaded test case(s)');
                        console.log('- # of test case(s): ' + this.testCases.length);
                        console.groupEnd();
                        return [2 /*return*/];
                }
            });
        });
    };
    class_2.prototype.cleanUp = function () {
        var results = this.results;
        console.group('Result');
        var failedResults = results.filter(function (result) { return !result.result; });
        if (failedResults.length == 0) {
            console.info("- " + results.length + " PASSED / 0 FAILED");
        }
        else {
            console.error("- " + (results.length - failedResults.length) + " PASSED / " + failedResults.length + " FAILED");
        }
        failedResults.forEach(function (result) {
            console.group(result.name);
            console.log('- ' + result.err.message);
            console.groupEnd();
        });
        console.groupEnd();
    };
    class_2.prototype.mainLoop = function () {
        return __awaiter(this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, this.runTestCase()];
                    case 1:
                        _a.sent();
                        this.currentTestCaseIndex++;
                        if (this.currentTestCaseIndex < this.testCases.length)
                            return [2 /*return*/, this.mainLoop()];
                        return [2 /*return*/];
                }
            });
        });
    };
    class_2.prototype.runTestCase = function () {
        return __awaiter(this, void 0, void 0, function () {
            var testCase, testName, elapsedTime, runner, inputs_1, outputs_1, startTime, err_1;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        testCase = this.testCases[this.currentTestCaseIndex];
                        testName = "[" + testCase.backend + "] " + testCase.description;
                        console.group("[" + (this.currentTestCaseIndex + 1) + "/" + this.testCases.length + "]" + testName);
                        _a.label = 1;
                    case 1:
                        _a.trys.push([1, 4, , 5]);
                        return [4 /*yield*/, WebDNN.load(this.rootUrl + testCase.dirname, {
                                backendOrder: testCase.backend,
                                ignoreCache: true
                            })];
                    case 2:
                        runner = _a.sent();
                        assert.equal(testCase.backend, runner.backendName, 'backend');
                        inputs_1 = runner.getInputViews();
                        outputs_1 = runner.getOutputViews();
                        testCase.inputs.forEach(function (data, i) { return inputs_1[i].set(data); });
                        startTime = performance.now();
                        return [4 /*yield*/, runner.run()];
                    case 3:
                        _a.sent();
                        elapsedTime = performance.now() - startTime;
                        testCase.expected.forEach(function (expected, i) { return assert.floatArrayEqual(expected, outputs_1[i].toActual(), "outputs[" + i + "]"); });
                        this.results.push({
                            name: testName,
                            testCase: testCase,
                            result: true,
                            elapsedTime: elapsedTime
                        });
                        console.log('- PASS: Elapsed time=' + (elapsedTime).toFixed(2) + '[ms]');
                        return [3 /*break*/, 5];
                    case 4:
                        err_1 = _a.sent();
                        this.results.push({
                            name: testName,
                            testCase: testCase,
                            result: false,
                            elapsedTime: -1,
                            err: err_1
                        });
                        console.error(err_1);
                        return [3 /*break*/, 5];
                    case 5:
                        console.groupEnd();
                        return [2 /*return*/];
                }
            });
        });
    };
    class_2.prototype.run = function () {
        return __awaiter(this, void 0, void 0, function () {
            var _this = this;
            return __generator(this, function (_a) {
                return [2 /*return*/, this.setup()
                        .then(function () { return console.groupCollapsed('Run'); })
                        .then(function () { return _this.mainLoop(); })
                        .then(function () { return console.groupEnd(); })
                        .then(function () { return _this.cleanUp(); })["catch"](function (err) { return console.error(err); })];
            });
        });
    };
    return class_2;
}());
