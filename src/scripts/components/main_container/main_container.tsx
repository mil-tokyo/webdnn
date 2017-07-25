import * as classNames from "classnames";
import * as React from "react";
import TIL from "../../common/til";
import { Button } from "../button/button";
import { ControlBar } from "../control_bar/control_bar";
import { Header } from "../header/header";
import { ProgressBar } from "../progress_bar/progress_bar";
import * as style from "./main_container.scss";

interface Props extends React.HTMLAttributes<HTMLElement> {
    onInitialized: () => any
}

interface State {
    running: boolean,
    isUserActionRequiredToPlayVideo: boolean,
    mode: Mode
}

enum Mode {
    None = 0,
    RandomImage,
    UserImage,
    WebCamPhoto,
    WebCamVideo
}

const MAX_RANDOM_IMAGE = 6;

export default class MainContainer extends React.Component<Props, State> {
    private runner: WebDNN.DescriptorRunner<WebDNN.GraphDescriptor>;
    private inputView: WebDNN.SymbolicFloat32Array;
    private outputView: WebDNN.SymbolicFloat32Array;
    private randomImageCount: number = Math.floor(Math.random() * MAX_RANDOM_IMAGE);

    constructor() {
        super();
        this.state = {
            running: false,
            isUserActionRequiredToPlayVideo: false,
            mode: Mode.None
        };
    }

    componentDidMount() {
        this.initializeAsync()
            .then(() => this.props.onInitialized());
    }

    onUserActionMessageClick(ev: React.MouseEvent<HTMLDivElement>) {
        if (!this.refs['previewVideo']) throw Error('previewVideo is not found');
        let $video = this.refs['previewVideo'] as HTMLVideoElement;

        ev.stopPropagation();
        ev.preventDefault();
        $video.play();

        this.setState({
            isUserActionRequiredToPlayVideo: false
        });
    }

    async onVideoClick() {
        if (this.state.mode !== Mode.WebCamPhoto) return;
        this.loadImageFromVideo(true);
        this.setState({
            mode: Mode.None
        });
        await this.run();
    }

    async onRandomImageButtonClick() {
        this.setState({ mode: Mode.RandomImage });
        await this.fetchRandomImage();
        await this.run();
    }

    async onUploadImageButtonClick() {
        this.setState({ mode: Mode.UserImage });
        await this.uploadImage();
        await this.run();
    }

    async onWebcamPhotoButtonClick() {
        if (this.state.mode == Mode.WebCamPhoto) return;
        this.setState({ mode: Mode.WebCamPhoto });

        try {
            await this.initializeWebCam();
        } catch (e) {
            alert('Access to web camera is denied. Please check your browser settings.');
            this.setState({ mode: Mode.None });
        }
    }

    async onWebcamVideoButtonClick() {
        if (this.state.mode == Mode.WebCamVideo) return;
        if (this.runner.backendName !== 'webgpu') {
            alert(`Sorry, real-time video style transfer can be performed only in WebGPU backend. current backend is "${this.runner.backendName}".`);
            return;
        }

        this.setState({ mode: Mode.WebCamVideo });

        if (this.state.mode !== Mode.WebCamPhoto) {
            try {
                await this.initializeWebCam();
            } catch (e) {
                alert('Access to web camera is denied. Please check your browser settings.');
                this.setState({ mode: Mode.None });
            }

            await this.runVideoModeLoop();
        }
    }

    private async initializeAsync() {
        this.runner = await WebDNN.load('./neural_style_transfer');
        this.inputView = this.runner.getInputViews()[0];
        this.outputView = this.runner.getOutputViews()[0];
    }

    async initializeWebCam() {
        let stream: MediaStream;
        stream = await navigator.mediaDevices.getUserMedia({
            video: true,
            audio: false
        });

        if (!this.refs['previewVideo']) throw Error('previewVideo is not found');
        let $video = this.refs['previewVideo'] as HTMLVideoElement;

        $video.srcObject = stream;

        return new Promise<void>((resolve, reject) => {
            $video.onplay = () => {
                $video.onplay = () => {};
                resolve();
            };

            try {
                $video.play();
            } catch (e) {
                console.dir(e);
                this.setState({ isUserActionRequiredToPlayVideo: true });
            }
        });
    }

