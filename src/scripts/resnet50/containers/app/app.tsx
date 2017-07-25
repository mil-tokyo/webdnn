import * as React from "react";
import MainContainer from "../main_container/main_container";
import "./app.scss";
import classNames = require("classnames");

export interface Props extends React.HTMLAttributes<HTMLDivElement> {
}

export interface State {
    isInitialized: boolean
}

export default class App extends React.Component<Props, State> {
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
            <div className={classNames('App', this.props.className)}>
                { this.state.isInitialized ? null : (
                    <div className="App-SplashScreen">Initializing...</div>
                ) }
                <MainContainer onInitialized={() => this.onMainContainerInitialized()}/>
            </ div>
        );
    }
}