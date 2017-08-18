import * as classNames from "classnames"
import * as React from "react"
import * as bootstrap from "../../../common/bootstrap";
import TableWrapper from "../../components/table_wrapper/table_wrapper";
import TopPageSection, { TopPageSectionSubTitle } from "../../components/toppage_section/toppage_section";
import * as style from "./about_section.scss";

export const AnchorID = "about";

declare function require(path: string): any;

const PipelineSVG = require('./pipeline.svg');

const AboutSectionJA = (props: React.HTMLAttributes<HTMLElement>) => (
    <TopPageSection title="About MIL WebDNN" id={AnchorID}>
        <div className={bootstrap.row}>
            <div className={bootstrap.col12}>
                <TableWrapper className={classNames(style.pipeline)}>
                    <PipelineSVG />
                </TableWrapper>
            </div>
            <div className={classNames(bootstrap.col12, bootstrap.colLg4)}>
                <TopPageSectionSubTitle title="Run Trained DNN Model on Web Browser" />
                <p>
                    近年、ディープニューラルネットワーク(Deep neural network, DNN)が様々なタスクで著しい成果をあげ注目されていますが、
                    計算負荷の高さがアプリケーション応用の際の問題となっています。
                    ハードウェアアクセラレーションによる解決方法では、煩雑な計算環境セットアップ手順やハードウェアの価格等が問題となり、
                    ユーザーエンド端末に同様の環境を構築することは非常に困難です。
                </p>
                <p>
                    WebDNNはこの問題を解決するために作られた、ウェブブラウザを利用したインストールフリーなDNN実行環境です。
                    WebDNNにより、ウェブブラウザ上での実行を前提とした積極的な最適化が学習済みモデルに行われるため、
                    パラメータデータの配信サイズを小さく抑え、高速な実行が可能となります。既存のライブラリと比較して最大200倍の高速化が達成できます。
                </p>
            </div>
            <div className={classNames(bootstrap.col12, bootstrap.colLg4)}>
                <TopPageSectionSubTitle title="Inference-phase-specialized Optimization" />
                <p>
                    DNNモデル計算グラフの最適化は、高速実行において非常に重要です。DNNの実行は学習フェーズと推論フェーズという、
                    2種類のフェーズに分けられます。学習フェーズでは学習に必要な中間データを保持しておく必要がありますが、推論フェーズでは
                    これらのデータを保持しておく必要はありません。このように、推論フェーズに特化することでDNNフレームワークはより積極的な
                    計算グラフ最適化が可能となります。
                </p>
                <p>
                    WebDNNはユーザーエンドデバイスでの推論フェーズ実行に特化しており、学習済みモデルの積極的な最適化をサポートしています。
                    また、この最適化パイプラインは既存の様々なDNN学習フレームワークに対応しており、
                    学習に使用したソースコードを一切変更すること無く利用することができます。
                </p>
            </div>
            <div className={classNames(bootstrap.col12, bootstrap.colLg4)}>
                <TopPageSectionSubTitle title="Next Generation JavaScript API" />
                <p>
                    JavaScriptで高速演算を行う上で、インタプリタ実行に起因するオーバーヘッドは深刻な問題となります。
                    この問題を解決するために、WebDNNはWebAssemblyで実装されたCPU演算バックエンドを提供しています。
                    このバックエンドは従来のJavaScriptと比較し、非常に小さなオーバーヘッドで実行することができます。
                </p>
                <p>
                    また、DNNの高速実行のためにはGPUの汎用目的での利用(GPGPU)が一般的となっていますが、
                    現状のJavaScript用GPU APIであるWebGLは画像処理用途に特化しており、汎用演算には適していませんでした。
                    WebDNNでは次世代のGPU API仕様であるWebGPUを利用し、GPUを利用した高速演算が可能となっています。
                    WebGPUは、GPUの汎用計算目的での利用を前提に設計されており、WebGLと比較してオーバーヘッドの少ない処理実行が可能となります。
                </p>
            </div>
        </div>
    </TopPageSection>
);
export default AboutSectionJA;
