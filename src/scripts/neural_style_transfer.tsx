import * as React from "react";
import * as ReactDOM from "react-dom";
import App from "./neural_style_transfer/containers/app/app";

document.addEventListener('DOMContentLoaded', () => ReactDOM.render(<App />, document.getElementById('root')));

document.title = 'Neural Style Transfer - MIL WebDNN';