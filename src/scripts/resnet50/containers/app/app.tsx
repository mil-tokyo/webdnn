import * as React from "react";
import * as WebDNN from "webdnn";
import InitializeLayer from "../../../common/components/initialize_layer/itnitialize_layer";
import StartLayer from "../../../common/components/start_layer/start_layer";
import MainLayer from "../../components/main_layer/main_layer";

enum Status {
    SLEEP,
    INITIALIZING,
    READY
}

interface State {
    runner: WebDNN.DescriptorRunner<WebDNN.GraphDescriptor> | null,
    loadingProgressRate: number,
    status: Status
}

const IS_MOBILE = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);

export default class App extends React.Component<React.HTMLAttributes<HTMLDivElement>, State> {
    constructor() {
        super();
        this.state = {
            runner: null,
            loadingProgressRate: 0,
            status: location.search == '?run=1' ? Status.INITIALIZING : Status.SLEEP
        };

        if (location.search == '?run=1') this.initAsync();
    }

    async initAsync() {
        let gl = document.createElement('canvas').getContext('webgl');
        let runner = await WebDNN.load("./resnet", {
            progressCallback: (loaded: number, total: number) => {
                this.setState({
                    loadingProgressRate: loaded / total
                });
            },
            transformUrlDelegate: (url: string) => {
                let ma = url.match(/([^/]+)(?:\?.*)?$/);
                return ma ? `https://mil-tokyo.github.io/webdnn-data/models/resnet/${ma[1]}?raw=true` : url;
            },
            backendOrder: (gl && gl.getParameter(gl.MAX_TEXTURE_SIZE) >= 16384) ?
                ['webgpu', 'webgl', 'webassembly', 'fallback'] :
                ['webgpu', 'webassembly', 'webgl', 'fallback']
        });

        const IS_WEBGPU_IMPLEMENTED = /iPhone OS 11_0/.test(navigator.userAgent) &&
            /Safari/.test(navigator.userAgent) &&
            !(/CriOS/.test(navigator.userAgent)) &&
            !(/FxiOS/.test(navigator.userAgent));

        if (IS_WEBGPU_IMPLEMENTED && runner.backendName !== 'webgpu') {
            //TODO
        }

        this.setState({
            runner: runner,
            status: Status.READY
        });
    }

    onStartButtonClick() {
        this.setState({
            status: Status.INITIALIZING
        });
        this.initAsync();
    }

    render() {
        switch (this.state.status) {
            case Status.SLEEP:
                return <StartLayer onStart={() => this.onStartButtonClick()} />;

            case Status.INITIALIZING:
                return <InitializeLayer rate={this.state.loadingProgressRate} />;

            case Status.READY:
                return <MainLayer runner={this.state.runner!} />;
        }
    }
}