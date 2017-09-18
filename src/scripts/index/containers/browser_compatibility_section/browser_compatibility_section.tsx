import * as classNames from "classnames"
import * as React from "react"
import * as WebDNN from "webdnn";
import * as bootstrap from "../../../common/bootstrap";
import TableWrapper from "../../components/table_wrapper/table_wrapper";
import TopPageSection, { TopPageSectionSubTitle } from "../../components/toppage_section/toppage_section";
import * as style from "./browser_compatibility_section.scss";

export const AnchorID = "compatibility";

declare function require(path: string): any;

let svgIcons = {
    ie: require('./ie.svg'),
    edge: require('./edge.svg'),
    chrome: require('./chrome.svg'),
    safari: require('./safari.svg'),
    firefox: require('./firefox.svg')
};

class BrowserCompatibilitySection extends React.Component<React.HTMLAttributes<HTMLElement>, { flagWebGPUDisabled: boolean }> {
    constructor() {
        super();
        this.state = { flagWebGPUDisabled: false }
    }

    componentDidMount() {
        const IS_WEBGPU_IMPLEMENTED = /iPhone OS 11_0/.test(navigator.userAgent) &&
            /Safari/.test(navigator.userAgent) &&
            !(/CriOS/.test(navigator.userAgent)) &&
            !(/FxiOS/.test(navigator.userAgent));

        let availability = WebDNN.getBackendAvailability().status;

        for (let backend of ['webgpu', 'webgl', 'webassembly', 'fallback']) {
            let node = (this.refs[backend] as (HTMLElement | null));
            if (!node) continue;

            node.classList.remove(style.checking);
            let statusNode = node.querySelector('span');

            if (availability[backend as WebDNN.BackendName]) {
                node.classList.add(style.supported);
                node.classList.remove(style.unsupported);
                if (statusNode) statusNode.textContent = 'Supported';
            } else {
                if (backend === 'webgpu' && IS_WEBGPU_IMPLEMENTED) {
                    node.classList.remove(style.unsupported);
                    node.classList.add(style.disabled);
                    if (statusNode) statusNode.textContent = 'Disabled';
                    this.setState({
                        flagWebGPUDisabled: true
                    });

                } else {
                    node.classList.remove(style.supported);
                    node.classList.add(style.unsupported);
                    if (statusNode) statusNode.textContent = 'Not supported';
                }
            }
        }
    }

