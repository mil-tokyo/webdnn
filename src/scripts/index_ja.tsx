import * as React from "react";
import * as ReactDOM from "react-dom";
import TopPageJA from "./index/containers/toppage/toppage_ja";

declare function require(path: string): any;

window.onload =async () => {
    // let IS_ES2017 = true;
    // try {
    //     eval('(() => { async function test(){return Promise.resolve()} })();');
    // } catch (e) {
    //     IS_ES2017 = false;
    // }
    //
    // let iframes = document.querySelectorAll('iframe');
    // for (let i = 0; i < iframes.length; i++) {
    //     let iframe = iframes[i];
    //     let baseUrl = iframe.dataset['src'];
    //     if (!baseUrl) throw Error('baseUrl is not found');
    //     iframe.src = IS_ES2017 ? baseUrl : baseUrl.replace('.html', '.es5.html');
    // }

    if ('serviceWorker' in navigator) {
        let registration = await navigator.serviceWorker.register(require('file-loader!../static/sw.js'));
        await registration.unregister();
    }
};

document.addEventListener('DOMContentLoaded', () => ReactDOM.render(<TopPageJA />, document.getElementById('root')));

document.title = 'MIL WebDNN';