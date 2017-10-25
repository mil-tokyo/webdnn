import * as classNames from "classnames";
import * as React from "react";
import * as WebDNN from "webdnn";
import "../../../stylus/bootstrap.scss";
import { AppShell } from "../../common/components/app_shell/app_shell";
import Button from "../../common/components/button/button";
import { LayoutFrame } from "../../common/components/layout/layout";
import WebCam from "../../common/webcam";
import dom from "../../common/dom";
import * as style from "./main_layer.scss";

declare function require(path: string): any;

const RunIcon = require('./ic_play_arrow_black_24px.svg');
const PauseIcon = require('./ic_pause_black_24px.svg');
const TakePhotoIcon = require('./ic_add_a_photo_black_24px.svg');
const RandomIcon = require('./ic_autorenew_black_24px.svg');
const UploadIcon = require('./ic_file_upload_black_24px.svg');
const PhotoIcon = require('./ic_photo_camera_black_24px.svg');
const VideoIcon = require('./ic_videocam_black_24px.svg');
const SwitchCameraIcon = require('./ic_switch_camera_black_24px.svg');
const SwitchVideoIcon = require('./ic_switch_video_black_24px.svg');

const IMAGE_PATH_LIST = [
    require('../../../static/images/0.png'),
    require('../../../static/images/1.png'),
    require('../../../static/images/2.png'),
    require('../../../static/images/5.png')
];
let random_image_index = Math.floor(Math.random() * IMAGE_PATH_LIST.length);


interface Props extends React.HTMLAttributes<HTMLDivElement> {
    runner: WebDNN.DescriptorRunner;
}

enum InputResource {
    None,
    Image,
    Photo,
    Video
}

interface State {
    isBusy: boolean,
    isContentLoaded: boolean,
    inputResource: InputResource,
    isWebCamReady: boolean,
    isVideoModeRunning: boolean,
    isFirstTime: boolean,
    isVideoPlaying: boolean
}

enum ResizeState {
    sleep,
    resizing,
    finish
}

class MainLayer extends React.Component<Props, State> {
    resizeHandler: () => void;
    resizeState: ResizeState = ResizeState.sleep;
    webcam: WebCam;

    constructor() {
        super();
        this.resizeHandler = () => this.onResize();
        this.webcam = new WebCam();
        this.state = {
            isBusy: false,
            isContentLoaded: false,
            inputResource: InputResource.None,
            isWebCamReady: false,
            isFirstTime: true,
            isVideoModeRunning: false,
            isVideoPlaying: false
        };
    }

    /**
     * Event Handler
     */

    onResize() {
        if (this.resizeState == ResizeState.resizing) return;
        this.resizeState = ResizeState.resizing;

        let handler = () => {
            if (this.resizeState == ResizeState.finish) {
                this.resetCanvasAll();
                // noinspection JSIgnoredPromiseFromCall
                this.loadStyleImage();

            } else {
                this.resizeState = ResizeState.finish;
                requestAnimationFrame(handler);
            }
        };

        requestAnimationFrame(handler);
    }

    async onRandomImageButtonClick() {
        this.setState({
            inputResource: InputResource.Image,
            isContentLoaded: false,
            isVideoModeRunning: false
        });
        this.resetContentCanvas();
        this.resetOutputCanvas();

        await this.loadRandomImage();

        this.setState({ isContentLoaded: true });
    }

    async onUploadImageButtonClick() {
        this.setState({
            inputResource: InputResource.Image,
            isContentLoaded: false,
            isVideoModeRunning: false
        });
        this.resetContentCanvas();
        this.resetOutputCanvas();

        await this.uploadLocalImage();

        this.setState({ isContentLoaded: true });
    }

    async onPhotoButtonClick() {
        this.setState({
            inputResource: InputResource.None,
            isContentLoaded: false,
            isVideoModeRunning: false

        });

        this.resetContentCanvas();
        this.resetOutputCanvas();

        try {
            await this.initializeWebCam();
            this.setState({
                inputResource: InputResource.Photo,
            });

        } catch (e) {
            console.error(e.message);
            this.finalizeWebCam();
            this.setState({
                inputResource: InputResource.None,
            });
        }
    }

    async onVideoButtonClick() {
        this.setState({
            inputResource: InputResource.None,
            isContentLoaded: false,
            isVideoModeRunning: false,
            isFirstTime: false
        });

        this.resetContentCanvas();
        this.resetOutputCanvas();

        try {
            await this.initializeWebCam();
            this.setState({
                inputResource: InputResource.Video,
                isContentLoaded: true
            });

        } catch (e) {
            console.error(e.message);
            this.finalizeWebCam();
            this.setState({
                inputResource: InputResource.None,
                isContentLoaded: false
            });
        }
    }

