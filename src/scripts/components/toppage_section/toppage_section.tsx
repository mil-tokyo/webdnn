import * as classNames from "classnames";
import * as React from "react";
import * as bootstrap from "../../common/bootstrap";
import * as style from "./toppage_section.scss";

interface Props extends React.HTMLAttributes<HTMLElement> {
    title?: string
    id?: string
}

export const TopPageSectionTitle = (props: { title: string }) => (
    <div className={bootstrap.row}>
        <div className={bootstrap.col12}>
            <h2 className={style.sectionTitle}>{props.title}</h2>
        </div>
    </div>
);

export const TopPageSectionSubTitle = (props: { title: string }) => (
    <h2 className={style.sectionSubTitle}>{props.title}</h2>
);

const TopPageSection = (props: Props) => (
    <section className={classNames(style.section, props.className)}>
        {props.id ? <a className={style.sectionAnchor} id={props.id} /> : null}
        <div className={bootstrap.container}>
            {props.title ? <TopPageSectionTitle title={props.title} /> : null}
            {props.children}
        </div>
    </section>
);

export default TopPageSection;
