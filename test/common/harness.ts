/// <reference path="../../build/array_prototype/webdnn.d.ts" />


namespace WebDNN {
    export namespace Test {
        export class Harness {
            webgpu: WebGPUHandler;
            summaries: TestSummary[];
            outputContainer: HTMLElement;
            output: HTMLElement;

            constructor(webgpu: WebGPUHandler, outputContainer: HTMLElement) {
                this.outputContainer = outputContainer;
                this.output = document.createElement('pre');

                this.outputContainer.appendChild(this.output);
                this.webgpu = webgpu;
                this.webgpu.loadKernel(`kernel void sync(){}`, 'basic');
                this.summaries = [];
            }

            async fetchKernel(src: string) {
                this.webgpu.loadKernel(await (await fetch(src)).text(), 'test');
            }

            async runPerformanceTest(test: Test) {
                let elapsedTimes = [];
                let iterationCount = test.iterationCount || 50;

                if (test.setup) test.setup();
                if (test.setupAsync) await test.setupAsync();

                if ('main' in test) {
                    for (let i = 0; i < iterationCount; i++) {
                        await this.webgpu.sync();
                        let startTime = performance.now();

                        test.main();

                        await this.webgpu.sync();
                        let endTime = performance.now();

                        elapsedTimes.push(endTime - startTime);
                    }

                } else {
                    for (let i = 0; i < iterationCount; i++) {
                        await this.webgpu.sync();
                        let startTime = performance.now();

                        await test.mainAsync();

                        await this.webgpu.sync();
                        let endTime = performance.now();

                        elapsedTimes.push(endTime - startTime);
                    }
                }

                let stats = computeStats(elapsedTimes);
                this.summaries.push((test.summarize || this.summarizePerformanceTestResult)(stats, test));

                if (test.cleanup) test.cleanup();
                if (test.cleanupAsync) await test.cleanupAsync();
            }

            private summarizePerformanceTestResult(elapsedTime: StatsValue, test: Test) {
                let normalizedStd = elapsedTime.std / elapsedTime.mean;

                return {
                    'Name': test.name,
                    'Elapsed time [ms]': elapsedTime.mean.toFixed(2),
                    'Normalized std [%]': (normalizedStd).toFixed(2)
                } as TestSummary
            }

            log(text) {
                this.output.textContent += text + '\n';
            }

            show() {
                let summaries = this.summaries;
                let headers = Object.keys(summaries[0]);

                let table = document.createElement('table');
                let html = '';

                html += `<thead><tr><th>${headers.join('</th><th>')}</th></tr></thead>`;
                html += '<tbody>';

                summaries.forEach(summary => {
                    html += `<tr><td>${headers.map(head => summary[head]).join('</td><td>')}</td></tr>`;
                });

                html += '</tbody>';
                table.innerHTML = html;
                this.outputContainer.appendChild(table);

                this.output = document.createElement('pre');
                this.outputContainer.appendChild(this.output);
            }

            clearSummary() {
                this.summaries = [];
            }

            clearText() {
                this.output.innerHTML = '';
            }

            clearAll() {
                this.clearSummary();

                this.outputContainer.innerHTML = '';
                this.output = document.createElement('pre');
                this.outputContainer.appendChild(this.output);
            }

            success(text) {
                let caption = document.createElement('span');
                caption.classList.add('success');
                caption.textContent = text;

                this.outputContainer.appendChild(caption);

                this.output = document.createElement('pre');
                this.outputContainer.appendChild(this.output);
            }

            bold(text) {
                let caption = document.createElement('span');
                caption.classList.add('bold');
                caption.textContent = text;

                this.outputContainer.appendChild(caption);

                this.output = document.createElement('pre');
                this.outputContainer.appendChild(this.output);
            }

            error(text) {
                let caption = document.createElement('span');
                caption.classList.add('error');
                caption.textContent = text;

                this.outputContainer.appendChild(caption);

                this.output = document.createElement('pre');
                this.outputContainer.appendChild(this.output);
            }
        }

        export interface StatsValue {
            mean: number
            std: number
            max: number
            argmax: number
            min: number
            argmin: number
            datum: number[]
        }

        function computeStats(datum: number[]): StatsValue {
            let argmax = datum.reduce((si, v, i) => si[0] < v ? [v, i] : si, [-Infinity, -1])[1];
            let argmin = datum.reduce((si, v, i) => si[0] > v ? [v, i] : si, [+Infinity, -1])[1];

            let sum = datum.reduce((s, v) => s + v, 0);
            let sum2 = datum.reduce((s, v) => s + v ** 2, 0);

            let mean = sum / datum.length;
            let std = Math.sqrt(sum2 / datum.length - mean ** 2);

            return {
                mean: mean,
                std: std,
                max: datum[argmax],
                argmax: argmax,
                min: datum[argmin],
                argmin: argmin,
                datum: datum
            }
        }

        export interface Test {
            name?: string
            setup?: () => void
            setupAsync?: () => Promise<any>
            main?: () => any
            mainAsync?: () => Promise<any>
            cleanup?: () => void
            cleanupAsync?: () => Promise<any>
            summarize?: (elapsedTime: StatsValue, test: Test) => TestSummary
            iterationCount?: number
        }

        export interface TestSummary {
            [key: string]: any
        }
    }
}
