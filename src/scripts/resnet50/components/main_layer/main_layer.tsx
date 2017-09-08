import * as classNames from "classnames";
import * as React from "react";
import "../../../../stylus/bootstrap.scss";
import Button from "../../../common/components/button/button";
import { LayoutFrame } from "../../../common/components/layout/layout";
import NavbarLayer from "../../../common/components/navbar_layer/navbar_layer";
import ProgressBar from "../../../common/components/progress_bar/progress_bar";
import dom from "../../../common/dom";
import Labels from "../../../common/imagenet_labels";
import { loadImageByDialog, loadImageByUrl } from "../../../common/til/load_image";
import { loadImageDataFromCanvas } from "../../../common/til/load_image_data";
import * as style from "./main_layer.scss";
import * as WebDNN from "webdnn";

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

function computeContainSize(originalWidth: number, originalHeight: number, referenceWidth: number, referenceHeight: number) {
    let computeWidth = referenceWidth;
    let computeHeight = originalHeight * (computeWidth / originalWidth);

    if (computeHeight > referenceHeight) {
        computeHeight = referenceHeight;
        computeWidth = originalWidth * (computeHeight / originalHeight)
    }

    return {
        width: computeWidth,
        height: computeHeight
    };
}

function clamp(x: number, min: number, max: number) { return x < min ? min : x > max ? max : x };

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

/**
 * Draw image data with adjusting whose size to be contained in specified canvas.
 * @param {HTMLCanvasElement} canvas
 * @param {Uint8Array} imageData whose contains only RGB data, not contains alpha data
 * @param {number} naturalWidth
 * @param {number} naturalHeight
 * @param imageWidth
 * @param imageHeight
 */
function drawAdjustedImageDataToCanvas(canvas: HTMLCanvasElement, data: Uint8Array | Float32Array,
                                       naturalWidth: number, naturalHeight: number,
                                       imageWidth: number = naturalWidth, imageHeight: number = naturalHeight) {
    let context = canvas.getContext('2d');
    if (!context) throw Error('context initialization failed');

    let { width: clientWidth, height: clientHeight } = computeContainSize(
        naturalWidth, naturalHeight,
        canvas.parentElement!.clientWidth, canvas.parentElement!.clientHeight);

    canvas.style.width = clientWidth + 'px';
    canvas.style.height = clientHeight + 'px';
    canvas.width = naturalWidth;
    canvas.height = naturalHeight;

    let imageData = new ImageData(naturalWidth, naturalHeight);

    for (let y = 0; y < naturalHeight; y++) {
        for (let x = 0; x < naturalWidth; x++) {
            imageData.data[(y * naturalWidth + x) * 4 + 0] = clamp(data[(y * naturalWidth + x) * 3 + 0], 0, 255);
            imageData.data[(y * naturalWidth + x) * 4 + 1] = clamp(data[(y * naturalWidth + x) * 3 + 1], 0, 255);
            imageData.data[(y * naturalWidth + x) * 4 + 2] = clamp(data[(y * naturalWidth + x) * 3 + 2], 0, 255);
            imageData.data[(y * naturalWidth + x) * 4 + 3] = 255;
        }
    }

    context.clearRect(0, 0, canvas.width, canvas.height);
    context.putImageData(imageData, 0, 0);

    let image = new Image();

    return new Promise(resolve => {
        image.onload = () => {
            drawAdjustedImageToCanvas(canvas, image, imageWidth, imageHeight);
            resolve();
        };

        image.src = canvas.toDataURL();
    });
}

/**
 * Draw image with adjusting whose size to be contained in specified canvas.
 * @param {HTMLCanvasElement} canvas
 * @param {HTMLImageElement} image
 * @param {number} imageWidth
 * @param {number} imageHeight
 */
function drawAdjustedImageToCanvas(canvas: HTMLCanvasElement, image: HTMLImageElement,
                                   imageWidth: number = image.naturalWidth,
                                   imageHeight: number = image.naturalHeight) {
    let context = canvas.getContext('2d');
    if (!context) throw Error('context initialization failed');

    let { width: clientWidth, height: clientHeight } = computeContainSize(
        imageWidth, imageHeight,
        canvas.parentElement!.clientWidth, canvas.parentElement!.clientHeight);

    canvas.style.width = clientWidth + 'px';
    canvas.style.height = clientHeight + 'px';
    canvas.width = imageWidth;
    canvas.height = imageHeight;

    context.clearRect(0, 0, canvas.width, canvas.height);
    context.drawImage(image, 0, 0, imageWidth, imageHeight);
}

interface Props extends React.HTMLAttributes<HTMLDivElement> {
    runner: WebDNN.DescriptorRunner<WebDNN.GraphDescriptor>;
}

interface State {
    isBusy: boolean,
    isContentLoaded: boolean
}

class MainLayer extends React.Component<Props, State> {
    processingTimes: number[] = [];
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

        await drawAdjustedImageToCanvas(
            dom.getFromRef<HTMLCanvasElement>(this, 'inputImageCanvas'),
            await loadImageByUrl(IMAGE_PATH_LIST[random_image_index]),
            224, 224
        );

        this.setState({ isContentLoaded: true });
    }

    async uploadLocalImage() {
        await drawAdjustedImageToCanvas(
            dom.getFromRef<HTMLCanvasElement>(this, 'inputImageCanvas'),
            await loadImageByDialog(),
            224, 224
        );

        this.setState({ isContentLoaded: true });
    }

    /**
     * Compute logic
     */
    async run() {
        let runner = this.props.runner;
        if (!runner) return;

        let inputImageCanvas = dom.getFromRef<HTMLCanvasElement>(this, 'inputImageCanvas');

        runner.getInputViews()[0].set(loadImageDataFromCanvas(inputImageCanvas));
        if (runner.backendName !== 'webgpu') {
            this.setState({ isBusy: true });
        }

        let startTime = performance.now();
        await runner.run();
        let endTime = performance.now();
        this.processingTimes.push(endTime - startTime);
        console.log(endTime - startTime);

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
                                            <dt>Average Processing Time:</dt>
                                            <dd>{this.processingTimes.length > 0 ?
                                                 `${(this.processingTimes.reduce((v, s) => v + s, 0) / this.processingTimes.length).toFixed(1)}[ms/image]` :
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