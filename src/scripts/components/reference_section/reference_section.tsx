import * as React from "react"
import * as bootstrap from "../../common/bootstrap";
import TopPageSection from "../toppage_section/toppage_section";
import * as style from "./reference_section.scss";

interface ReferenceItemBaseProps extends React.HTMLAttributes<HTMLLIElement> {
}

interface ReferenceItemWebPageProps extends ReferenceItemBaseProps {
    url: string,
    title?: string
}

interface ReferenceItemPaperProps extends ReferenceItemBaseProps {
    authors: string,
    title: string,
    conference: string,
    year: number
}

export const ReferenceItemBase = (props: ReferenceItemBaseProps) => (<li id={props.id}>{props.children}</li>);

export const ReferenceItemWebPage = (props: ReferenceItemWebPageProps) => (
    <ReferenceItemBase id={props.id}>
        <a target="_blank" href={props.url} rel="noopener">{props.title || props.url}</a>
    </ReferenceItemBase>
);

export const ReferenceItemPaper = (props: ReferenceItemPaperProps) => (
    <ReferenceItemBase id={props.id}>
        {props.authors}, <i>"{props.title}"</i>, {props.conference}, {props.year}.
    </ReferenceItemBase>
);

const ReferenceSection = (props: React.HTMLAttributes<HTMLElement>) => (
    <TopPageSection title="References">
        <div className={bootstrap.row}>
            <div className={bootstrap.col12}>
                <ol className={style.reference}>
                    <ReferenceItemWebPage url="https://github.com/transcranial/keras-js" id="ref1" />
                    <ReferenceItemPaper authors="K. Simonyan, and A. Zisserman"
                                        title="Very Deep Convolutional Networks for Large-Scale Image Recognition"
                                        conference="the International Conference on Learning Representations (ICLR)"
                                        year={2014}
                                        id="ref2" />
                    <ReferenceItemPaper authors="K. He, X. Zhang, S. Ren, and J. Sun"
                                        title="Deep Residual Learning for Image Recognition"
                                        conference="IEEE Conference on Computer Vision and Pattern Recognition (CVPR)"
                                        year={2015}
                                        id="ref3" />
                    <ReferenceItemPaper authors="J. Johnson, A. Alahi, and L. Fei-Fei"
                                        title="Perceptual Losses for Real-time Style Transfer and Single Image Super-Resolution"
                                        conference="International Conference on Machine Learning (ICML)"
                                        year={2015}
                                        id="ref4" />
                    <ReferenceItemWebPage url="https://github.com/pfnet/chainer"
                                          id="ref5" />
                    <ReferenceItemWebPage url="https://github.com/yusuketomoto/chainer-fast-neuralstyle"
                                          id="ref6" />
                    <ReferenceItemWebPage url="https://github.com/gafr/chainer-fast-neuralstyle-models"
                                          id="ref7" />
                    <ReferenceItemPaper authors="J. Deng, W. Dong, R. Socher, L. Li, K. Li and L. Fei-Fei"
                                        title="ImageNet: A Large-Scale Hierarchical Image Database"
                                        conference="IEEE Conference on Computer Vision and Pattern Recognition (CVPR)"
                                        year={2009}
                                        id="ref8" />
                    <ReferenceItemWebPage url="https://github.com/KaimingHe/deep-residual-networks"
                                          id="ref9" />
                    <ReferenceItemPaper authors="C. Szegedy, V. Vanhoucke, S. Ioffe, J. Shlens, Z and Wojna"
                                        title="The IEEE Conference on Computer Vision and Pattern Recognition (CVPR)"
                                        conference="The IEEE Conference on Computer Vision and Pattern Recognition (CVPR)"
                                        year={2016}
                                        id="ref10" />
                </ol>
            </div>
        </div>
    </TopPageSection>
);
export default ReferenceSection;
