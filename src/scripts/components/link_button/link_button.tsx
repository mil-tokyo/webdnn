import * as classNames from "classnames";
import * as React from "react";
import * as style from "./link_button.scss";

const LinkButton = (props: React.HTMLAttributes<HTMLAnchorElement>) => (
    <a className={classNames(style.linkButton, props.className)} href={props.href}>
        <div className={style.body}>{props.children}</div>
    </a>
);
export default LinkButton;