    onTakePhotoButtonClick() {
        // noinspection JSIgnoredPromiseFromCall
        this.takePhoto();
        this.finalizeWebCam();
    }

    onRunButtonClick() {
        // noinspection JSIgnoredPromiseFromCall
        this.run();
    }

    onToggleButtonClick() {
        if (this.state.isVideoModeRunning) {
            this.setState({
                isVideoModeRunning: false
            });
        } else {
            this.setState({
                isVideoModeRunning: true
            });
            // noinspection JSIgnoredPromiseFromCall
            this.videoModeLoop()
        }
    }

    componentDidMount() {
        window.addEventListener('resize', this.resizeHandler);
        // noinspection JSIgnoredPromiseFromCall
        this.loadStyleImage();
    }

    componentWillUnmount() {
        window.removeEventListener('resize', this.resizeHandler);
    }

    /**
     * Loading images
     */

    resetContentCanvas() {
        let canvas = dom.getFromRef<HTMLCanvasElement>(this, 'contentCanvas');
        let context = canvas.getContext('2d');
        if (!context) throw Error('Context initialization failed');

        context.clearRect(0, 0, canvas.width, canvas.height);

        this.setState({
            isContentLoaded: false
        });
    }

    resetOutputCanvas() {
        let canvas = dom.getFromRef<HTMLCanvasElement>(this, 'outputCanvas');
        let context = canvas.getContext('2d');
        if (!context) throw Error('Context initialization failed');

        context.clearRect(0, 0, canvas.width, canvas.height);
    }

    resetStyleCanvas() {
        let canvas = dom.getFromRef<HTMLCanvasElement>(this, 'styleCanvas');
        let context = canvas.getContext('2d');
        if (!context) throw Error('Context initialization failed');

        context.clearRect(0, 0, canvas.width, canvas.height);
    }

    resetCanvasAll() {
        this.resetContentCanvas();
        this.resetStyleCanvas();
        this.resetOutputCanvas();
    }

    async loadStyleImage() {
        if (this.state.isWebCamReady) {this.finalizeWebCam();}

        let styleCanvas = dom.getFromRef<HTMLCanvasElement>(this, 'styleCanvas');
        let image = await WebDNN.Image.loadImageByUrl(require('./neural_style_transfer-style.jpg'));
        let data = WebDNN.Image.getImageArrayFromDrawable(image);

        WebDNN.Image.setImageArrayToCanvas(data, image.naturalWidth, image.naturalHeight, styleCanvas, {
            dstH: styleCanvas.height, dstW: styleCanvas.width
        });
    }

    async loadRandomImage() {
        if (this.state.isWebCamReady) {this.finalizeWebCam();}

        random_image_index++;
        if (random_image_index >= IMAGE_PATH_LIST.length) random_image_index = 0;

        let styleCanvas = dom.getFromRef<HTMLCanvasElement>(this, 'contentCanvas');
        let image = await WebDNN.Image.loadImageByUrl(IMAGE_PATH_LIST[random_image_index]);
        let data = WebDNN.Image.getImageArrayFromDrawable(image);

        WebDNN.Image.setImageArrayToCanvas(data, image.naturalWidth, image.naturalHeight, styleCanvas, {
            dstH: styleCanvas.height, dstW: styleCanvas.width
        });

        this.setState({ isContentLoaded: true });
    }

    async uploadLocalImage() {
        let styleCanvas = dom.getFromRef<HTMLCanvasElement>(this, 'contentCanvas');
        let image = await WebDNN.Image.loadImageByDialog();
        let data = WebDNN.Image.getImageArrayFromDrawable(image);

        WebDNN.Image.setImageArrayToCanvas(data, image.naturalWidth, image.naturalHeight, styleCanvas, {
            dstH: styleCanvas.height, dstW: styleCanvas.width
        });

        this.setState({ isContentLoaded: true });
    }

    /**
     * WebCam
     */
    async initializeWebCam(forceReInitialize: boolean = false) {
        if (!forceReInitialize && this.state.isWebCamReady) return;

        let video = dom.getFromRef<HTMLVideoElement>(this, 'previewVideo');
        this.setState({ isWebCamReady: false, isVideoPlaying: false });
        video.srcObject = null;

        try {
            video.srcObject = await this.webcam.getNextDeviceStream();
        } catch (err) {
            alert('Sorry, WebCamera on this device cannot be accessed.');
            return;
        }

        this.setState({ isWebCamReady: true });
        await this.playVideo();
    }

