import * as React from "react"
import AboutSection from "../about_section/about_section";
import BenchmarkSection from "../benchmark_section/benchmark_section";
import BrowserCompatibilitySection from "../browser_compatibility_section/browser_compatibility_section";
import NeuralStyleTransferExampleSection from "../neural_style_transfer_example_section/neural_style_transfer_example_section";
import PageFooter from "../page_footer/page_footer";
import PageHeader from "../page_header/page_header";
import ReferenceSection from "../reference_section/reference_section";
import Resnet50ExampleSection from "../resnet50_example_section/resnet50_example_section";
import Splash from "../splash/splash";
// noinspection ES6UnusedImports
import * as style from "./toppage.scss";

const TopPage = (props: React.HTMLAttributes<HTMLElement>) => (
    <div className={style.topPage}>
        <PageHeader />
        <div>
            <Splash />
            <AboutSection />
            <BrowserCompatibilitySection />
            <BenchmarkSection />
            <NeuralStyleTransferExampleSection />
            <Resnet50ExampleSection />
            <ReferenceSection />
            <PageFooter />
        </div>
    </div>
);
export default TopPage;
