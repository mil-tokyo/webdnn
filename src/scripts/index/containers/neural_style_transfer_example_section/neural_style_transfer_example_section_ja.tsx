import * as classNames from "classnames";
import * as React from "react";
import * as bootstrap from "../../../common/bootstrap";
import Playground from "../../../common/components/playground/playground";
import TopPageSection from "../../components/toppage_section/toppage_section";

export const AnchorID = "neural-style-transfer";

const NeuralStyleTransferExampleSectionJA = (props: React.HTMLAttributes<HTMLElement>) => (
    <TopPageSection title="Neural Style Transfer" id={AnchorID}>
        <div className={bootstrap.row}>
            <div className={classNames(bootstrap.col12, bootstrap.colLg)}>
                <p>
                    このサンプルでは、DNNによる画風変換を行います。Neural Style Transfer
                    <a className="ref" href="#ref4">[4]</a>と呼ばれるこのモデルは、コンテンツ画像とスタイル画像という2種類の画像を入力とし、
                    スタイル画像の画風をコンテンツ画像へ適用した、新しい画像を生成します。
                </p>
                <p>
                    このサンプルで使用したモデルは、Chainer<a className="ref" href="#ref5">[5]</a>で実装されており、
                    <a className="ref" href="#ref6">[6]</a>で配布されています。また、学習済みモデルのデータは
                    <a className="ref" href="#ref7">[7]</a>で配布されています。学習済みモデルは<b>GraphTranspiler</b>
                    によってGraphDescriptorへとトランスパイルされ、<b>DescriptorRunner</b>によって実行されています。
                    <b>すべての演算はウェブブラウザ上で行われており、画像の外部への送信等は一切行っていません。</b>
                </p>
            </div>
            <div className={classNames(bootstrap.col12, bootstrap.colLg)}>
                <Playground url="/webdnn/neural_style_transfer.html" title="Neural Style Transfer" />
            </div>
        </div>
    </TopPageSection>
);

export default NeuralStyleTransferExampleSectionJA;
