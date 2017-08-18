import * as classNames from "classnames";
import * as React from "react";
import { LayoutFrame, Props as LayoutProps } from "../layout/layout";
import Navbar from "../navbar/navbar";
import * as style from "./navbar_layer.scss";

interface Props extends LayoutProps {
    title?: string
}

const NavbarLayer = (props: Props) => (
    <div className={classNames(style.navbarLayer, props.className)}>
        <Navbar title={props.title} />
        <LayoutFrame className={style.main} {...props}>
            {props.children}
        </LayoutFrame>
    </div>
);
export default NavbarLayer