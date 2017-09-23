import * as React from "react";
import * as ReactDOM from "react-dom";
import { TopPage } from "./containers/toppage/toppage";

document.addEventListener('DOMContentLoaded', () => ReactDOM.render(<TopPage />, document.getElementById('root')));

document.title = 'MIL WebDNN';