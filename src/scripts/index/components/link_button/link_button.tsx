import * as classNames from "classnames";
import * as React from "react";
import * as style from "./link_button.scss";

export const LinkButton = (props: React.AnchorHTMLAttributes<HTMLElement>) => (
    <a className={ classNames(style.linkButton, props.className) }
       href={ props.href }
       onClick={ props.onClick }>
        <div className={ style.body }>{ props.children }</div>
    </a>
);