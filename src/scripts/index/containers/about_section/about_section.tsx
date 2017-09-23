import * as classNames from "classnames"
import * as React from "react"
import * as bootstrap from "../../../common/bootstrap";
import { TableWrapper } from "../../components/table_wrapper/table_wrapper";
import { TopPageSection, TopPageSectionSubTitle } from "../../components/toppage_section/toppage_section";
import * as style from "./about_section.scss";

export const AnchorID = "about";

declare function require(path: string): any;

const PipelineSVG = require('./pipeline.svg');

export const AboutSection = (props: React.HTMLAttributes<HTMLElement>) => (
    <TopPageSection title="About MIL WebDNN" id={ AnchorID }>
        <div className={ bootstrap.row }>
            <div className={ bootstrap.col12 }>
                <TableWrapper className={ classNames(style.pipeline) }>
                    <PipelineSVG />
                </TableWrapper>
            </div>
            <div className={ classNames(bootstrap.col12, bootstrap.colLg4) }>
                <TopPageSectionSubTitle title="Run Trained DNN Model on Web Browser" />
                <p>
                    Deep neural network (DNN) is getting much attention to use in many applications. However, it
                    requires a lot of computational
                    resources, and there are many tremendous processes to setup execution environment based hardware
                    acceleration such as GPGPU. Therefore providing DNN applications to end-users is very hard.
                    WebDNN
                    solves this problem by using web browser as installation-free DNN execution framework. This
                    framework
                    optimizes trained DNN model to compress the model data and accelerate the execution, and
                    executes
                    it with novel JavaScript API such as WebAssembly and WebGPU to achieve zero-overhead execution.
                    Empirical
                    evaluations showed that it achieved more than 200x acceleration.
                </p>
            </div>
            <div className={ classNames(bootstrap.col12, bootstrap.colLg4) }>
                <TopPageSectionSubTitle title="Inference-phase-specialized Optimization" />
                <p>
                    To achieve speedier execution, optimizing the computation graph of DNN models is very important.
                    Execution of DNN consists of two phases, the training phase and the inference phase. The
                    training
                    phase updates the parameters with a back propagation technique. The inference phase makes
                    predictions (forward-propagation only) for the actual task. If the framework focuses on only the
                    inference phase, it can optimize the computation graph more aggressively.
                </p>
                <p>
                    WebDNN focuses on only the inference phase execution on end user devices and supports aggressive
                    optimization. This optimization pipeline can be applied for models trained with various DNN
                    frameworks. It is not required to edit the training codes.
                </p>
            </div>
            <div className={ classNames(bootstrap.col12, bootstrap.colLg4) }>
                <TopPageSectionSubTitle title="Next Generation JavaScript API" />
                <p>
                    JavaScript is executed by an interpreter. Therefore, it requires computing overhead and it
                    cannot
                    completely harness the capacity of the CPU. The same problem is encountered in GPU. Modern web
                    browsers support WebGL, which is a JavaScript API to use GPU. However, this API is designed for
                    graphics processing and is not suitable for general purpose computation. In addition, using
                    WebGL
                    for general purpose computing incurs overhead costs.
                </p>
                <p>
                    WebDNN uses next generation JavaScript API, WebGPU for GPU execution, and WebAssembly for CPU
                    execution. These APIs help to bring out the full performance of GPU and CPU.
                </p>
            </div>
        </div>
    </TopPageSection>
);