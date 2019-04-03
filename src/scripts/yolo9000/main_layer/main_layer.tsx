import * as classNames from "classnames";
import * as React from "react";
import * as WebDNN from "webdnn";
import "../../../stylus/bootstrap.scss";
import { AppShell } from "../../common/components/app_shell/app_shell";
import { LayoutFrame } from "../../common/components/layout/layout";
import dom from "../../common/dom";
import WebCam from "../../common/webcam";
import LABELS from "./labels";
import * as style from "./main_layer.scss";
import TREE from "./tree";

/**
 * Hyper Parameters
 */
const NUM_CLASS = 9418;

// See /yolo-9000/darknet/cfg/yolo9000.cfg#192
const ANCHORS = [[0.77871, 1.14074], [3.00525, 4.31277], [9.22725, 9.61974]];

// @See /yolo-9000/darknet/src/detector.c#L503
const DETECTION_THRESHOLD = 0.1;
const DETECTION_HIERARCHY_THRESHOLD = 0.7;

// @See /yolo-9000/darknet/src/detector.c#L458
const IOU_THRESHOLD = 0.4;

/**
 * Bounding Box
 */

interface Box {
    x0: number
    y0: number
    x1: number
    y1: number
    conf: number
    classId: number
    categoryId: number
    className: string
    probability: number
}

function intersection(b1: Box, b2: Box) {
    return Math.max(0, Math.min(b1.x1, b2.x1) - Math.max(b1.x0, b2.x0)) *
        Math.max(0, Math.min(b1.y1, b2.y1) - Math.max(b1.y0, b2.y0));
}

function union(b1: Box, b2: Box) {
    return (b1.x1 - b1.x0) * (b1.y1 - b1.y0) + (b2.x1 - b2.x0) * (b2.y1 - b2.y0) - intersection(b1, b2);
}

function iou(b1: Box, b2: Box) {
    return intersection(b1, b2) / union(b1, b2);
}

function nonMaximumSuppression(boxes: Box[]) {
    let result: Box[] = [];

    boxes = boxes.sort((b1, b2) => b1.probability < b2.probability ? -1 : b1.probability > b2.probability ? +1 : 0);

    for (let i = 0; i < boxes.length; i++) {
        let flag = true;
        for (let j = i + 1; j < boxes.length; j++) {
            if (iou(boxes[i], boxes[j]) > IOU_THRESHOLD) {
                flag = false;
                break;
            }
        }
        if (flag) result.push(boxes[i]);
    }

    return result;
}

/**
 * Hierarchical Label
 */

let GROUP_SIZES: number[] = [];
let GROUP_OFFSET: number[] = [0];
let CHILDREN_GROUP_ID: number[] = [];

function buildTree() {
    let last_parent = -1;
    let size = 0;
    let offset = 0;
    for (let i = 0; i < NUM_CLASS; i++) {
        if (TREE[i] !== last_parent) {
            GROUP_SIZES.push(size);
            GROUP_OFFSET.push(offset);
            CHILDREN_GROUP_ID[TREE[i]] = GROUP_SIZES.length;
            size = 0;
        }
        size++;
        offset++;
        last_parent = TREE[i];
    }
}

/**
 * Main
 */

declare function require(path: string): any;

const Colors = ['#f00', '#0f0', '#88f', '#ff0', '#f0f', '#0ff', '#f80', '#80f', '#f08', '#08f', '#080'];
const RunIcon = require('./ic_play_arrow_black_24px.svg');
const VideoIcon = require('./ic_videocam_black_24px.svg');
const PauseIcon = require('./ic_pause_black_24px.svg');

interface Props extends React.HTMLAttributes<HTMLDivElement> {
    runner: WebDNN.DescriptorRunner;
}

