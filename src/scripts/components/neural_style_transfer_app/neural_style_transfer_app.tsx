import * as classNames from "classnames";
import * as React from "react";
import MainContainer from "../main_container/main_container";
import * as style from "./neural_style_transfer_app.scss";

interface State {
    isInitialized: boolean
}

export default class NeuralStyleTransferApp extends React.Component<React.HTMLAttributes<HTMLDivElement>, State> {
    constructor() {
        super();
        this.state = {
            isInitialized: false
        };
    }

    onMainContainerInitialized() {
        this.setState({
            isInitialized: true
        });
    }

    render() {
        return (
            <div className={classNames(style.neuralStyleTransferApp, this.props.className)}>
                {this.state.isInitialized ? null : (
                    <div className={style.neuralStyleTransferAppSplashScreen}>Initializing...</div>
                )}
                <MainContainer onInitialized={() => this.onMainContainerInitialized()} />
            </ div>
        );
    }
}