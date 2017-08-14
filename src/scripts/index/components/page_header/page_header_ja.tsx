import * as classNames from "classnames";
import * as React from "react";
import * as bootstrap from "../../../common/bootstrap";
import { AnchorID as AboutAnchorID } from "../../containers/about_section/about_section";
import { AnchorID as BenchmarkAnchorID } from "../../containers/benchmark_section/benchmark_section";
import { AnchorID as CompatibilityAnchorID } from "../../containers/browser_compatibility_section/browser_compatibility_section";
import { AnchorID as ExampleSectionAnchorID } from "../../containers/neural_style_transfer_example_section/neural_style_transfer_example_section";
import * as style from "./page_header.scss";

declare function require(path: string): any;

const GitHubSVG = require('./github.svg');

const PageHeaderJA = (props: React.HTMLAttributes<HTMLElement>) => (
    <header className={classNames(style.pageHeader, props.className)}>
        <h1><span className={style.logo}>MIL</span> WebDNN</h1>
        <div className={style.itemContainer}>
            <p className={classNames(style.menu, bootstrap.mobileHide)}>
                <a href={'#' + AboutAnchorID}>About</a>
                <a href={'#' + CompatibilityAnchorID}>Compatibility</a>
                <a href={'#' + BenchmarkAnchorID}>Benchmark</a>
                <a href={'#' + ExampleSectionAnchorID}>Examples</a>
            </p>
            <p className={style.link}>
                <a href="/webdnn"><span>English</span></a>
                <a href="https://github.com/mil-tokyo/webdnn">
                    <GitHubSVG />
                </a>
            </p>
        </div>
    </header>
);

export default PageHeaderJA