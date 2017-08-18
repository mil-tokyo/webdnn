import * as React from "react";
import * as ReactDOM from "react-dom";
import App from "./resnet50/containers/app/app";

document.addEventListener('DOMContentLoaded', () => ReactDOM.render(<App />, document.getElementById('root')));

document.title = 'ResNet50 - MIL WebDNN';