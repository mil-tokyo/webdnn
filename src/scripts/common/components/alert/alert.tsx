import * as classNames from "classnames";
import * as React from "react";
import * as style from "./alert.scss";

interface Props extends React.HTMLAttributes<HTMLButtonElement> {
    srcSet?: string,
    primary?: boolean
    active?: boolean
}

class Alert extends React.Component<Props, {}> {
    render() {
        return (
            <button className={classNames(
                style.alert,
                this.props.className,
            )}>
                {this.props.children}
            </button>
        );
    }
}

export default Alert;