interface State {
    isBusy: boolean
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
            isWebCamReady: false,
            isContentLoaded: false
        };
    }

    componentDidMount() {
        this.initializeAsync();
    }

    async initializeAsync() {
        let xyOffset = [];
        for (let i = 0; i < 13; i++) {
            xyOffset[i] = i;
        }
        this.props.runner.getInputViews()[1].set(xyOffset);
        this.props.runner.getInputViews()[2].set(xyOffset);
        this.props.runner.getInputViews()[3].set(ANCHORS.map(anchor => anchor[0]));
        this.props.runner.getInputViews()[4].set(ANCHORS.map(anchor => anchor[1]));

        buildTree();
    }

    /**
     * Event Handler
     */

    async onVideoButtonClick() {
        await this.initializeWebCam();
    }

    async onRunButtonClick() {
        await this.run();
    }

    onToggleButtonClick() {
        if (this.state.isBusy) {
            this.setState({
                isBusy: false
            });
        } else {
            this.setState({
                isBusy: true
            });
            requestAnimationFrame(async () => await this.run());
        }
    }

    /**
     * WebCam
     */

    async initializeWebCam(forceReInitialize: boolean = false) {
        if (!forceReInitialize && this.state.isWebCamReady) return;

        let video = dom.getFromRef<HTMLVideoElement>(this, 'input');
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

    async playVideo() {
        let $input = dom.getFromRef<HTMLVideoElement>(this, 'input');
        let $output = dom.getFromRef<HTMLCanvasElement>(this, 'output');

        try {
            await $input.play();
            $output.width = $input.videoWidth;
            $output.height = $input.videoHeight;
            this.setState({ isContentLoaded: !$input.paused });
        } catch (err) {
            this.setState({ isContentLoaded: false });
        }
    }

    finalizeWebCam() {
        let video = dom.getFromRef<HTMLVideoElement>(this, 'input');

        if (video.srcObject) {
            for (let stream of (video.srcObject as MediaStream).getTracks()) {
                stream.stop();
            }
        }

        this.setState({ isWebCamReady: false, isContentLoaded: false });
    }

    /**
     * Compute logic
     */
    async run() {
        if (!this.state.isBusy) return;
        let runner = this.props.runner;

        let $input = dom.getFromRef<HTMLVideoElement>(this, 'input');
        let $output = dom.getFromRef<HTMLCanvasElement>(this, 'output');

        runner.getInputViews()[0].set(WebDNN.Image.getImageArrayFromDrawable($input, {
            dstW: 416, dstH: 416,
            order: WebDNN.Image.Order.CHW,
            color: WebDNN.Image.Color.RGB,
            scale: [255, 255, 255]
        }));

        await runner.run();

        let boxes: Box[] = [];
        let x = runner.getOutputViews()[0].toActual();
        let y = runner.getOutputViews()[1].toActual();
        let w = runner.getOutputViews()[2].toActual();
        let h = runner.getOutputViews()[3].toActual();
        let conf = runner.getOutputViews()[4].toActual();
        let prob = runner.getOutputViews()[5].toActual();

        for (let i = 0; i < 3 * 13 * 13; i++) {
            if (conf[i] < DETECTION_THRESHOLD) continue;

            let offset = i * NUM_CLASS;
            for (let j = 0; j < NUM_CLASS; j++) {
                if (TREE[j] >= 0) prob[i * NUM_CLASS + j] *= prob[offset + TREE[j]];
            }

            let accumulatedProb = 1;
            let groupIndex = 0;
            let maxVal = 0;
            let maxIndex = 0;
            let categoryId = 0;
            let depth = 0;

            while (true) {
                maxVal = 0;
                maxIndex = 0;

                for (let j = 0; j < GROUP_SIZES[groupIndex]; j++) {
                    let index = j + GROUP_OFFSET[groupIndex];
                    let val = prob[offset + index];
                    if (val > maxVal) {
                        maxVal = val;
                        maxIndex = index;
                    }
                }

                accumulatedProb *= maxVal;
                if (accumulatedProb < DETECTION_HIERARCHY_THRESHOLD) break;

                groupIndex = CHILDREN_GROUP_ID[maxIndex];
                if (!groupIndex) break;

                depth++;
                if (depth < 3) categoryId = groupIndex;
            }

            boxes.push({
                x0: Math.round(Math.min(1, Math.max(0, x[i] - w[i] / 2)) * $input.videoWidth),
                y0: Math.round(Math.min(1, Math.max(0, y[i] - h[i] / 2)) * $input.videoHeight),
                x1: Math.round(Math.min(1, Math.max(0, x[i] + w[i] / 2)) * $input.videoWidth),
                y1: Math.round(Math.min(1, Math.max(0, y[i] + h[i] / 2)) * $input.videoHeight),
                conf: conf[i],
                classId: maxIndex,
                categoryId: categoryId,
                className: LABELS[maxIndex],
                probability: maxVal
            });
        }

        boxes = nonMaximumSuppression(boxes);

        let context = $output.getContext('2d')!;
        context.drawImage($input, 0, 0);
        context.font = '16px "sans-serif"';
        for (let box of boxes) {
            let color = Colors[box.categoryId % Colors.length];

            context.strokeStyle = color;
            context.lineWidth = 3;
            context.strokeRect(box.x0, box.y0, box.x1 - box.x0, box.y1 - box.y0);

            context.fillStyle = color;
            let w = context.measureText(box.className).width;
            context.fillRect(box.x0, box.y0 - 20, w + 8, 20);
            context.strokeRect(box.x0, box.y0 - 20, w + 8, 20);

            context.fillStyle = '#000';
            context.fillText(box.className, box.x0 + 4, box.y0 - 4);
        }

        requestAnimationFrame(() => this.run());
    }

    render() {
        let runButton = this.state.isBusy ?
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
                        });

        return (
            <div className={ classNames(style.mainLayer, this.props.className) }>
                <AppShell title="YOLO9000 Object Detection"
                          subTitle={ `backend: ${this.props.runner.backendName}` }
                          bottomBar={ [{
                              onClick: ev => this.onVideoButtonClick(),
                              disabled: this.state.isBusy,
                              icon: <VideoIcon />,
                              label: 'Video'
                          }, runButton] }>
                    <LayoutFrame fit block>
                        <video className={ style.fit } ref="input" />
                        <canvas className={ style.fit } ref="output" />
                    </LayoutFrame>
                </AppShell>
            </div>
        );
    }
}

export default MainLayer;