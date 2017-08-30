///<reference path="../dist/webdnn.umd.d.ts" />

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

interface TestCase {
    description: string,
    backend: WebDNN.BackendName,
    dirname: string,
    inputs: number[][],
    expected: number[][],
    EPS: number,
    ABS_EPS: number
}

interface Result {
    name: string,
    testCase: TestCase,
    err?: Error,
    result: boolean,
    elapsedTime: number
}

//noinspection JSUnusedLocalSymbols
const TestRunner = new class {
    testCases: TestCase[] = [];
    rootUrl: string;
    results: Result[] = [];
    currentTestCaseIndex = 0;

    async setup() {
        let masterJSONUrl = (document.getElementById('masterJSONUrl')! as HTMLInputElement).value;

        let res = await fetch(masterJSONUrl);
        this.testCases = await res.json();
        this.rootUrl = masterJSONUrl.split('/').slice(0, masterJSONUrl.split('/').length - 1).join('/') + '/';
        this.results = [];
        this.currentTestCaseIndex = 0;

        console.group('Setup');
        console.log('- TestRunner loaded test case(s)');
        console.log('- # of test case(s): ' + this.testCases.length);
        console.groupEnd();
    }

    cleanUp() {
        let results = this.results;
        console.group('Result');

        let failedResults = results.filter(result => !result.result);
        let warningResults = results.filter(result => result.result && result.err);

        if (failedResults.length == 0) {
            console.info(`- ${results.length} PASSED / 0 FAILED`);
        } else {
            console.error(`- ${results.length - failedResults.length} PASSED / ${failedResults.length} FAILED`);

            console.group('Failed');
            failedResults.forEach(result => {
                console.group(result.name);
                console.log(`In: ${result.testCase.dirname}`);
                console.log('- ' + result.err.message);
                console.groupEnd();
            });
            console.groupEnd();
        }

        if (warningResults.length > 0) {
            console.group('Warning');
            warningResults.forEach(result => {
                console.group(result.name);
                console.log(`In: ${result.testCase.dirname}`);
                console.log('- ' + result.err.message);
                console.groupEnd();
            });
            console.groupEnd();
        }

        console.groupEnd();
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

        console.group(`[${this.currentTestCaseIndex + 1}/${this.testCases.length}]${testName}`);

        try {
            assert.EPS = testCase.EPS;
            assert.ABS_EPS = testCase.ABS_EPS;

            let runner = await WebDNN.load(this.rootUrl + testCase.dirname, {
                backendOrder: testCase.backend,
                ignoreCache: true
            });
            assert.equal(testCase.backend, runner.backendName, 'backend');

            let inputs = runner.getInputViews();
            let outputs = runner.getOutputViews();

            testCase.inputs.forEach((data, i) => inputs[i].set(data));
            let startTime = performance.now();
            await runner.run();
            await runner.run();
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

            console.log('- PASS: Elapsed time=' + (elapsedTime).toFixed(2) + '[ms]');
            console.log(result);

        } catch (err) {
            if (err instanceof Warning) {
                this.results.push({
                    name: testName,
                    testCase: testCase,
                    result: true,
                    elapsedTime: elapsedTime,
                    err: err
                });
                console.warn(err.message);
            } else {
                this.results.push({
                    name: testName,
                    testCase: testCase,
                    result: false,
                    elapsedTime: -1,
                    err: err
                });
                console.error(err);
            }
        }

        console.groupEnd();
    }

    async run() {
        return this.setup()
            .then(() => console.group('Run'))
            .then(() => this.mainLoop())
            .then(() => console.groupEnd())
            .then(() => this.cleanUp())
            .catch(err => console.error(err))
    }
};
