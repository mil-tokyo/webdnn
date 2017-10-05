import * as classNames from "classnames";
import * as React from "react";
import * as WebDNN from "webdnn";
import "../../../stylus/bootstrap.scss";
import { AppShell } from "../../common/components/app_shell/app_shell";
import Button from "../../common/components/button/button";
import { LayoutFrame } from "../../common/components/layout/layout";
import WebCam from "../../common/webcam";
import dom from "../../common/dom";
import Labels from "../../common/imagenet_labels";
import * as style from "./main_layer.scss";

declare function require(path: string): any;

const RunIcon = require('./ic_play_arrow_black_24px.svg');
const RandomIcon = require('./ic_autorenew_black_24px.svg');
const UploadIcon = require('./ic_file_upload_black_24px.svg');
const VideoIcon = require('./ic_videocam_black_24px.svg');
const PauseIcon = require('./ic_pause_black_24px.svg');

const IMAGE_PATH_LIST = [
    require('../../../static/images/0.png'),
    require('../../../static/images/1.png'),
    require('../../../static/images/2.png'),
    require('../../../static/images/3.png'),
    require('../../../static/images/4.png'),
    require('../../../static/images/5.png')
];
let random_image_index = Math.floor(Math.random() * IMAGE_PATH_LIST.length);

function softmax(x: Float32Array) {
    let max = -Infinity;
    for (let i = 0; i < x.length; i++) max = max > x[i] ? max : x[i];

    let exp = new Float32Array(x.length);
    let sum = 0;
    for (let i = 0; i < x.length; i++) {
        let e = Math.exp(x[i] - max);
        sum += e;
        exp[i] = e;
    }

    for (let i = 0; i < exp.length; i++) exp[i] /= sum;

    return exp;
}

interface Props extends React.HTMLAttributes<HTMLDivElement> {
    runner: WebDNN.DescriptorRunner;
}

interface State {
    isBusy: boolean
    isVideoMode: boolean
    isWebCamReady: boolean
    isContentLoaded: boolean
}

class MainLayer extends React.Component<Props, State> {
    webcam: WebCam;
    results: ({ label: string, prob: number }[] | null) = null;

    constructor() {
        super();
        this.webcam = new WebCam();
        this.state = {
            isBusy: false,
            isVideoMode: false,
            isWebCamReady: false,
            isContentLoaded: false
        };
    }

    /**
     * Event Handler
     */
    async onRandomImageButtonClick() {
        this.finalizeWebCam();
        this.setState({
            isVideoMode: false
        });
        await this.loadRandomImage();
    }

    async onUploadImageButtonClick() {
        this.finalizeWebCam();
        this.setState({
            isVideoMode: false
        });
        await this.uploadLocalImage();
    }

    async onVideoButtonClick() {
        this.setState({
            isVideoMode: true
        });
        await this.initializeWebCam();
    }

    async onRunButtonClick() {
        await this.run();
    }

    async onToggleButtonClick() {
        if (this.state.isBusy) {
            this.setState({
                isBusy: false
            });
        } else {
            this.setState({
                isBusy: true
            });
            await this.videoModeLoop();
        }
    }

    /**
     * Loading images
     */
    async loadRandomImage() {
        random_image_index++;
        if (random_image_index >= IMAGE_PATH_LIST.length) random_image_index = 0;

        let canvas = dom.getFromRef<HTMLCanvasElement>(this, 'inputImageCanvas');
        let image = await WebDNN.Image.loadImageByUrl(IMAGE_PATH_LIST[random_image_index]);
        let data = WebDNN.Image.getImageArrayFromDrawable(image);
        WebDNN.Image.setImageArrayToCanvas(data, image.naturalWidth, image.naturalHeight, canvas);

        this.setState({ isContentLoaded: true });
    }

    async uploadLocalImage() {
        let canvas = dom.getFromRef<HTMLCanvasElement>(this, 'inputImageCanvas');
        let image = await WebDNN.Image.loadImageByDialog();
        let data = WebDNN.Image.getImageArrayFromDrawable(image);
        WebDNN.Image.setImageArrayToCanvas(data, image.naturalWidth, image.naturalHeight, canvas);

        this.setState({ isContentLoaded: true });
    }

