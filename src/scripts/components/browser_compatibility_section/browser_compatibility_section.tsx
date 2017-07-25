import * as classNames from "classnames"
import * as React from "react"
import * as bootstrap from "../../common/bootstrap";
import TableWrapper from "../table_wrapper/table_wrapper";
import TopPageSection, { TopPageSectionSubTitle } from "../toppage_section/toppage_section";
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

class BrowserCompatibilitySection extends React.Component<React.HTMLAttributes<HTMLElement>, {}> {
    componentDidMount() {
        let availability: { [key: string]: boolean } = {
            'webgpu': ('WebGPUComputeCommandEncoder' in window),
            'webassembly': ('Worker' in window),
            'fallback': true
        };

        for (let backend of ['webgpu', 'webassembly', 'fallback']) {
            let node = (this.refs[backend] as (HTMLElement | null));
            if (!node) continue;

            node.classList.remove(style.checking);
            let statusNode = node.querySelector('span');

            if (availability[backend]) {
                node.classList.add(style.supported);
                node.classList.remove(style.unsupported);
                if (statusNode) statusNode.textContent = 'Supported';
            } else {
                node.classList.remove(style.supported);
                node.classList.add(style.unsupported);
                if (statusNode) statusNode.textContent = 'Not supported';
            }
        }
    }

    render() {
        return (<TopPageSection title="Browser Compatibility" id={AnchorID}>
            <div className={bootstrap.row}>
                <div className={bootstrap.col12}>
                    <p>
                        WebDNN supports 3 execution backend implementations:&nbsp;<b>WebGPU</b>, <b>WebAssembly</b>,
                        and&nbsp;<b>fallback pure javascript implementation</b>.
                        By using this 3 backend implementations, <b>WebDNN works all major browsers</b>.
                    </p>
                    <dl>
                        <dt>WebGPU backend</dt>
                        <dd>Compute on GPU by WebGPU API. This backend is fastest in 3 backends, but currently WebGPU
                            API is
                            supported only in Safari Technology Preview.
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
                                <td className={style.webassembly} rowSpan={2}>
                                    <span className={style.versionRange}>10 - 11</span>
                                    <span className={style.backend}>WebAssembly/asm.js</span>
                                </td>
                                <td className={style.webassembly} rowSpan={3}>
                                    <span className={style.versionRange}> - 15</span>
                                    <span className={style.backend}>WebAssembly/asm.js</span>
                                </td>
                                <td className={style.webgpu} rowSpan={1}>
                                    <span className={style.versionRange}>Technology Preview</span>
                                    <span className={style.backend}>WebGPU</span>
                                </td>
                                <td className={style.webassembly} rowSpan={3}>
                                    <span className={style.versionRange}> - 58</span>
                                    <span className={style.backend}>WebAssembly/asm.js</span>
                                </td>
                                <td className={style.webassembly} rowSpan={3}>
                                    <span className={style.versionRange}> - 53</span>
                                    <span className={style.backend}>WebAssembly/asm.js</span>
                                </td>
                            </tr>
                            <tr>
                                <td className={style.webassembly} rowSpan={2}>
                                    <span className={style.versionRange}> - 10.1</span>
                                    <span className={style.backend}>WebAssembly/asm.js</span>
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
                    <p id="mes-ts">
                        In Safari Technology Preview, WebGPU API is disabled as default. To enable the API,
                        see&nbsp;<i>"Develop"</i>&nbsp;>&nbsp;<i>"Experimental Features"</i>&nbsp;>&nbsp;
                        <i>"WebGPU"</i>&nbsp;in
                        menu bar.
                    </p>
                </div>
            </div>
        </TopPageSection>);
    }
}

export default BrowserCompatibilitySection;
