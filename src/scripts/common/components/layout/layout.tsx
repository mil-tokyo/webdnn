import * as classNames from "classnames";
import * as React from "react";
import * as style from "./layout.scss";


export interface Props extends React.HTMLAttributes<HTMLElement> {
    row?: boolean
    column?: boolean
    autoReverse?: boolean
    fit?: boolean
    flex?: boolean | number
    center?: boolean
    stretch?: boolean
    block?: boolean
}

export const LayoutFrame = (props: Props) => (
    <div className={classNames(
        style.frame,
        props.className,
        (props.block ? style.block : null),
        (props.fit ? style.fit : null),
        (props.flex ? style.flex : null),
        (!props.block ? style.flexContainer : null),
        (!props.block && props.row ? style.row : null),
        (!props.block && props.column ? style.column : null),
        (!props.block && props.autoReverse ? style.autoReverse : null),
        (!props.block && (!props.row && !props.column && !props.autoReverse) ? style.auto : null),
        (!props.block && props.center ? style.center : null)
    )}>
        {props.block ?
         (
             <div className={classNames(
                 style.flexContainer,
                 style.blockInner,
                 (props.row ? style.row : null),
                 (props.column ? style.column : null),
                 (props.autoReverse ? style.autoReverse : null),
                 ((!props.row && !props.column && !props.autoReverse) ? style.auto : null),
                 (props.center ? style.center : null)
             )}>{props.children}</div>
         ) :
         props.children}
    </div>
);
