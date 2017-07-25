import * as React from "react";
import { Button } from "../../../components/button/button";
import { ControlBar } from "../../../components/control_bar/control_bar";
import { Header } from "../../../components/header/header";
import { ProgressBar } from "../../../components/progress_bar/progress_bar";
import TIL from "../../../common/til";
import { ImageNetClassificationResult } from "../../components/imagenet_classification_result/imagenet_classification_result";
import "./main_container.scss";
import classNames = require("classnames");
import Labels from "../../../common/imagenet_labels";

export interface Props extends React.HTMLAttributes<HTMLElement> {
    onInitialized: () => any
}

export interface State {
    running: boolean
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
            running: false
        };

        this.initializeAsync()
            .then(() => {
                this.props.onInitialized();
            });
    }

    async onRandomImageButtonClick() {
        await this.fetchRandomImage();
        await this.run();
    }

    async onUploadImageButtonClick() {
        await this.uploadImage();
        await this.run();
    }

    private async initializeAsync() {
        this.runner = await WebDNN.load('./resnet50');
        this.inputView = this.runner.getInputViews()[0];
        this.outputView = this.runner.getOutputViews()[0];
    }

    private async run(): Promise<void> {
        let $inputCanvas = this.refs['inputCanvas'] as (HTMLCanvasElement | null);
        if (!$inputCanvas) throw Error('inputCanvas is not found');

        this.inputView.set(await TIL.loadFromCanvas($inputCanvas));

        this.setState({ running: true });
        await this.runner.run();
        this.setState({
            running: false
        });

        let output = Array.from(this.outputView.toActual())
        let argmaxIndex = WebDNN.Math.argmax(output, 10);
        for (let i = 0; i < 10; i++) {
            console.log(Labels[argmaxIndex[i]], (output[argmaxIndex[i]] * 100).toFixed(1) + '%');
        }
    }

    private setContentImage($img: HTMLImageElement) {
        let $inputCanvas = this.refs['inputCanvas'] as (HTMLCanvasElement | null);
        if (!$inputCanvas)  throw Error('inputCanvas is not found');
        $inputCanvas.style.width = '';
        $inputCanvas.style.height = '';

        let ctx = $inputCanvas.getContext('2d');
        if (!ctx) throw Error('Context initialization failed');

        const naturalWidth = 224;
        const naturalHeight = 224;
        let imageAspect = naturalHeight / naturalWidth;
        let canvasAspect = $inputCanvas.clientHeight / $inputCanvas.clientWidth;
        let width: number;
        let height: number;
        if (canvasAspect > imageAspect) {
            width = Math.min(naturalWidth, $inputCanvas.clientWidth);
            height = width * imageAspect;
        } else {
            height = Math.min(naturalHeight, $inputCanvas.clientHeight);
            width = height / imageAspect;
        }

        $inputCanvas.style.width = width + 'px';
        $inputCanvas.style.height = height + 'px';
        $inputCanvas.width = width;
        $inputCanvas.height = height;
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

    render() {
        return (
            <main className={classNames('MainContainer', this.props.className)}>
                <ProgressBar running={this.state.running}/>
                <Header title="Image Classification"/>
                <div className={classNames('MainContainer', this.props.className)}>
                    <div className="MainContainer-Images">
                        <div className="MainContainer-Input">
                            <header className="MainContainer-Header">
                                Content
                            </header>
                            <canvas className="MainContainer-InputCanvas" ref="inputCanvas"/>
                        </div>
                        <div className="MainContainer-Output">
                            <header className="MainContainer-Header">
                                Output
                                <ImageNetClassificationResult/>
                            </header>
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
                </ControlBar>
            </ main>);
    }
}