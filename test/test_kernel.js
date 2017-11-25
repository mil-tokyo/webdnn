var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : new P(function (resolve) { resolve(result.value); }).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
///<reference path="../dist/webdnn.umd.d.ts" />
let logger = console;
let pageLogger;
class PageLogger {
    constructor() {
        this.placeholder = document.getElementById("log");
    }
    write(message) {
        let elem = document.createElement("span");
        elem.innerText = message;
        this.placeholder.appendChild(elem);
        this.placeholder.appendChild(document.createElement("br"));
    }
    group(groupTitle) {
        this.write(`group: ${groupTitle}`);
        console.group(groupTitle);
    }
    groupEnd() {
        this.write("group end");
        console.groupEnd();
    }
    log(message) {
        this.write(`log: ${message}`);
        console.log(message);
    }
    info(message) {
        this.write(`info: ${message}`);
        console.info(message);
    }
    warn(message) {
        this.write(`warn: ${message}`);
        console.warn(message);
    }
    error(message) {
        this.write(`error: ${message}`);
        console.error(message);
    }
}
class Warning extends Error {
}
const assert = new class {
    constructor() {
        this.EPS = 1e-4;
        this.ABS_EPS = 0.0;
    }
    equal(expected, real, description) {
        if (expected !== real)
            throw Error(`${description ? description + ': ' : ''}(expected: ${expected}) != (real: ${real})`);
    }
    floatEqual(expected, real, description) {
        if (!(Math.abs(expected - real) <= (this.ABS_EPS + this.EPS * Math.abs(expected)))) {
            throw Error(`${description ? description + ': ' : ''}(expected: ${expected}) != (real: ${real})`);
        }
    }
    floatArrayEqual(expected, real) {
        for (let i = 0; i < expected.length; i++) {
            try {
                this.floatEqual(expected[i], real[i]);
            }
            catch (e) {
                throw Error(e.message
                    .replace('expected', `expected[${i}]`)
                    .replace('real', `real[${i}]`));
            }
        }
    }
};
//noinspection JSUnusedLocalSymbols
const TestRunner = new class {
    constructor() {
        this.testCases = [];
        this.results = [];
        this.currentTestCaseIndex = 0;
    }
    setup() {
        return __awaiter(this, void 0, void 0, function* () {
            if (!pageLogger) {
                pageLogger = new PageLogger();
            }
            logger = document.getElementById('displayOnPage').checked ? pageLogger : console;
            // avoid loading from cache
            let masterJSONUrl = `${document.getElementById('masterJSONUrl').value}?t=${Date.now()}`;
            let res = yield fetch(masterJSONUrl);
            this.testCases = yield res.json();
            yield this.loadDataRef();
            this.rootUrl = masterJSONUrl.split('/').slice(0, masterJSONUrl.split('/').length - 1).join('/') + '/';
            this.results = [];
            this.currentTestCaseIndex = 0;
            logger.group('Setup');
            logger.log('- TestRunner loaded test case(s)');
            logger.log('- # of test case(s): ' + this.testCases.length);
            logger.groupEnd();
        });
    }
    loadDataRef() {
        return __awaiter(this, void 0, void 0, function* () {
            if (!this.testCases[0].inputs_ref) {
                return;
            }
            let dataUrl = `${document.getElementById('masterJSONUrl').value}.bin?t=${Date.now()}`;
            let res = yield fetch(dataUrl);
            let dataArrayBuffer = yield res.arrayBuffer();
            for (let i = 0; i < this.testCases.length; i++) {
                let testCase = this.testCases[i];
                testCase.inputs = testCase.inputs_ref.map((v) => this.createArrayFromDataRef(dataArrayBuffer, v));
                testCase.expected = testCase.expected_ref.map((v) => this.createArrayFromDataRef(dataArrayBuffer, v));
            }
        });
    }
    createArrayFromDataRef(baseArray, dataRef) {
        return new Float32Array(baseArray, dataRef.byte_offset, dataRef.length);
    }
    cleanUp() {
        let results = this.results;
        logger.group('Result');
        let succeededResults = results.filter(result => result.result);
        let failedResults = results.filter(result => !result.result);
        let numSkippedTests = this.testCases.length - failedResults.length - succeededResults.length;
        if (failedResults.length == 0) {
            logger.info(`- ${succeededResults.length} PASSED / ${failedResults.length} FAILED / ${numSkippedTests} SKIP`);
        }
        else {
            logger.error(`- ${succeededResults.length} PASSED / ${failedResults.length} FAILED / ${numSkippedTests} SKIP`);
            logger.group('Failed');
            failedResults.forEach(result => {
                logger.group(result.name);
                logger.log(`In: ${result.testCase.dirname}`);
                logger.log('- ' + result.err.message);
                logger.groupEnd();
            });
            logger.groupEnd();
        }
        let warningResults = results.filter(result => result.result && result.err);
        if (warningResults.length > 0) {
            logger.group('Warning');
            warningResults.forEach(result => {
                logger.group(result.name);
                logger.log(`In: ${result.testCase.dirname}`);
                logger.log('- ' + result.err.message);
                logger.groupEnd();
            });
            logger.groupEnd();
        }
        logger.groupEnd();
        window.results = results;
    }
    mainLoop() {
        return __awaiter(this, void 0, void 0, function* () {
            yield this.runTestCase();
            this.currentTestCaseIndex++;
            if (this.currentTestCaseIndex < this.testCases.length)
                return this.mainLoop();
        });
    }
    runTestCase() {
        return __awaiter(this, void 0, void 0, function* () {
            const testCase = this.testCases[this.currentTestCaseIndex];
            const testName = `[${testCase.backend}] ${testCase.description}`;
            let elapsedTime;
            let outputs;
            logger.group(`[${this.currentTestCaseIndex + 1}/${this.testCases.length}]${testName}`);
            if (WebDNN.getBackendAvailability().status[testCase.backend]) {
                try {
                    assert.EPS = testCase.EPS;
                    assert.ABS_EPS = testCase.ABS_EPS;
                    let runner = yield WebDNN.load(this.rootUrl + testCase.dirname, {
                        backendOrder: testCase.backend,
                        ignoreCache: true
                    });
                    assert.equal(testCase.backend, runner.backendName, 'backend');
                    let inputs = runner.getInputViews();
                    outputs = runner.getOutputViews();
                    testCase.inputs.forEach((data, i) => inputs[i].set(data));
                    let startTime = performance.now();
                    yield runner.run();
                    elapsedTime = performance.now() - startTime;
                    testCase.expected.forEach((expected, i) => assert.floatArrayEqual(expected, outputs[i].toActual()));
                    let result = {
                        name: testName,
                        testCase: testCase,
                        result: true,
                        elapsedTime: elapsedTime,
                        outputs: outputs.map(v => v.toActual())
                    };
                    this.results.push(result);
                    logger.log('- PASS: Elapsed time=' + (elapsedTime).toFixed(2) + '[ms]');
                    logger.log(result);
                }
                catch (err) {
                    if (err instanceof Warning) {
                        this.results.push({
                            name: testName,
                            testCase: testCase,
                            result: true,
                            elapsedTime: elapsedTime,
                            err: err,
                            outputs: outputs ? outputs.map(v => v.toActual()) : null
                        });
                        logger.warn(err.message);
                    }
                    else {
                        this.results.push({
                            name: testName,
                            testCase: testCase,
                            result: false,
                            elapsedTime: -1,
                            err: err,
                            outputs: outputs ? outputs.map(v => v.toActual()) : null
                        });
                        logger.error(err);
                    }
                }
            }
            else {
                logger.log(`backend "${testCase.backend}" is not supported in this browser, and test case is skipped.`);
            }
            logger.groupEnd();
        });
    }
    run() {
        return __awaiter(this, void 0, void 0, function* () {
            return this.setup()
                .then(() => logger.group('Run'))
                .then(() => this.mainLoop())
                .then(() => logger.groupEnd())
                .then(() => this.cleanUp())
                .catch(err => logger.error(err));
        });
    }
};
