import * as classNames from "classnames";
import * as React from "react";
import * as style from "./flat_button.scss";

const FlatButton = (props: React.HTMLAttributes<HTMLButtonElement>) => (
    <button className={classNames(style.flatButton, this.props.className, {
        'Button--primary': this.props.primary
    })}
            {...props}>
        <div className={style.body}>{this.props.children}</div>
    </button>
);
export default FlatButton;