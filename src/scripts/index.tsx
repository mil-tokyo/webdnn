// import "../common/analytics.js";
// window.onload = () => {
//     let IS_ES2017 = true;
//     try {
//         eval('(() => { async function test(){return Promise.resolve()} })();');
//     } catch (e) {
//         IS_ES2017 = false;
//     }
//
//     let iframes = document.querySelectorAll('iframe');
//     for (let i = 0; i < iframes.length; i++) {
//         let iframe = iframes[i];
//         let baseUrl = iframe.dataset['src'];
//         if (!baseUrl) throw Error('baseUrl is not found');
//         iframe.src = IS_ES2017 ? baseUrl : baseUrl.replace('.html', '.es5.html');
//     }
//
//     if ('serviceWorker' in navigator) navigator.serviceWorker.register('/webdnn/sw.js');
// };

import * as React from "react";
import * as ReactDOM from "react-dom";
import TopPage from "./components/toppage/toppage";

document.addEventListener('DOMContentLoaded', () => ReactDOM.render(<TopPage />, document.getElementById('root')));