    async playVideo() {
        let video = dom.getFromRef<HTMLVideoElement>(this, 'previewVideo');

        try {
            await video.play();
            this.setState({ isVideoPlaying: !video.paused });
        } catch (err) {
            this.setState({ isVideoPlaying: false });
        }
    }

    async toggleCamera() {
        await this.initializeWebCam(true);
    }

    async takePhoto() {
        let video = dom.getFromRef<HTMLVideoElement>(this, 'previewVideo');
        video.pause();

        let data = (await WebDNN.Image.getImageArrayFromDrawable(video, {
            dstW: 192, dstH: 144, order: WebDNN.Image.Order.CHW
        })) as Float32Array;
        WebDNN.Image.setImageArrayToCanvas(data, 192, 144, dom.getFromRef<HTMLCanvasElement>(this, 'contentCanvas'), {
            order: WebDNN.Image.Order.CHW,
        });

        this.setState({ isContentLoaded: true });
    }

    finalizeWebCam() {
        let video = dom.getFromRef<HTMLVideoElement>(this, 'previewVideo');

        if (video.srcObject) {
            for (let stream of video.srcObject.getTracks()) {
                stream.stop();
            }
        }

        this.setState({ isWebCamReady: false });
    }

    /**
     * Compute logic
     */
    async videoModeLoop() {
        let video = dom.getFromRef<HTMLVideoElement>(this, 'previewVideo');
        let contentCanvas = dom.getFromRef<HTMLCanvasElement>(this, 'contentCanvas');

        let data = (await WebDNN.Image.getImageArrayFromDrawable(video, {
            dstW: 192, dstH: 144, order: WebDNN.Image.Order.CHW
        })) as Float32Array;
        WebDNN.Image.setImageArrayToCanvas(data, 192, 144, contentCanvas);

        let runner = this.props.runner;
        if (!runner) return;

        runner.getInputViews()[0].set(data);

        await runner.run();

        let outputCanvas = dom.getFromRef<HTMLCanvasElement>(this, 'outputCanvas');
        WebDNN.Image.setImageArrayToCanvas(runner.getOutputViews()[0].toActual(), 192, 144, outputCanvas, {
            order: WebDNN.Image.Order.CHW,
        });

        if (this.state.inputResource == InputResource.Video && this.state.isVideoModeRunning) {
            requestAnimationFrame(() => this.videoModeLoop());
        }
    }

    async run() {
        let runner = this.props.runner;
        if (!runner) return;

        if (this.state.isFirstTime) {
            this.setState({
                isFirstTime: false
            });
        }

        let contentCanvas = dom.getFromRef<HTMLCanvasElement>(this, 'contentCanvas');

        runner.getInputViews()[0].set(WebDNN.Image.getImageArrayFromCanvas(contentCanvas, {
            dstW: 192, dstH: 144, order: WebDNN.Image.Order.CHW
        }));

        this.setState({ isBusy: true });

        // Update screen
        await new Promise(resolve => {
            requestAnimationFrame(async () => {
                await runner.run();
                resolve();
            });
        });
        this.setState({ isBusy: false });

        let outputCanvas = dom.getFromRef<HTMLCanvasElement>(this, 'outputCanvas');
        WebDNN.Image.setImageArrayToCanvas(runner.getOutputViews()[0].toActual(), 192, 144, outputCanvas, {
            order: WebDNN.Image.Order.CHW,
        });
    }

