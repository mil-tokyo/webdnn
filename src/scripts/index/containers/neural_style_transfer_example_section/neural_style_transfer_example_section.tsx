import * as classNames from "classnames";
import * as React from "react";
import * as bootstrap from "../../../common/bootstrap";
import Playground from "../../../common/components/playground/playground";
import TopPageSection from "../../components/toppage_section/toppage_section";

export const AnchorID = "neural-style-transfer";

const NeuralStyleTransferExampleSection = (props: React.HTMLAttributes<HTMLElement>) => (
    <TopPageSection title="Neural Style Transfer" id={AnchorID}>
        <div className={bootstrap.row}>
            <div className={classNames(bootstrap.col12, bootstrap.colLg)}>
                <p>
                    This example runs Neural Style Transfer model&nbsp;<a className="ref" href="#ref4">[4]</a>.
                    Neural Style Transfer model are given 2 input images, one is content image and another is style
                    image. Then this model generate an image based on the style of the style image and the content
                    in the content image.
                </p>
                <p>
                    We use chainer&nbsp;<a className="ref" href="#ref5">[5]</a>&nbsp;implementation provided
                    in&nbsp;<a className="ref" href="#ref6">[6]</a>&nbsp;and pre-trained model provided
                    in&nbsp;<a className="ref" href="#ref7">[7]</a>.
                    The pre-trained model are transpiled by&nbsp;<b>GraphTranspiler</b>&nbsp;into graph descriptor,
                    and then executed by&nbsp;<b>DescriptorRunner</b>.&nbsp;<b>All computation are done by web
                                                                               browser, not by server.</b>
                </p>
            </div>
            <div className={classNames(bootstrap.col12, bootstrap.colLg)}>
                <Playground url="/webdnn/neural_style_transfer.html" title="Neural Style Transfer" />
            </div>
        </div>
    </TopPageSection>
);

export default NeuralStyleTransferExampleSection;
