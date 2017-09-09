import * as classNames from "classnames";
import * as React from "react";
import * as WebDNN from "webdnn";
import "../../../../stylus/bootstrap.scss";
import Button from "../../../common/components/button/button";
import { LayoutFrame } from "../../../common/components/layout/layout";
import NavbarLayer from "../../../common/components/navbar_layer/navbar_layer";
import ProgressBar from "../../../common/components/progress_bar/progress_bar";
import dom from "../../../common/dom";
import Labels from "../../../common/imagenet_labels";
import * as style from "./main_layer.scss";

declare function require(path: string): any;

const RunIcon = require('./ic_play_arrow_black_24px.svg');
const RandomIcon = require('./ic_autorenew_black_24px.svg');
const UploadIcon = require('./ic_file_upload_black_24px.svg');

const IMAGE_PATH_LIST = [
    require('../../../../assets/images/0.png'),
    require('../../../../assets/images/1.png'),
    require('../../../../assets/images/2.png'),
    require('../../../../assets/images/3.png'),
    require('../../../../assets/images/4.png'),
    require('../../../../assets/images/5.png')
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
    runner: WebDNN.DescriptorRunner<WebDNN.GraphDescriptor>;
}

interface State {
    isBusy: boolean,
    isContentLoaded: boolean
}

class MainLayer extends React.Component<Props, State> {
    processingTime: number;
    results: ({ label: string, prob: number }[] | null) = null;

    constructor() {
        super();
        this.state = {
            isBusy: false,
            isContentLoaded: false
        };
    }

    /**
     * Event Handler
     */
    onRandomImageButtonClick() {
        this.loadRandomImage();
    }

    onUploadImageButtonClick() {
        this.uploadLocalImage();
    }

    onRunButtonClick() {
        this.run();
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

        let size = Math.min(canvas.clientWidth, canvas.clientHeight);
        canvas.style.width = size + 'px';
        canvas.style.height = size + 'px';
        WebDNN.Image.setImageArrayToCanvas(data, image.naturalWidth, image.naturalHeight, canvas);

        this.setState({ isContentLoaded: true });
    }

    async uploadLocalImage() {
        let canvas = dom.getFromRef<HTMLCanvasElement>(this, 'inputImageCanvas');
        let image = await WebDNN.Image.loadImageByDialog();
        let data = WebDNN.Image.getImageArrayFromDrawable(image);

        let size = Math.min(canvas.clientWidth, canvas.clientHeight);
        canvas.style.width = size + 'px';
        canvas.style.height = size + 'px';
        WebDNN.Image.setImageArrayToCanvas(data, image.naturalWidth, image.naturalHeight, canvas);

        this.setState({ isContentLoaded: true });
    }

    /**
     * Compute logic
     */
    async run() {
        let runner = this.props.runner;
        if (!runner) return;

        let inputImageCanvas = dom.getFromRef<HTMLCanvasElement>(this, 'inputImageCanvas');

        runner.getInputViews()[0].set(WebDNN.Image.getImageArrayFromCanvas(inputImageCanvas, {
            dstH: 224, dstW: 224, order: WebDNN.Image.Order.HWC
        }));
        if (runner.backendName !== 'webgpu') {
            this.setState({ isBusy: true });
        }

        let startTime = performance.now();
        await runner.run();
        let endTime = performance.now();
        this.processingTime = endTime - startTime;

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

    render() {
        return (
            <div className={classNames(style.mainLayer, this.props.className)}>
                <ProgressBar running={this.state.isBusy} />
                <NavbarLayer title="ResNet50 Image Classification" column>
                    <LayoutFrame flex>
                        <LayoutFrame fit block>
                            <LayoutFrame className={style.inputAndInformationContainer}>
                                <LayoutFrame fit block autoReverse>
                                    <LayoutFrame className={style.inputImageContainer} center>
                                        <canvas ref="inputImageCanvas" />
                                    </LayoutFrame>
                                    <LayoutFrame className={style.informationContainer}>
                                        <dl>
                                            <dt>Backend:</dt>
                                            <dd>{this.props.runner ? this.props.runner.backendName : '(unknown)'}</dd>
                                            <dt>Processing Time:</dt>
                                            <dd>{this.processingTime ?
                                                 this.processingTime.toFixed(1) + ' [ms]' :
                                                 'N/A'}</dd>
                                        </dl>
                                    </LayoutFrame>
                                </LayoutFrame>
                            </LayoutFrame>
                            <LayoutFrame className={style.resultContainer} column center>
                                {
                                    this.results ? (
                                        <table className={style.resultTable}>
                                            <tbody>
                                            {this.results.map((result, i) => (<tr key={i}>
                                                <th>
                                                    <LayoutFrame column>
                                                        <span style={{
                                                            opacity: result.prob / 2 + 0.5,
                                                        }}>{result.label}</span>
                                                        <span className={style.resultProb}
                                                              style={{
                                                                  opacity: result.prob / 2 + 0.5,
                                                              }}
                                                        >{(result.prob * 100).toFixed(1) + '%'}</span>
                                                    </LayoutFrame>
                                                </th>
                                                <td>
                                                    <div className={style.resultBar}
                                                         style={{
                                                             opacity: result.prob,
                                                             transform: `scaleX(${result.prob})`,
                                                             WebkitTransform: `scaleX(${result.prob})`,
                                                             MozTransform: `scaleX(${result.prob})`
                                                         }} />
                                                </td>
                                            </tr>))}
                                            </tbody>
                                        </table>
                                    ) : (
                                        null
                                    )
                                }
                            </LayoutFrame>
                        </LayoutFrame>
                    </LayoutFrame>
                    <LayoutFrame className={style.panel} row>
                        <Button className={style.panelButton}
                                onClick={ev => this.onRandomImageButtonClick()}
                                disabled={this.state.isBusy}>
                            <RandomIcon />
                            <span>Random</span>
                        </Button>
                        <Button className={style.panelButton}
                                onClick={ev => this.onUploadImageButtonClick()}
                                disabled={this.state.isBusy}>
                            <UploadIcon />
                            <span>Upload</span>
                        </Button>
                        <Button className={style.panelButton}
                                primary
                                onClick={ev => this.onRunButtonClick()}
                                disabled={this.state.isBusy || !this.state.isContentLoaded}>
                            <RunIcon />
                            <span>Run</span>
                        </Button>
                    </LayoutFrame>
                </NavbarLayer>
            </div>
        );
    }
}

export default MainLayer;