    async initializeWebCam(forceReInitialize: boolean = false) {
        if (!forceReInitialize && this.state.isWebCamReady) return;

        let video = dom.getFromRef<HTMLVideoElement>(this, 'previewVideo');
        this.setState({ isWebCamReady: false, isContentLoaded: false });
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

    /**
     * WebCam
     */

    async playVideo() {
        let video = dom.getFromRef<HTMLVideoElement>(this, 'previewVideo');

        try {
            await video.play();
            this.setState({ isContentLoaded: !video.paused });
        } catch (err) {
            this.setState({ isContentLoaded: false });
        }
    }

    async toggleCamera() {
        await this.initializeWebCam(true);
    }

    finalizeWebCam() {
        let video = dom.getFromRef<HTMLVideoElement>(this, 'previewVideo');

        if (video.srcObject) {
            for (let stream of video.srcObject.getTracks()) {
                stream.stop();
            }
        }

        this.setState({ isWebCamReady: false, isContentLoaded: false });
    }

    /**
     * Compute logic
     */
    async run() {
        let runner = this.props.runner;
        if (!runner) return;

        let inputImageCanvas = dom.getFromRef<HTMLCanvasElement>(this, 'inputImageCanvas');

        runner.getInputViews()[0].set(WebDNN.Image.getImageArrayFromCanvas(inputImageCanvas, {
            dstH: 224, dstW: 224, order: WebDNN.Image.Order.CHW,
            color: WebDNN.Image.Color.BGR,
            bias: [123.68, 116.779, 103.939]
        }));
        if (runner.backendName !== 'webgpu') {
            this.setState({ isBusy: true });
        }

        // Update screen
        await new Promise(resolve => {
            requestAnimationFrame(async () => {
                await runner.run();
                resolve();
            });
        });

        let output = runner.getOutputViews()[0].toActual();
        if (runner.backendName === 'webgl') output = softmax(output);
        this.results = WebDNN.Math.argmax(output, 5)
            .map((i: number) => ({
                label: Labels[i],
                prob: output[i]
            }));

        if (runner.backendName === 'webgpu') {
            //FIXME
            this.forceUpdate();
        } else {
            this.setState({ isBusy: false });
        }
    }

    async videoModeLoop() {
        let runner = this.props.runner;
        if (!runner) return;

        let video = dom.getFromRef<HTMLVideoElement>(this, 'previewVideo');

        runner.getInputViews()[0].set(WebDNN.Image.getImageArrayFromDrawable(video, {
            dstH: 224, dstW: 224, order: WebDNN.Image.Order.CHW,
            color: WebDNN.Image.Color.BGR,
            bias: [123.68, 116.779, 103.939]
        }));

        await runner.run();

        let output = runner.getOutputViews()[0].toActual();
        if (runner.backendName === 'webgl') output = softmax(output);
        this.results = WebDNN.Math.argmax(output, 5)
            .map((i: number) => ({
                label: Labels[i],
                prob: output[i]
            }));

        this.forceUpdate();

        if (this.state.isBusy) requestAnimationFrame(() => this.videoModeLoop());
    }

    render() {
        let runButton = this.state.isVideoMode ?
                        this.state.isBusy ?
                        ({
                            onClick: () => this.onToggleButtonClick(),
                            icon: <PauseIcon />,
                            label: 'Stop',
                            primary: true
                        }) :
                        ({
                            onClick: () => this.onToggleButtonClick(),
                            disabled: this.state.isBusy || !this.state.isContentLoaded,
                            icon: <RunIcon />,
                            label: 'Start',
                            primary: true
                        }) :
            {
                onClick: () => this.onRunButtonClick(),
                disabled: this.state.isBusy || !this.state.isContentLoaded,
                icon: <RunIcon />,
                label: 'Run',
                primary: true
            };

        return (
            <div className={ classNames(style.mainLayer, this.props.className) }>
                <AppShell title="ResNet50 Image Classification"
                          subTitle={ `backend: ${this.props.runner.backendName}` }
                          progressBar={ !this.state.isVideoMode && this.state.isBusy }
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
                              onClick: ev => this.onVideoButtonClick(),
                              disabled: this.state.isBusy,
                              icon: <VideoIcon />,
                              label: 'Video'
                          }, runButton] }>
                    <LayoutFrame fit block>
                        <LayoutFrame flex block>
                            <LayoutFrame fit block center>
                                <canvas ref="inputImageCanvas"
                                        className={ classNames(
                                            style.toggleDisplay,
                                            style.inputImageCanvas,
                                            this.state.isVideoMode ? null : style.active,
                                        ) } />
                                <video ref="previewVideo"
                                       playsInline={ true }
                                       className={ classNames(
                                           style.toggleDisplay,
                                           style.previewVideo,
                                           this.state.isVideoMode ? style.active : null,
                                       ) } />
                                {
                                    (this.state.isWebCamReady && !this.state.isContentLoaded) ?
                                    <LayoutFrame fit className={ style.playVideoButtonLayer }>
                                        <Button primary onClick={ ev => this.playVideo() }>
                                            <RunIcon />
                                            <span>Activate Camera</span>
                                        </Button>
                                    </LayoutFrame> : null
                                }

                            </LayoutFrame>
                        </LayoutFrame>
                        <LayoutFrame flex block>
                            <LayoutFrame fit column center className={ style.resultContainer }>
                                {
                                    this.results ? (
                                        <table className={ style.resultTable }>
                                            <tbody>
                                            { this.results.map((result, i) => (<tr key={ i }>
                                                <th>
                                                    <LayoutFrame column>
                                                    <span style={ {
                                                        opacity: result.prob / 2 + 0.5,
                                                    } }>{ result.label }</span>
                                                        <span className={ style.resultProb }
                                                              style={ {
                                                                  opacity: result.prob / 2 + 0.5,
                                                              } }
                                                        >{ (result.prob * 100).toFixed(1) + '%' }</span>
                                                    </LayoutFrame>
                                                </th>
                                                <td>
                                                    <div className={ style.resultBar }
                                                         style={ {
                                                             opacity: result.prob,
                                                             transform: `scaleX(${result.prob})`,
                                                             WebkitTransform: `scaleX(${result.prob})`,
                                                             MozTransform: `scaleX(${result.prob})`
                                                         } } />
                                                </td>
                                            </tr>)) }
                                            </tbody>
                                        </table>
                                    ) : (
                                        null
                                    )
                                }
                            </LayoutFrame>
                        </LayoutFrame>
                    </LayoutFrame>
                </AppShell>
            </div>
        );
    }
}

export default MainLayer;