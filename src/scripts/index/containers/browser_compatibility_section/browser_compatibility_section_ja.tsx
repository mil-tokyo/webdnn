import * as classNames from "classnames"
import * as React from "react"
import * as WebDNN from "webdnn";
import * as bootstrap from "../../../common/bootstrap";
import { TableWrapper } from "../../components/table_wrapper/table_wrapper";
import { TopPageSection, TopPageSectionSubTitle } from "../../components/toppage_section/toppage_section";
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

export default class BrowserCompatibilitySectionJA extends React.Component<React.HTMLAttributes<HTMLElement>, { flagWebGPUDisabled: boolean }> {
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
                if (statusNode) statusNode.textContent = '利用可能';
            } else {
                if (backend === 'webgpu' && IS_WEBGPU_IMPLEMENTED) {
                    node.classList.remove(style.unsupported);
                    node.classList.add(style.disabled);
                    if (statusNode) statusNode.textContent = '無効化されています';
                    this.setState({
                        flagWebGPUDisabled: true
                    });

                } else {
                    node.classList.remove(style.supported);
                    node.classList.add(style.unsupported);
                    if (statusNode) statusNode.textContent = '利用できません';
                }
            }
        }
    }

    render() {
        return (<TopPageSection title="Browser Compatibility" id={ AnchorID }>
            <div className={ bootstrap.row }>
                <div className={ bootstrap.col12 }>
                    <p>
                        WebDNNは4種類の実行環境(バックエンド)を実装しています。
                        これらのバックエンドを組み合わせて用いることで、WebDNNは主要ブラウザのすべてで動作します。
                    </p>
                    <dl>
                        <dt>WebGPU backend</dt>
                        <dd>すべての演算をGPUで行います。GPU APIにはWebGPUを使用しており、4種類の中で最も高速に動作します。ただし、
                            現在WebGPUをサポートしているブラウザはSafari Technology Preview版しかありません。
                        </dd>
                        <dt>WebGL backend</dt>
                        <dd>すべての演算をGPUで行います。GPU APIにはWebGLを使用しており、WebGPUバックエンドと同様CPUベースのバックエンドより高速に動作します。
                            また、WebGLはモダンなブラウザのほぼ全てでサポートされています。
                        </dd>
                        <dt>WebAssembly backend</dt>
                        <dd>すべての演算をCPUで行います。実装にはWebAssemblyを使用し、オーバーヘッドの少ない処理を可能にしています。
                            このバックエンドはKeras.js<a className="ref" href="#ref1">[1]</a>の
                            GPUモードと同等の速度で動作します。また、asm.jsと組み合わせることで、ほぼすべてのモダンなウェブブラウザで動作することができます。
                        </dd>
                        <dt>Fallback backend</dt>
                        <dd>すべての演算をCPUで行います。実装はECMAScript3に準拠しており、今日の主要なウェブブラウザのほぼすべてで動作します。
                            ただし、このバックエンドは後方互換性のためだけに存在しており、速度面の考慮はされていません。
                        </dd>
                    </dl>
                </div>
                <div className={ bootstrap.col12 }>
                    <TopPageSectionSubTitle title="各ブラウザで利用可能なバックエンド一覧" />
                    <TableWrapper>
                        <table className={ style.compatibilityTable }>
                            <tbody>
                            <tr>
                                <th>
                                    <svgIcons.ie />
                                    <span className={ style.browser }>Internet Explorer</span>
                                </th>
                                <th>
                                    <svgIcons.edge />
                                    <span className={ style.browser }>Edge</span>
                                </th>
                                <th>
                                    <svgIcons.safari />
                                    <span className={ style.browser }>Safari</span>
                                </th>
                                <th>
                                    <svgIcons.chrome />
                                    <span className={ style.browser }>Chrome</span>
                                </th>
                                <th>
                                    <svgIcons.firefox />
                                    <span className={ style.browser }>FireFox</span>
                                </th>
                            </tr>
                            <tr>
                                <td className={ style.webassembly } rowSpan={ 1 }>
                                    <span className={ style.versionRange }>11</span>
                                    <span className={ style.backend }>WebGL, WebAssembly/asm.js</span>
                                </td>
                                <td className={ style.webassembly } rowSpan={ 3 }>
                                    <span className={ style.versionRange }> - 15</span>
                                    <span className={ style.backend }>WebGL, WebAssembly/asm.js</span>
                                </td>
                                <td className={ style.webgpu } rowSpan={ 1 }>
                                    <span className={ style.versionRange }>11</span>
                                    <span className={ style.backend }>WebGPU, WebAssembly/asm.js</span>
                                </td>
                                <td className={ style.webassembly } rowSpan={ 3 }>
                                    <span className={ style.versionRange }> - 58</span>
                                    <span className={ style.backend }>WebGL, WebAssembly/asm.js</span>
                                </td>
                                <td className={ style.webassembly } rowSpan={ 3 }>
                                    <span className={ style.versionRange }> - 53</span>
                                    <span className={ style.backend }>WebGL, WebAssembly/asm.js</span>
                                </td>
                            </tr>
                            <tr>
                                <td className={ style.webassembly } rowSpan={ 1 }>
                                    <span className={ style.versionRange }>10</span>
                                    <span className={ style.backend }>WebAssembly/asm.js</span>
                                </td>
                                <td className={ style.webassembly } rowSpan={ 2 }>
                                    <span className={ style.versionRange }> - 10.1</span>
                                    <span className={ style.backend }>WebAssembly/asm.js</span>
                                </td>
                            </tr>
                            <tr>
                                <td className={ style.fallback } rowSpan={ 1 }>
                                    <span className={ style.versionRange }> - 9</span>
                                    <span className={ style.backend }>Fallback</span>
                                </td>
                            </tr>
                            </tbody>
                        </table>
                    </TableWrapper>
                </div>
            </div>
            <hr />
            <div className={ bootstrap.row }>
                <div className={ bootstrap.col12 }>
                    <TopPageSectionSubTitle title="このブラウザで利用可能なバックエンド" />
                    <TableWrapper>
                        <table className={ style.thisBrowserTable }>
                            <tbody>
                            <tr>
                                <th>
                                    <span className={ style.backend }>WebGPU</span>
                                </th>
                                <th>
                                    <span className={ style.backend }>WebGL</span>
                                </th>
                                <th>
                                    <span className={ style.backend }>WebAssembly/asm.js</span>
                                </th>
                                <th>
                                    <span className={ style.backend }>Fallback</span>
                                </th>
                            </tr>
                            <tr>
                                <td className={ classNames(style.webgpu, style.unsupported) } ref="webgpu">
                                    <span>利用できません</span>
                                </td>
                                <td className={ classNames(style.webassembly, style.unsupported) } ref="webgl">
                                    <span>利用できません</span>
                                </td>
                                <td className={ classNames(style.webassembly, style.unsupported) } ref="webassembly">
                                    <span>利用できません</span>
                                </td>
                                <td className={ classNames(style.fallback, style.unsupported) } ref="fallback">
                                    <span>利用できません</span>
                                </td>
                            </tr>
                            </tbody>
                        </table>
                    </TableWrapper>
                    <p style={ { display: this.state.flagWebGPUDisabled ? '' : 'none' } }
                       className={ style.webgpuTips }>
                        このブラウザはWebGPUが無効化されています。WebGPUを有効化するとWebDNNの実行速度が劇的に高速化されます。
                        WebGPUを有効化する方法は、
                        <a href={ /iPhone/.test(navigator.userAgent) ?
                                  "https://mil-tokyo.github.io/webdnn/docs/tips/enable_webgpu_ios_ja.html" :
                                  "https://mil-tokyo.github.io/webdnn/docs/tips/enable_webgpu_macos_ja.html" }>
                            このドキュメント
                        </a>を確認してください。
                    </p>
                    <p style={ { display: this.state.flagWebGPUDisabled ? 'none' : '' } }
                       className={ style.webgpuTips }>
                        <b>macOS High Sierra</b>, <b>iOS 11</b>, および <b>Safari Technology Preview</b>ではWebGPU
                                                APIを利用した高速処理が可能です（搭載ハードウェアにより実行できない場合があります）。
                                                WebGPUを有効化する方法は、
                        <a href={ /iPhone/.test(navigator.userAgent) ?
                                  "https://mil-tokyo.github.io/webdnn/docs/tips/enable_webgpu_ios_ja.html" :
                                  "https://mil-tokyo.github.io/webdnn/docs/tips/enable_webgpu_macos_ja.html" }>
                            このドキュメント
                        </a>を確認してください。
                    </p>
                </div>
            </div>
        </TopPageSection>);
    }
}
