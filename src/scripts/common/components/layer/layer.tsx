import * as classNames from "classnames";
import * as style from "./layer.scss";
import * as React from "react";

const Layer = (props: React.HTMLAttributes<HTMLDivElement>) => (
    <div className={classNames(style.layer, props.className)}>
        {props.children}
    </div>
);

export default Layer;