    async runVideoModeLoop(flagContinuous: boolean = false) {
        if (this.state.mode !== Mode.WebCamVideo) return;

        this.loadImageFromVideo(false);
        await this.run(flagContinuous);
        requestAnimationFrame(() => this.runVideoModeLoop(true));
    }

    finalizeWebCam() {
        if (!this.refs['previewVideo']) throw Error('previewVideo is not found');
        let $video = this.refs['previewVideo'] as HTMLVideoElement;

        $video.pause();
        if ($video.srcObject) {
            for (let track of $video.srcObject.getVideoTracks()) track.stop();
        }
    }

    private async run(flagContinuous: boolean = false): Promise<void> {
        let $contentCanvas = this.refs['contentCanvas'] as (HTMLCanvasElement | null);
        if (!$contentCanvas) throw Error('contentCanvas is not found');

        let $outputCanvas = this.refs['outputCanvas'] as (HTMLCanvasElement | null);
        if (!$outputCanvas) throw Error('outputCanvas is not found');

        const width = $contentCanvas.width;
        const height = $contentCanvas.height;

        if (!flagContinuous) {
            $outputCanvas.style.width = width * 2 + 'px';
            $outputCanvas.style.height = height * 2 + 'px';
            $outputCanvas.width = width;
            $outputCanvas.height = height;
        }

        this.inputView.set(await TIL.loadFromCanvas($contentCanvas));

        if (!flagContinuous) this.setState({ running: true });
        await this.runner.run();
        if (!flagContinuous) this.setState({ running: false });

        TIL.drawImageArray($outputCanvas, this.outputView.toActual(), width, height);
    }

    private setContentImage($img: HTMLImageElement | HTMLVideoElement) {
        let $contentCanvas = this.refs['contentCanvas'] as (HTMLCanvasElement | null);
        if (!$contentCanvas) throw Error('contentCanvas is not found');
        $contentCanvas.style.width = '';
        $contentCanvas.style.height = '';

        let ctx = $contentCanvas.getContext('2d');
        if (!ctx) throw Error('Context initialization failed');

        const naturalWidth = ($img as HTMLImageElement).naturalWidth || ($img as HTMLVideoElement).videoWidth;
        const naturalHeight = ($img as HTMLImageElement).naturalHeight || ($img as HTMLVideoElement).videoHeight;
        let imageAspect = naturalHeight / naturalWidth;
        let canvasAspect = $contentCanvas.clientHeight / $contentCanvas.clientWidth;
        let width: number;
        let height: number;
        if (canvasAspect > imageAspect) {
            width = Math.min(naturalWidth, $contentCanvas.clientWidth);
            height = width * imageAspect;
        } else {
            height = Math.min(naturalHeight, $contentCanvas.clientHeight);
            width = height / imageAspect;
        }
        width = 192;
        height = 144;


        $contentCanvas.style.width = width + 'px';
        $contentCanvas.style.height = height + 'px';
        $contentCanvas.width = width;
        $contentCanvas.height = height;
        ctx.drawImage($img, 0, 0, width, height);
    }

    private async uploadImage() {
        let $img: HTMLImageElement;
        try {
            $img = await TIL.loadByDialog();
        } catch (e) {
            console.warn(e);
            return;
        }

        this.setContentImage($img);
    }

    private async fetchRandomImage() {
        let $img: HTMLImageElement;
        this.randomImageCount = (this.randomImageCount + 1) % MAX_RANDOM_IMAGE;

        try {
            $img = await TIL.loadByUrl(`./assets/images/${this.randomImageCount}.png`);
        } catch (e) {
            console.warn(e);
            return;
        }

        this.setContentImage($img);
    }

