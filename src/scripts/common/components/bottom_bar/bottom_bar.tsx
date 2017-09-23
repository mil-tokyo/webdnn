import * as classNames from "classnames";
import * as React from "react";
import { LayoutFrame } from "../layout/layout";
import * as style from "./bottom_bar.scss"

interface Props extends React.HTMLAttributes<HTMLElement> {
}


export const BottomBar = (props: Props) => {
    return (
        <LayoutFrame className={ classNames(style.bottomBar, props.className) } row>
            { props.children }
        </LayoutFrame>
    );
};
