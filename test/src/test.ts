/// <reference path="../../array-prototype/webgpu_handler.ts" />


namespace WebDNN {

    export namespace Test {
        type EventHandler = (...args: any[]) => any;

        class EvntDispatcher<EventType> {
            private map = new Map<EventType, EventHandler[]>();

            on(type: EventType, handler: EventHandler) {
                if (!this.map.has(type)) this.map.set(type, []);

                this.map.get(type).push(handler);
            }

            off(type: EventType, handler: EventHandler) {
                if (!this.map.has(type)) return;

                let handlers = this.map.get(type);
                for (let i = handlers.length - 1; i >= 0; i--) {
                    if (handlers[i] === handler) handlers.splice(i, 1);
                }
            }

            fire(type: EventType, ...args: any[]) {
                if (!this.map.has(type)) return;

                this.map.get(type).forEach(handler => handler.apply(this, args));
            }
        }

        type RunnerEventType =
            'startPerformanceTest' |
            'startMain' |
            'endMain' |
            'endPerformanceTest' |
            'updatePerformanceSummary';

        export class Runner extends EvntDispatcher<RunnerEventType> {
            webgpu: WebGPUHandler;

            constructor(webgpu: WebGPUHandler) {
                super();
                this.webgpu = webgpu;
            }

            async runPerformanceTest(test: PerformanceTest) {
                let elapsedTimes = [];
                let iterationCount = test.iterationCount || 50;

                if (test.setup) test.setup();
                if (test.setupAsync) await test.setupAsync()

                this.fire('startPerformanceTest', test);

                for (let i = 0; i < iterationCount; i++) {

                    this.fire('startMain', test);

                    await WebDNN.PrototypeKernel.sync();
                    let startTime = performance.now();

                    test.main();

                    await WebDNN.PrototypeKernel.sync();
                    let endTime = performance.now();

                    this.fire('endMain', test);

                    elapsedTimes.push(endTime - startTime);
                }

                this.fire('endPerformanceTest', test);

                if (test.cleanup) test.cleanup();
                if (test.cleanupAsync) await test.cleanupAsync()

                let stats = computeStats(elapsedTimes);
                let summary = (test.summarize || this.summarizePerformanceTestResult)(stats, test);

                this.fire('updatePerformanceSummary', summary);
            }

            private summarizePerformanceTestResult(elapsedTime: StatsValue, test: PerformanceTest) {
                let normalizedStd = elapsedTime.std / elapsedTime.mean;

                return {
                    'name': test.name,
                    'elapsed time [ms]': elapsedTime.mean.toFixed(2),
                    'std [ms]': (normalizedStd * 100).toFixed(2)
                } as PerformanceTestSummary
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

        export interface PerformanceTest {
            name: string
            setup?: () => void
            setupAsync?: () => Promise<any>
            main: () => any
            cleanup?: () => void
            cleanupAsync?: () => Promise<any>
            summarize?: (elapsedTime: StatsValue, test: PerformanceTest) => PerformanceTestSummary
            iterationCount?: number
        }

        export interface PerformanceTestSummary {
            [key: string]: any
        }

        export class DOMTextLogger {
            runner: Runner;
            outputContainer: HTMLElement;
            output: HTMLElement;
            summaries: PerformanceTestSummary[];

            constructor(runner: Runner, outputContainer: HTMLElement) {
                this.runner = runner;
                this.outputContainer = outputContainer;
                this.output = document.createElement("pre");

                this.summaries = [];
                runner.on('updatePerformanceSummary', (summary) => this.summaries.push(summary));

                this.outputContainer.appendChild(this.output);
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

                this.output = document.createElement("pre");
                this.outputContainer.appendChild(this.output);
            }

            clearSummary() {
                this.summaries = [];
            }

            clearText() {
                this.outputContainer.innerHTML = '';

                this.output = document.createElement("pre");
                this.outputContainer.appendChild(this.output);
            }

            clearAll() {
                this.clearSummary();
                this.clearText();
            }

            success(text) {
                let caption = document.createElement('span');
                caption.classList.add('success');
                caption.textContent = text;

                this.outputContainer.appendChild(caption);

                this.output = document.createElement("pre");
                this.outputContainer.appendChild(this.output);
            }

            bold(text) {
                let caption = document.createElement('span');
                caption.classList.add('bold');
                caption.textContent = text;

                this.outputContainer.appendChild(caption);

                this.output = document.createElement("pre");
                this.outputContainer.appendChild(this.output);
            }

            error(text) {
                let caption = document.createElement('span');
                caption.classList.add('error');
                caption.textContent = text;

                this.outputContainer.appendChild(caption);

                this.output = document.createElement("pre");
                this.outputContainer.appendChild(this.output);
            }
        }
    }
}
