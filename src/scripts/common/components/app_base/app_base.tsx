import * as React from "react";
import * as WebDNN from "webdnn";
import InitializeLayer from "../../../common/components/initialize_layer/itnitialize_layer";

export interface State {
    runner: WebDNN.DescriptorRunner | null,
    loadingMessage: string,
    loadingProgressRate: number
}

export abstract class AppBase extends React.Component<React.HTMLAttributes<HTMLDivElement>, State> {
    constructor() {
        super();
        this.state = {
            runner: null,
            loadingMessage: '',
            loadingProgressRate: 0
        };
        this.initAsync();
    }

    abstract async initAsync(): Promise<void>;

    abstract renderMainLayer(): JSX.Element;

    render(): JSX.Element {
        if (this.state.runner) {
            return this.renderMainLayer();
        } else {
            return <InitializeLayer message={ this.state.loadingMessage }
                                    rate={ this.state.loadingProgressRate }
            />;
        }
    }
}
