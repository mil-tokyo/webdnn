import * as React from "react";
import * as ReactDOM from "react-dom";
import NeuralStyleTransferApp from "./components/neural_style_transfer_app/neural_style_transfer_app";

document.addEventListener('DOMContentLoaded', () => ReactDOM.render(
    <NeuralStyleTransferApp />, document.getElementById('root')));
