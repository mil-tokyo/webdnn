/// <reference path="../../libs/webdnn.d.ts" />

import * as React from "react";
import * as ReactDOM from "react-dom";
import App from "./containers/app/app";

window.onload = () => {
    ReactDOM.render(<App />, document.getElementById('root'));
};
