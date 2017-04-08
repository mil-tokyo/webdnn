/**
 * You must load 2 scripts before this file
 * 
 * - gpgpu.js
 * - functions/warmup.js
 * 
 */

Object.defineProperty(window, 'TestHarness', {
    enumerable: true,
    configurable: false,
    writable: false,
    value: new class TestHarness {
        constructor() {
            this.results = [];
        }

        async runPerformanceTestAsync(test) {

            if ('name' in test) console.log(`test: ${test.name}`);
            if ('pre' in test) test.pre();

            // warmup();

            await GPGPU.sync();
            let clockStart = performance.now();

            test.main();

            await GPGPU.sync();
            let clockEnd = performance.now();

            if ('post' in test) test.post();

            this.results.push(test.summarize(clockEnd - clockStart));
        }

        showSummaryAsTable() {
            console.table(this.results);
        }
    }
});