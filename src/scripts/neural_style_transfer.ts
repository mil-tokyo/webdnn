/// <reference path="../libs/webdnn.d.ts" />
import "../style/neural_style_transfer.scss";
import InitializingView from "./modules/initializing_view";
import WebCam from "./modules/webcam";

const KEY_WEBGPU_LAST_STATUS = 'webgpu_last_status';
const KEY_FLAG_WEBGPU_DISABLED_ALERT = 'flag_webgpu_disabled_alert';

const NUM_RANDOM_IMAGE = 6;

enum State {
    INITIALIZING,
    STAND_BY,
    RUNNING,
    ERROR,
}

type DataSource = 'sample' | 'photo' | 'video';

const App = new class {
    runners: { [key: string]: WebDNN.DescriptorRunner };
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
    backendSelect: HTMLSelectElement;
    webcam: WebCam;
    lastStatus: string = '';

    async initialize() {
        let select = document.getElementById('backend') as HTMLSelectElement;
        if (!select) throw Error('#backend is not found.');
        this.backendSelect = select;

        let availability = WebDNN.getBackendAvailability();
        if (availability.status['webgpu']) {
            this.lastStatus = localStorage.getItem(KEY_WEBGPU_LAST_STATUS) || 'none';
            switch (this.lastStatus) {
                case 'none':
                    break;

                case 'running':
                case 'crashed':
                    availability.status['webgpu'] = false;
                    localStorage.setItem(KEY_WEBGPU_LAST_STATUS, 'crashed');

                    console.warn('This browser supports WebGPU. However, it was crashed at last execution with WebGPU. Therefore, WebDNN disabled WebGPU backend temporally.');

                    if (!localStorage.getItem(KEY_FLAG_WEBGPU_DISABLED_ALERT)) {
                        alert('This browser supports WebGPU. However, it was crashed at last execution with WebGPU. \n\nTherefore, WebDNN disabled WebGPU backend temporally.');
                        localStorage.setItem(KEY_FLAG_WEBGPU_DISABLED_ALERT, '1');
                    }
                    break;

                case 'completed':
                    break;
            }
        }

        if (!availability.status['webgpu']) {
            let option = document.querySelector('option[value="webgpu"]') as HTMLOptionElement;
            if (option) option.disabled = true;
            select.value = 'webassembly';
        }

        if (!availability.status['webassembly']) {
            let option = document.querySelector('option[value="webassembly"]') as HTMLOptionElement;
            if (option) option.disabled = true;
            throw Error('This browser does not support either WebGPU nor WebAssembly/asm.js backends');
        }
        select.addEventListener('change', () => this.onBackendSelectChange());

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

        this.runners = {};
        await this.initBackendAsync(this.backendSelect.value, (loaded, total) => initializingView.updateProgress(loaded / total));

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

        await this.updateDataSource();
        initializingView.remove();
    }

    onDataSourceSelectChange() {
        this.updateDataSource();
    }

    onBackendSelectChange() {
        this.initBackendAsync(this.backendSelect.value);
    }

    async onPlayButtonClick() {
        switch (this.state) {
            case State.STAND_BY:
                await this.setState(State.RUNNING);
                break;

            case State.RUNNING:
                await this.setState(State.STAND_BY);
                break;

            default:
                break;
        }
    }

    async initBackendAsync(backend: string, callback?: (loaded: number, total: number) => void) {
        await this.setState(State.INITIALIZING);

        await WebDNN.init([backend]);

        if (backend in this.runners) {
            this.runner = this.runners[backend];
        } else {
            this.runner = this.runners[backend] = WebDNN.gpu.createDescriptorRunner();
            await this.runner.load('./models/neural_style_transfer', callback);
        }

        this.inputView = (await this.runner.getInputViews())[0];
        this.outputView = (await this.runner.getOutputViews())[0];

        await this.setState(State.STAND_BY);
    }

    async updateDataSource() {
        this.dataSource = this.dataSourceSelect.value as DataSource;
        this.sampleContainer.style.display = this.dataSource == 'sample' ? 'block' : 'none';
        this.cameraContainer.style.display = (this.dataSource == 'video' || this.dataSource == 'photo') ?
                                             'block' :
                                             'none';

        switch (this.dataSource) {
            case 'photo':
            case 'video':
                await this.setState(State.INITIALIZING);
                await this.initializeCamera();
                await this.setState(State.STAND_BY);
                break;

            case 'sample':
                await this.setState(State.INITIALIZING);
                this.finalizeCamera();
                await this.loadSampleImageToPreview();
                await this.setState(State.STAND_BY);
                break;
        }
    }

    initializeCamera() {
        return new Promise(resolve => {
            this.webcam = new WebCam({
                width: 192,
                height: 144,
                fps: 60,
                flip_horiz: false,
                image_format: 'png',
                force_flash: false,
                swfURL: '/webdnn/webcam.swf',
                unfreeze_snap: this.dataSource == 'video'
            });
            this.webcam.on('live', resolve);
            this.webcam.on('error', (err) => {
                console.error(err);
                this.setMessage(err);
                this.setState(State.ERROR);
            });
            this.webcam.attach('#cameraContainer');
        });
    }

    finalizeCamera() {
        if (this.webcam) this.webcam.reset();
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

                if (this.dataSource == 'video') {
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

        if (this.runner.backend === 'webgpu' && this.lastStatus === 'none') {
            localStorage.setItem(KEY_WEBGPU_LAST_STATUS, 'running');
            this.lastStatus = 'running';
        }
        await this.runner.run();
        if (this.runner.backend === 'webgpu' && this.lastStatus === 'running') {
            localStorage.setItem(KEY_WEBGPU_LAST_STATUS, 'completed');
            this.lastStatus = 'completed';
        }
        this.setImageData();

        if (this.dataSource == 'video') requestAnimationFrame(() => this.transfer());
    }

    async getImageData() {
        let w = this.w;
        let h = this.h;

        if (this.dataSource == 'photo') {
            await new Promise(resolve => {
                this.webcam.freeze();
                this.webcam.snap(resolve, this.inputCanvas);
            });

        } else if (this.dataSource == 'video') {
            await new Promise(resolve => {
                this.webcam.snap(resolve, this.inputCanvas);
            });
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
    WebDNN.registerTransformDelegate((url: string) => {
        let ma = url.match(/([^/]+)(?:\?.*)?$/);

        if (ma) {
            return `https://mil-tokyo.github.io/webdnn-data/models/neural_style_transfer/${ma[1]}?raw=true`;
        } else {
            return url;
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
