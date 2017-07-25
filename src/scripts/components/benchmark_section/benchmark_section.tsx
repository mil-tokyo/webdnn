import * as React from "react"
import * as bootstrap from "../../common/bootstrap";
import TableWrapper from "../table_wrapper/table_wrapper";
import TopPageSection from "../toppage_section/toppage_section";
import * as style from "./benchmark_section.scss";

export const AnchorID = "benchmark";

declare function require(path: string): any;

const BenchmarkSection = (props: React.HTMLAttributes<HTMLElement>) => (
    <TopPageSection title="Benchmark" id={AnchorID}>
        <div className={bootstrap.row}>
            <div className={bootstrap.col12}>
                <p>
                    We measured execution time for
                    VGG16&nbsp;<a className="ref" href="#ref2">[2]</a>&nbsp;,
                    Inception-v3&nbsp;<a className="ref" href="#ref10">[10]</a>&nbsp;,
                    and ResNet50&nbsp;<a className="ref" href="#ref2">[3]</a>.
                    Below figure shows the result compared with Keras.js. Computation time per image is shown in
                    vertical axis as logarithmic scale. All tests were run on
                    Mac Book Pro early 2015,
                    Intel Core i5 2.7 GHz CPU,
                    16 GB Memory,
                    and Intel Iris Graphics 6100 GPU. The web browser is Safari Technology Preview 30.
                </p>
                <TableWrapper>
                    <img className={style.figure}
                         src={require('./performance-412x198.png')}
                         srcSet={`${require('./performance-824x396.png')} 824w,
                                  ${require('./performance-1236x594.png')} 1236w,
                                  ${require('./performance-1648x792.png')} 1648w`} />
                </TableWrapper>
            </div>
        </div>
    </TopPageSection>
);
export default BenchmarkSection;
