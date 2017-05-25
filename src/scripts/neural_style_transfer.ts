/// <reference path="../libs/webdnn.d.ts" />
/// <reference path="../libs/webcamjs.d.ts" />
import "../style/neural_style_transfer.scss";
import InitializingView from "./modules/initializing_view";

const NUM_RANDOM_IMAGE = 6;

enum State {
    INITIALIZING,
    STAND_BY,
    RUNNING,
    ERROR,
}

type DataSource = 'sample' | 'camera';

const App = new class {
    runner: WebDNN.DescriptorRunner;
    inputView: Float32Array;
    outputView: Float32Array;
    inputCanvas: HTMLCanvasElement;
    inputCtx: CanvasRenderingContext2D;
    outputCtx: CanvasRenderingContext2D;
    runButton: HTMLButtonElement;
    state: State = State.INITIALIZING;
    w: number;
    h: number;
    dataSource: DataSource;
    dataSourceSelect: HTMLSelectElement;
    cameraContainer: HTMLDivElement;
    sampleContainer: HTMLDivElement;

    async initialize() {
        let runButton = document.getElementById('runButton') as HTMLButtonElement;
        if (!runButton) throw Error('#runButton is not found.');
        this.runButton = runButton;
        this.runButton.addEventListener('click', () => App.onPlayButtonClick());

        let launchView = document.getElementById('launchView');
        if (launchView && launchView.parentNode) {
            launchView.parentNode.removeChild(launchView);
            launchView = null;
        }

        let dataSourceSelect = document.getElementById('dataSource') as HTMLSelectElement;
        if (!dataSourceSelect) throw Error('#dataSource is not found');
        this.dataSourceSelect = dataSourceSelect;
        dataSourceSelect.addEventListener('change', () => this.onDataSourceSelectChange());

        let cameraContainer = document.getElementById('cameraContainer') as HTMLDivElement;
        if (!cameraContainer) throw Error('#cameraContainer is not found');
        this.cameraContainer = cameraContainer;

        let sampleContainer = document.getElementById('sampleContainer') as HTMLDivElement;
        if (!sampleContainer) throw Error('#sampleContainer is not found');
        this.sampleContainer = sampleContainer;

        let initializingViewBase = document.getElementById('initializingView');
        if (!initializingViewBase) throw Error('#initializingView is not found');
        let initializingView = new InitializingView(initializingViewBase);

        initializingView.updateMessage('Load model data');

        await WebDNN.init();
        this.runner = WebDNN.gpu.createDescriptorRunner();
        await this.runner.load('./models/neural_style_transfer', (loaded, total) => initializingView.updateProgress(loaded / total));
        this.inputView = (await this.runner.getInputViews())[0];
        this.outputView = (await this.runner.getOutputViews())[0];

        let inputCanvas = document.getElementById('inputCanvas') as HTMLCanvasElement;
        if (!inputCanvas) throw Error('#inputCanvas is not found');
        this.inputCanvas = inputCanvas;
        this.w = inputCanvas.width;
        this.h = inputCanvas.height;

        let inputCtx = inputCanvas.getContext('2d');
        if (!inputCtx) throw Error('Canvas initialization failed');
        this.inputCtx = inputCtx;

        let outputCanvas = document.getElementById('outputCanvas') as HTMLCanvasElement;
        if (!outputCanvas) throw Error('#outputCanvas is not found');

        let outputCtx = outputCanvas.getContext('2d');
        if (!outputCtx) throw Error('Canvas initialization failed');
        this.outputCtx = outputCtx;

        Webcam.on('error', (err) => {
            console.error(err);
            this.setMessage(err);
            this.setState(State.ERROR);
        });

        await this.updateDataSource();
        initializingView.remove();
    }

    onDataSourceSelectChange() {
        this.updateDataSource();
    }

    onPlayButtonClick() {
        switch (this.state) {
            case State.STAND_BY:
                this.setState(State.RUNNING);
                break;

            case State.RUNNING:
                this.setState(State.STAND_BY);
                break;

            default:
                break;
        }
    }

    async updateDataSource() {
        this.dataSource = this.dataSourceSelect.value as DataSource;
        this.sampleContainer.style.display = this.dataSource == 'sample' ? 'block' : 'none';
        this.cameraContainer.style.display = this.dataSource == 'camera' ? 'block' : 'none';

        switch (this.dataSource) {
            case 'camera':
                this.setState(State.INITIALIZING);
                await this.initializeCamera();
                this.setState(State.STAND_BY);
                break;

            case 'sample':
                this.setState(State.INITIALIZING);
                this.finalizeCamera();
                await this.loadSampleImageToPreview();
                this.setState(State.STAND_BY);
                break;
        }
    }

    initializeCamera() {
        return new Promise(resolve => {
            let onceCallback = () => {
                Webcam.off('live', onceCallback);
                resolve();
            };

            Webcam.set({
                width: 192,
                height: 144,
                fps: 60,
                flip_horiz: true,
                image_format: 'png',
                force_flash: false
            });
            Webcam.on('live', onceCallback);
            Webcam.attach('#cameraContainer');
        });
    }

    finalizeCamera() {
        Webcam.reset();
    }

    async loadSampleImageToPreview() {
        let randomImageIndex = Math.floor(Math.random() * NUM_RANDOM_IMAGE);

        let url = `./assets/images/${randomImageIndex}.png`;
        let image = new Image();

        await new Promise(resolve => {
            image.onload = () => resolve(image);
            image.src = url;
        });

        this.inputCtx.drawImage(image, 0, 0, image.width, image.height, 0, 0, this.inputCtx.canvas.width, this.inputCtx.canvas.height);
    }

    async setState(state: State) {
        this.state = state;
        switch (state) {
            case State.INITIALIZING:
                this.setMessage('Initializing...');
                this.runButton.textContent = 'Initializing...';
                this.runButton.disabled = true;
                break;

            case State.STAND_BY:
                this.setMessage(`Ready(backend: ${this.runner.backend})`);
                this.runButton.textContent = 'Run';
                this.runButton.disabled = false;
                break;

            case State.RUNNING:
                this.setMessage('Processing...');
                this.runButton.disabled = true;

                await this.transfer();
                if (this.dataSource == 'camera') {
                    this.setMessage('Running');
                    this.runButton.textContent = 'Stop';
                    this.runButton.disabled = false;
                } else {
                    setTimeout(() => this.setState(State.STAND_BY));
                }
                break;

            case State.ERROR:
                this.runButton.textContent = 'Error';
                this.runButton.disabled = true;
                break;
        }
    }

    async transfer() {
        if (this.state !== State.RUNNING) return;

        await this.getImageData();

        await this.runner.run();
        this.setImageData();

        if (this.dataSource == 'camera') requestAnimationFrame(() => this.transfer());
    }

    async getImageData() {
        let w = this.w;
        let h = this.h;

        if (this.dataSource == 'camera') {
            await new Promise(resolve => Webcam.snap(resolve, this.inputCanvas));
        }
        let pixelData = this.inputCtx.getImageData(0, 0, w, h).data;

        for (let y = 0; y < h; y++) {
            for (let x = 0; x < w; x++) {
                this.inputView[(y * w + x) * 3] = pixelData[(y * w + x) * 4];
                this.inputView[(y * w + x) * 3 + 1] = pixelData[(y * w + x) * 4 + 1];
                this.inputView[(y * w + x) * 3 + 2] = pixelData[(y * w + x) * 4 + 2];
            }
        }
    }

    setImageData() {
        let w = this.w;
        let h = this.h;

        let imageData = new ImageData(w, h);

        for (let y = 0; y < h; y++) {
            for (let x = 0; x < w; x++) {
                imageData.data[(y * w + x) * 4] = this.outputView[(y * w + x) * 3];
                imageData.data[(y * w + x) * 4 + 1] = this.outputView[(y * w + x) * 3 + 1];
                imageData.data[(y * w + x) * 4 + 2] = this.outputView[(y * w + x) * 3 + 2];
                imageData.data[(y * w + x) * 4 + 3] = 255;
            }
        }

        this.outputCtx.putImageData(imageData, 0, 0);
    }

    setMessage(message: string) {
        let $message = document.getElementById('message');
        if (!$message) return;
        $message.textContent = message;
    }
};

window.addEventListener('DOMContentLoaded', () => {
    WebDNN.registerFetchDelegate((input, init) => {
        let url = ((input instanceof Request) ? input.url : input) as string;
        let ma = url.match(/([^/]+?.bin)(?:\?.*)?$/);

        if (ma) {
            // return fetch(`https://github.com/mil-tokyo/webdnn-hp/blob/master/src/static/models/neural_style_transfer/${ma[1]}?raw=true`);
            return fetch(`/models/neural_style_transfer/${ma[1]}`);
        } else {
            return fetch(input, init);
        }
    });

    if (location.search == '?run=1') {
        App.initialize();
    } else {
        let runAppButton = document.getElementById('runAppButton');
        if (!runAppButton) throw Error('#runAppButton is not found');
        runAppButton.addEventListener('click', () => App.initialize());
    }
});
