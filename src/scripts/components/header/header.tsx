import * as classNames from "classnames";
import * as React from "react";
import "./header.scss";

interface Props extends React.HTMLAttributes<HTMLElement> {
    title?: string
}

interface State {

}

export class Header extends React.Component<Props, State> {
    render() {
        let title: React.ReactNode;
        if ('title' in this.props) {
            title = <h1 className="Header-Title">{this.props.title}</h1>
        }
        return (
            <header className={classNames('Header', this.props.className)}>
                {title}
                {this.props.children}
            </header>
        );
    }
}