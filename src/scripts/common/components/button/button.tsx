import * as classNames from "classnames";
import * as React from "react";
import { LayoutFrame } from "../layout/layout";
import * as style from "./button.scss";

interface Props extends React.HTMLAttributes<HTMLButtonElement> {
    srcSet?: string,
    primary?: boolean
    active?: boolean
    disabled?: boolean
}

const Button = (props: Props, {}) => {
    return (
        <button className={classNames(
            style.button,
            props.className,
            props.active ? style.active : null,
            props.primary ? style.primary : null
        )}
                disabled={props.disabled}
                onClick={props.onClick}>
            <div className={style.ripple} />
            <LayoutFrame fit column center className={style.body}>
                {props.children}
            </LayoutFrame>
        </button>
    );
};

export default Button;

