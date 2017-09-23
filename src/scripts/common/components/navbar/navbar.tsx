import * as classNames from "classnames";
import * as React from "react";
import * as style from "./navbar.scss"

interface Props extends React.HTMLAttributes<HTMLElement> {
    title?: string
    subTitle?: string
}

export const Navbar = (props: Props) => {
    let title: React.ReactNode;
    let subTitle: React.ReactNode;
    if ('title' in props) {
        title = <h1 className={ style.title }>{ props.title }</h1>
    }
    if ('subTitle' in props) {
        subTitle = <p className={ style.subTitle }>{ props.subTitle }</p>
    }
    return (
        <header className={ classNames(style.navbar, props.className) }>
            { title }
            { subTitle }
        </header>
    );
};
