///<reference path="../dist/webdnn.umd.d.ts" />

let logger: DebugLogger = console;
let pageLogger: DebugLogger;

interface DebugLogger {
    group: (groupTitle?: string) => void;
    groupEnd: () => void;
    log: (message?: any) => void;
    info: (message?: any) => void;
    warn: (message?: any) => void;
    error: (message?: any) => void;
}

class PageLogger implements DebugLogger {
    // FIXME: better representation
    placeholder: HTMLElement;

    constructor() {
        this.placeholder = document.getElementById("log");
    }

    private write(message: string) {
        let elem = document.createElement("span");
        elem.innerText = message;
        this.placeholder.appendChild(elem);
        this.placeholder.appendChild(document.createElement("br"));
    }

    group(groupTitle?: string) {
        this.write(`group: ${groupTitle}`);
        console.group(groupTitle);
    }

    groupEnd() {
        this.write("group end");
        console.groupEnd();
    }

    log(message?: any) {
        this.write(`log: ${message}`);
        console.log(message);
    }

    info(message?: any) {
        this.write(`info: ${message}`);
        console.info(message);
    }

    warn(message?: any) {
        this.write(`warn: ${message}`);
        console.warn(message);
    }

    error(message?: any) {
        this.write(`error: ${message}`);
        console.error(message);
    }
}

class Warning extends Error {
}

const assert = new class {
    EPS = 1e-4;
    ABS_EPS = 0.0;

    equal<T>(expected: T, real: T, description?: string) {
        if (expected !== real) throw Error(`${description ? description + ': ' : ''}(expected: ${expected}) != (real: ${real})`);
    }

    floatEqual(expected: number, real: number, description?: string) {
        if (!(Math.abs(expected - real) <= (this.ABS_EPS + this.EPS * Math.abs(expected)))) {
            throw Error(`${description ? description + ': ' : ''}(expected: ${expected}) != (real: ${real})`);
        }
    }

    floatArrayEqual(expected: ArrayLike<number>, real: ArrayLike<number>) {
        for (let i = 0; i < expected.length; i++) {
            try {
                this.floatEqual(expected[i], real[i]);
            } catch (e) {
                throw Error(e.message
                    .replace('expected', `expected[${i}]`)
                    .replace('real', `real[${i}]`));
            }
        }
    }
};

interface DataRef {
    byte_offset: number,
    length: number
}

interface TestCase {
    description: string,
    backend: WebDNN.BackendName,
    dirname: string,
    inputs: (Float32Array | number[])[],
    expected: (Float32Array | number[])[],
    inputs_ref: DataRef[],
    expected_ref: DataRef[],
    EPS: number,
    ABS_EPS: number
}

interface Result {
    name: string,
    testCase: TestCase,
    err?: Error,
    result: boolean,
    elapsedTime: number,
    outputs: number[][]
}

//noinspection JSUnusedLocalSymbols
const TestRunner = new class {
    testCases: TestCase[] = [];
    rootUrl: string;
    results: Result[] = [];
    currentTestCaseIndex = 0;

    async setup() {
        if (!pageLogger) {
            pageLogger = new PageLogger();
        }
        logger = (document.getElementById('displayOnPage')! as HTMLInputElement).checked ? pageLogger : console;

        // avoid loading from cache
        let masterJSONUrl = `${(document.getElementById('masterJSONUrl')! as HTMLInputElement).value}?t=${Date.now()}`;

        let res = await fetch(masterJSONUrl);
        this.testCases = await res.json();
        await this.loadDataRef();
        this.rootUrl = masterJSONUrl.split('/').slice(0, masterJSONUrl.split('/').length - 1).join('/') + '/';
        this.results = [];
        this.currentTestCaseIndex = 0;

        logger.group('Setup');
        logger.log('- TestRunner loaded test case(s)');
        logger.log('- # of test case(s): ' + this.testCases.length);
        logger.groupEnd();
    }

    async loadDataRef() {
        if (!this.testCases[0].inputs_ref) {
            return;
        }

        let dataUrl = `${(document.getElementById('masterJSONUrl')! as HTMLInputElement).value}.bin?t=${Date.now()}`;
        let res = await fetch(dataUrl);
        let dataArrayBuffer = await res.arrayBuffer();
        for (let i = 0; i < this.testCases.length; i++) {
            let testCase = this.testCases[i];
            testCase.inputs = testCase.inputs_ref.map((v) => this.createArrayFromDataRef(dataArrayBuffer, v));
            testCase.expected = testCase.expected_ref.map((v) => this.createArrayFromDataRef(dataArrayBuffer, v));
        }
    }

    createArrayFromDataRef(baseArray: ArrayBuffer, dataRef: DataRef): Float32Array {
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
        } else {
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
        (window as any).results = results;
    }

    async mainLoop() {
        await this.runTestCase();

        this.currentTestCaseIndex++;
        if (this.currentTestCaseIndex < this.testCases.length) return this.mainLoop();
    }

    async runTestCase() {
        const testCase = this.testCases[this.currentTestCaseIndex];
        const testName = `[${testCase.backend}] ${testCase.description}`;
        let elapsedTime: number;
        let outputs: any;

        logger.group(`[${this.currentTestCaseIndex + 1}/${this.testCases.length}]${testName}`);

        if (WebDNN.getBackendAvailability().status[testCase.backend]) {
            try {
                assert.EPS = testCase.EPS;
                assert.ABS_EPS = testCase.ABS_EPS;

                let runner = await WebDNN.load(this.rootUrl + testCase.dirname, {
                    backendOrder: testCase.backend,
                    ignoreCache: true
                });
                assert.equal(testCase.backend, runner.backendName, 'backend');

                let inputs = runner.getInputViews();
                outputs = runner.getOutputViews();

                testCase.inputs.forEach((data, i) => inputs[i].set(data));
                let startTime = performance.now();
                await runner.run();
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

            } catch (err) {
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
                } else {
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
        } else {
            logger.log(`backend "${testCase.backend}" is not supported in this browser, and test case is skipped.`);
        }

        logger.groupEnd();
    }

    async run() {
        return this.setup()
            .then(() => logger.group('Run'))
            .then(() => this.mainLoop())
            .then(() => logger.groupEnd())
            .then(() => this.cleanUp())
            .catch(err => logger.error(err))
    }
};
