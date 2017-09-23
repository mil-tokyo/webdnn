import * as classNames from "classnames"
import * as React from "react"
import * as bootstrap from "../../../common/bootstrap";
import { default as Playground } from "../../components/playground/playground";
import { TopPageSection } from "../../components/toppage_section/toppage_section";

export const Resnet50ExampleSectionJA = (props: React.HTMLAttributes<HTMLElement>) => (
    <TopPageSection title="ResNet50 Image Classification">
        <div className={ bootstrap.row }>
            <div className={ classNames(bootstrap.col12, bootstrap.colLg) }>
                <p>
                    このサンプルでは、画像識別モデルのResNet50を実行します。モデルはImageNet
                    <a className="ref" href="#ref8">[8]</a>データセットで学習されており、オリジナルの学習済みモデルは
                    <a className="ref" href="#ref9">[9]</a>で配布されています。
                    <b>すべての演算はウェブブラウザ上で行われており、画像の外部への送信等は一切行っていません。</b>
                </p>
            </div>
            <div className={ classNames(bootstrap.col12, bootstrap.colLg) }>
                <Playground url="/webdnn/resnet50.html" title="ResNet50 Image Classification" />
            </div>
        </div>
    </TopPageSection>
);
