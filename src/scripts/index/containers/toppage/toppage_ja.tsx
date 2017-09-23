import * as React from "react"
import { PageFooterJA } from "../../components/page_footer/page_footer_ja";
import { PageHeaderJA } from "../../components/page_header/page_header_ja";
import Splash from "../../components/splash/splash";
import { AboutSectionJA } from "../about_section/about_section_ja";
import { BenchmarkSectionJA } from "../benchmark_section/benchmark_section_ja";
import BrowserCompatibilitySectionJA from "../browser_compatibility_section/browser_compatibility_section_ja";
import { NeuralStyleTransferExampleSectionJA } from "../neural_style_transfer_example_section/neural_style_transfer_example_section_ja";
import { ReferenceSection } from "../reference_section/reference_section";
import { Resnet50ExampleSectionJA } from "../resnet50_example_section/resnet50_example_section_ja";
import * as style from "./toppage.scss";

export const TopPageJA = (props: React.HTMLAttributes<HTMLElement>) => (
    <div className={ style.topPage }>
        <PageHeaderJA />
        <div>
            <Splash />
            <AboutSectionJA />
            <BrowserCompatibilitySectionJA />
            <BenchmarkSectionJA />
            <NeuralStyleTransferExampleSectionJA />
            <Resnet50ExampleSectionJA />
            <ReferenceSection />
            <PageFooterJA />
        </div>
    </div>
);