    render() {
        return (<TopPageSection title="Browser Compatibility" id={AnchorID}>
            <div className={bootstrap.row}>
                <div className={bootstrap.col12}>
                    <p>
                        WebDNN supports 4 execution backend implementations:&nbsp;<b>WebGPU</b>, <b>WebGL</b>,
                        <b>WebAssembly</b>, and&nbsp;<b>fallback pure javascript implementation</b>.
                        By using these backends, <b>WebDNN works all major browsers</b>.
                    </p>
                    <dl>
                        <dt>WebGPU backend</dt>
                        <dd>Compute on GPU by WebGPU API. This backend is fastest in 4 backends, but currently WebGPU
                            API is
                            supported only in Safari Technology Preview.
                        </dd>
                        <dt>WebGL backend</dt>
                        <dd>Compute on GPU by WebGL API. This backend is also faster than CPU-based backends, and WebGL
                            is supported by almost all browsers.
                        </dd>
                        <dt>WebAssembly backend</dt>
                        <dd>Compute on CPU by WebAssembly API. This backend is enough faster than GPU mode of
                            Keras.js&nbsp;<a className="ref" href="#ref1">[1]</a>. By using with asm.js, this backend
                            works most of all modern browsers.
                        </dd>
                        <dt>Fallback backend</dt>
                        <dd>Compute on CPU by ECMAScript3. This backend is only for backward compatibility, and not so
                            faster.
                        </dd>
                    </dl>
                </div>
                <div className={bootstrap.col12}>
                    <TopPageSectionSubTitle title="Browser Compatibility Table" />
                    <TableWrapper>
                        <table className={style.compatibilityTable}>
                            <tbody>
                            <tr>
                                <th>
                                    <svgIcons.ie />
                                    <span className={style.browser}>Internet Explorer</span>
                                </th>
                                <th>
                                    <svgIcons.edge />
                                    <span className={style.browser}>Edge</span>
                                </th>
                                <th>
                                    <svgIcons.safari />
                                    <span className={style.browser}>Safari</span>
                                </th>
                                <th>
                                    <svgIcons.chrome />
                                    <span className={style.browser}>Chrome</span>
                                </th>
                                <th>
                                    <svgIcons.firefox />
                                    <span className={style.browser}>FireFox</span>
                                </th>
                            </tr>
                            <tr>
                                <td className={style.webassembly} rowSpan={1}>
                                    <span className={style.versionRange}>11</span>
                                    <span className={style.backend}>WebGL, WebAssembly/asm.js</span>
                                </td>
                                <td className={style.webassembly} rowSpan={3}>
                                    <span className={style.versionRange}> - 15</span>
                                    <span className={style.backend}>WebGL, WebAssembly/asm.js</span>
                                </td>
                                <td className={style.webgpu} rowSpan={1}>
                                    <span className={style.versionRange}>11</span>
                                    <span className={style.backend}>WebGPU, WebAssembly/asm.js</span>
                                </td>
                                <td className={style.webassembly} rowSpan={3}>
                                    <span className={style.versionRange}> - 58</span>
                                    <span className={style.backend}>WebGL, WebAssembly/asm.js</span>
                                </td>
                                <td className={style.webassembly} rowSpan={3}>
                                    <span className={style.versionRange}> - 53</span>
                                    <span className={style.backend}>WebGL, WebAssembly/asm.js</span>
                                </td>
                            </tr>
                            <tr>
                                <td className={style.webassembly} rowSpan={1}>
                                    <span className={style.versionRange}>10</span>
                                    <span className={style.backend}>WebAssembly/asm.js</span>
                                </td>
                                <td className={style.webassembly} rowSpan={2}>
                                    <span className={style.versionRange}> - 10.1</span>
                                    <span className={style.backend}>WebGL, WebAssembly/asm.js</span>
                                </td>
                            </tr>
                            <tr>
                                <td className={style.fallback} rowSpan={1}>
                                    <span className={style.versionRange}> - 9</span>
                                    <span className={style.backend}>Fallback</span>
                                </td>
                            </tr>
                            </tbody>
                        </table>
                    </TableWrapper>
                </div>
            </div>
            <hr />
            <div className={bootstrap.row}>
                <div className={bootstrap.col12}>
                    <TopPageSectionSubTitle title="This Browser" />
                    <TableWrapper>
                        <table className={style.thisBrowserTable}>
                            <tbody>
                            <tr>
                                <th>
                                    <span className={style.backend}>WebGPU</span>
                                </th>
                                <th>
                                    <span className={style.backend}>WebGL</span>
                                </th>
                                <th>
                                    <span className={style.backend}>WebAssembly/asm.js</span>
                                </th>
                                <th>
                                    <span className={style.backend}>Fallback</span>
                                </th>
                            </tr>
                            <tr>
                                <td className={classNames(style.webgpu, style.unsupported)} ref="webgpu">
                                    <span>Not supported</span>
                                </td>
                                <td className={classNames(style.webassembly, style.unsupported)} ref="webgl">
                                    <span>Not supported</span>
                                </td>
                                <td className={classNames(style.webassembly, style.unsupported)} ref="webassembly">
                                    <span>Not supported</span>
                                </td>
                                <td className={classNames(style.fallback, style.unsupported)} ref="fallback">
                                    <span>Not supported</span>
                                </td>
                            </tr>
                            </tbody>
                        </table>
                    </TableWrapper>
                    <p style={{ display: this.state.flagWebGPUDisabled ? '' : 'none' }} className={style.webgpuTips}>
                        This browser supports WebGPU, but currently it's disabled. WebGPU accelerates WebDNN
                        considerably. To enable WebGPU, see
                        <a href={/iPhone/.test(navigator.userAgent) ?
                                 "https://mil-tokyo.github.io/webdnn/docs/tips/enable_webgpu_ios.html" :
                                 "https://mil-tokyo.github.io/webdnn/docs/tips/enable_webgpu_macos.html"}>
                            this document
                        </a>.
                    </p>
                    <p style={{ display: this.state.flagWebGPUDisabled ? 'none' : '' }} className={style.webgpuTips}>
                        In <b>Safari 11 on macOS High Sierra</b> and <b>Safari Technology Preview</b>, WebGPU API is available (some hardware cannot be supported yet).
                        To enable WebGPU, see <a href={/iPhone/.test(navigator.userAgent) ?
                                 "https://mil-tokyo.github.io/webdnn/docs/tips/enable_webgpu_ios.html" :
                                 "https://mil-tokyo.github.io/webdnn/docs/tips/enable_webgpu_macos.html"}>
                            this document
                        </a>.
                    </p>
                </div>
            </div>
        </TopPageSection>);
    }
}

export default BrowserCompatibilitySection;
