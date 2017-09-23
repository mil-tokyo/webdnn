import * as React from "react"
import * as bootstrap from "../../../common/bootstrap";
import { TableWrapper } from "../../components/table_wrapper/table_wrapper";
import { TopPageSection } from "../../components/toppage_section/toppage_section";
import * as style from "./benchmark_section.scss";

export const AnchorID = "benchmark";

declare function require(path: string): any;

export const BenchmarkSectionJA = (props: React.HTMLAttributes<HTMLElement>) => (
    <TopPageSection title="Benchmark" id={ AnchorID }>
        <div className={ bootstrap.row }>
            <div className={ bootstrap.col12 }>
                <p>
                    画像識別モデルのVGG16<a className="ref" href="#ref2">[2]</a>,
                    Inception-v3<a className="ref" href="#ref10">[10]</a>,
                    及びResNet50<a className="ref" href="#ref3">[3]</a>の実行速度を、Keras.jsと比較した結果を示します。
                    縦軸は画像一枚あたりの処理時間（対数スケール）を表しています。
                    すべての実行はMac Book Pro early 2015, Intel Core i5 2.7 GHz CPU, 16 GB Memory, Intel Iris Graphics
                    6100 GPUで行い、ウェブブラウザはSafari Technology Preview 30を使用しました。
                </p>
                <TableWrapper>
                    <img className={ style.figure }
                         src={ require('./performance-412x198.png') }
                         srcSet={ `${require('./performance-824x396.png')} 824w,
                                  ${require('./performance-1236x594.png')} 1236w,
                                  ${require('./performance-1648x792.png')} 1648w` } />
                </TableWrapper>
            </div>
        </div>
    </TopPageSection>
);
