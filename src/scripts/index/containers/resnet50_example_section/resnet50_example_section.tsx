import * as classNames from "classnames"
import * as React from "react"
import * as bootstrap from "../../../common/bootstrap";
import Playground from "../../../common/components/playground/playground";
import TopPageSection from "../../components/toppage_section/toppage_section";

const Resnet50ExampleSection = (props: React.HTMLAttributes<HTMLElement>) => (
    <TopPageSection title="ResNet50 Image Classification">
        <div className={bootstrap.row}>
            <div className={classNames(bootstrap.col12, bootstrap.colLg)}>
                <p>
                    In this example you can run ResNet50 classification model trained
                    by ImageNet&nbsp;<a className="ref" href="#ref8">[8]</a>. Original pre-trained model is provided
                    in&nbsp;<a className="ref" href="#ref9">[9]</a>.&nbsp;<b>
                    All computation are done by web browser, not by server.</b>
                </p>
            </div>
            <div className={classNames(bootstrap.col12, bootstrap.colLg)}>
                <Playground url="/webdnn/resnet.html" title="ResNet50 Image Classification" />
            </div>
        </div>
    </TopPageSection>
);
export default Resnet50ExampleSection;