    private loadImageFromVideo(flagPause: boolean = true) {
        if (!this.refs['previewVideo']) throw Error('previewVideo is not found');
        let $video = this.refs['previewVideo'] as HTMLVideoElement;
        if (flagPause) $video.pause();

        this.setContentImage($video);
    }

    componentDidUpdate(prevProps: Props, prevState: State) {
        if ((prevState.mode === Mode.WebCamVideo || prevState.mode === Mode.WebCamPhoto) &&
            (this.state.mode !== Mode.WebCamVideo && this.state.mode !== Mode.WebCamPhoto)) {
            this.finalizeWebCam();
        }
    }

    render() {
        return (
            <main className={classNames(style.mainContainer, this.props.className)}>
                <ProgressBar running={this.state.running} />
                <Header title="WebDNN Style Transfer" />
                <div className={classNames(style.mainContainer, this.props.className)}>
                    <div className={style.mainContainerImages}>
                        <div className={style.mainContainerInputs}>
                            <div className={style.mainContainerContent}>
                                <header className={style.mainContainerHeader}>
                                    Content
                                </header>
                                <div className={classNames(style.mainContainerUserActionMessage, {
                                    'MainContainer-UserActionMessage--active': (this.state.mode == Mode.WebCamPhoto || this.state.mode == Mode.WebCamVideo)
                                    && this.state.isUserActionRequiredToPlayVideo
                                })} onClick={(ev) => this.onUserActionMessageClick(ev)}>Tap to enable video
                                </div>
                                <video ref="previewVideo" className={classNames(style.mainContainerPreviewVideo, {
                                    'MainContainer-PreviewVideo--active': this.state.mode == Mode.WebCamPhoto || this.state.mode == Mode.WebCamVideo
                                })}
                                       onClick={(ev) => this.onVideoClick()} />
                                <canvas className={style.mainContainerContentCanvas} ref="contentCanvas" />
                            </div>
                            <div className={style.mainContainerStyle}>
                                <header className={style.mainContainerHeader}>
                                    Style
                                </header>
                                <img className={style.mainContainerStyleImage}
                                     src="./assets/neural_style_transfer-style.jpg" />
                            </div>
                        </div>
                        <div className={style.mainContainerOutput}>
                            <header className={style.mainContainerHeader}>
                                Output
                            </header>
                            <canvas className={style.mainContainerOutputCanvas} ref="outputCanvas" />
                        </div>
                    </div>
                </div>
                <ControlBar>
                    <Button icon="./icons/ic_autorenew_white_24dp_1x.png"
                            srcSet="./icons/ic_autorenew_white_24dp_2x.png 2x"
                            disabled={this.state.running}
                            onClick={() => this.onRandomImageButtonClick()}>
                        Random Image
                    </Button>
                    <Button icon="./icons/ic_photo_size_select_actual_white_24dp_1x.png"
                            srcSet="./icons/ic_photo_size_select_actual_white_24dp_2x.png 2x"
                            disabled={this.state.running}
                            onClick={() => this.onUploadImageButtonClick()}>
                        Upload Image
                    </Button>
                    <Button icon="./icons/ic_photo_camera_white_24dp_1x.png"
                            srcSet="./icons/ic_photo_camera_white_24dp_2x.png 2x"
                            disabled={this.state.running}
                            active={this.state.mode === Mode.WebCamPhoto}
                            onClick={() => this.onWebcamPhotoButtonClick()}>
                        Webcam Photo
                    </Button>
                    <Button icon="./icons/ic_videocam_white_24dp_1x.png"
                            srcSet="./icons/ic_videocam_white_24dp_2x.png 2x"
                            disabled={this.state.running}
                            active={this.state.mode === Mode.WebCamVideo}
                            onClick={() => this.onWebcamVideoButtonClick()}>
                        Webcam Video
                    </Button>
                </ControlBar>
            </ main>
        );
    }
}