    render() {
        return (
            <div className={ classNames(style.mainLayer, this.props.className) }>
                <AppShell title="Neural Style Transfer"
                          subTitle={ `backend: ${this.props.runner.backendName}` }
                          progressBar={ this.state.isBusy }
                          bottomBar={ [{
                              onClick: ev => this.onRandomImageButtonClick(),
                              disabled: this.state.isBusy,
                              icon: <RandomIcon />,
                              label: 'Random'
                          }, {
                              onClick: ev => this.onUploadImageButtonClick(),
                              disabled: this.state.isBusy,
                              icon: <UploadIcon />,
                              label: 'Upload'
                          }, {
                              onClick: ev => this.onPhotoButtonClick(),
                              disabled: this.state.isBusy,
                              icon: <PhotoIcon />,
                              label: 'Photo'
                          }, {
                              onClick: ev => this.onVideoButtonClick(),
                              disabled: this.state.isBusy,
                              icon: <VideoIcon />,
                              label: 'Video'
                          }] }>
                    <LayoutFrame className={ style.canvasContainer } flex block>
                        <LayoutFrame className={ style.inputImageContainer } autoReverse>
                            <LayoutFrame className={ style.contentImageContainer } center>
                                <canvas ref="contentCanvas" className={ style.contentCanvas }
                                        style={ {
                                            display:
                                                (
                                                    (this.state.inputResource == InputResource.Video) ||
                                                    (this.state.inputResource == InputResource.Photo && !this.state.isContentLoaded)
                                                ) ? 'none' : ''
                                        } } />
                                <video ref="previewVideo"
                                       playsInline={ true }
                                       className={ classNames(
                                           style.previewVideo,
                                           this.state.isWebCamReady ? style.active : null,
                                       ) } />
                                <p className={ style.canvasLabel }>Content</p>
                                {
                                    (this.state.isWebCamReady && !this.state.isVideoPlaying) ?
                                    <LayoutFrame fit className={ style.playVideoButtonLayer }>
                                        <Button primary onClick={ ev => this.playVideo() }>
                                            <RunIcon />
                                            <span>Activate Camera</span>
                                        </Button>
                                    </LayoutFrame> : null
                                }
                            </LayoutFrame>
                            <LayoutFrame className={ style.styleImageContainer } center>
                                <canvas ref="styleCanvas" className={ style.styleCanvas } />
                                <p className={ style.canvasLabel }>Style</p>
                            </LayoutFrame>
                        </LayoutFrame>
                        <LayoutFrame className={ style.outputImageContainer } center>
                            {
                                this.state.isFirstTime ? (
                                    this.state.isContentLoaded ? (
                                        <span>Click "Run" button</span>
                                    ) : (
                                        <span>Select content image from bottom buttons</span>
                                    )
                                ) : null
                            }
                            <canvas ref="outputCanvas"
                                    className={ style.outputCanvas }
                                    style={ { display: this.state.isFirstTime ? 'none' : '' } } />
                            <p className={ style.canvasLabel }>Output</p>
                        </LayoutFrame>
                    </LayoutFrame>
                    <LayoutFrame column>
                        {
                            this.state.inputResource == InputResource.Photo ? (
                                this.state.isContentLoaded ? (
                                    <LayoutFrame row>
                                        <Button primary
                                                disabled={ this.state.isBusy || !this.state.isContentLoaded }
                                                className={ style.useThisPhotoButton }
                                                onClick={ ev => this.onRunButtonClick() }>
                                            <RunIcon />
                                            <span>Run</span>
                                        </Button>
                                        <Button disabled={ this.state.isBusy }
                                                onClick={ ev => this.onPhotoButtonClick() }
                                                className={ style.retakeButton }>
                                            <TakePhotoIcon />
                                            <span>Retake</span>
                                        </Button>
                                    </LayoutFrame>
                                ) : (
                                    <LayoutFrame row>
                                        <Button disabled={ this.state.isBusy || !this.state.isWebCamReady }
                                                onClick={ ev => this.toggleCamera() }>
                                            <SwitchCameraIcon />
                                            <span>Switch Camera</span>
                                        </Button>
                                        <Button disabled={ this.state.isBusy || !this.state.isWebCamReady || !this.state.isVideoPlaying }
                                                onClick={ ev => this.onTakePhotoButtonClick() }
                                                className={ style.snapButton }>
                                            <TakePhotoIcon />
                                            <span>Take Photo</span>
                                        </Button>
                                    </LayoutFrame>
                                )
                            ) : this.state.inputResource == InputResource.Video ? (
                                this.state.isVideoModeRunning ? (
                                    <Button primary
                                            disabled={ this.state.isBusy || !this.state.isContentLoaded }
                                            onClick={ ev => this.onToggleButtonClick() }>
                                        <PauseIcon />
                                        <span>Stop</span>
                                    </Button>
                                ) : (
                                    <LayoutFrame row>
                                        <Button disabled={ this.state.isBusy || !this.state.isWebCamReady }
                                                onClick={ ev => this.toggleCamera() }>
                                            <SwitchVideoIcon />
                                            <span>Switch Camera</span>
                                        </Button>
                                        <Button primary
                                                disabled={ this.state.isBusy || !this.state.isContentLoaded || !this.state.isVideoPlaying }
                                                onClick={ ev => this.onToggleButtonClick() }>
                                            <RunIcon />
                                            <span>Start</span>
                                        </Button>
                                    </LayoutFrame>
                                )
                            ) : (
                                    <Button primary
                                            disabled={ this.state.isBusy || !this.state.isContentLoaded }
                                            onClick={ ev => this.onRunButtonClick() }>
                                        <RunIcon />
                                        <span>Run</span>
                                    </Button>
                                )
                        }
                    </LayoutFrame>
                </AppShell>
            </div>
        );
    }
}

export default MainLayer;