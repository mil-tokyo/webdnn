import * as React from "react";
import * as ReactDOM from "react-dom";
import * as WebDNN from "webdnn";
import { AppBase } from "../common/components/app_base/app_base";
import MainLayer from "./main_layer/main_layer";

class App extends AppBase {
    async initAsync() {
        let runner: WebDNN.DescriptorRunner;
        try {
            runner = await WebDNN.load("./resnet", {
                progressCallback: (loaded: number, total: number) => {
                    this.setState({
                        loadingProgressRate: loaded / total
                    });
                },
                transformUrlDelegate: (url: string) => {
                    let ma = url.match(/([^/]+)(?:\?.*)?$/);
                    if (ma) {
                        url = `https://mil-tokyo.github.io/webdnn-data/models/resnet/${ma[1]}`;
                    }

                    return url;
                },
                backendOrder: ['webgpu', 'webgl', 'webassembly', 'fallback']
            });
            // For DEBUG
            // await new Promise(r => requestAnimationFrame(r));
            // let runner = {backendName: 'webgpu'} as WebDNN.DescriptorRunner;
            this.setState({
                runner: runner
            });
        } catch (e) {
            console.error(e);
            this.setState({
                loadingMessage: 'Sorry, this browser is not supported yet.'
            });
        }
    }

    renderMainLayer() {
        return <MainLayer runner={ this.state.runner! } />;
    }
}

document.addEventListener('DOMContentLoaded', () => ReactDOM.render(<App />, document.getElementById('root')));

document.title = 'ResNet50 Image Classification - MIL WebDNN';