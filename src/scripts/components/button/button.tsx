import * as classNames from "classnames";
import * as React from "react";
import * as style from "./button.scss";

interface Props extends React.HTMLAttributes<HTMLButtonElement> {
    icon?: React.ReactNode,
    srcSet?: string,
    primary?: boolean
    active?: boolean
}

export class Button extends React.Component<Props, {}> {
    render() {
        let img: React.ReactNode = this.props.icon;
        if (typeof img == 'string') {
            img = <img className={style.image} src={img} srcSet={this.props.srcSet} />
        }

        let buttonClass: { [key: string]: boolean } = {};
        buttonClass[style.active] = this.props.active || false;
        buttonClass[style.primary] = this.props.primary || false;

        return (
            <button className={classNames(style.button, this.props.className, buttonClass)}
                    disabled={this.props.disabled}
                    onClick={this.props.onClick}>
                {img}
                <div className={style.body}>{this.props.children}</div>
            </button>
        );
    }
}

