import * as classNames from "classnames";
import * as React from "react";
import * as style from "./navbar.scss"

interface Props extends React.HTMLAttributes<HTMLElement> {
    title?: string
}

class Navbar extends React.Component<Props, {}> {
    render() {
        let title: React.ReactNode;
        if ('title' in this.props) {
            title = <h1 className={style.title}>{this.props.title}</h1>
        }
        return (
            <header className={classNames(style.navbar, this.props.className)}>
                {title}
                {this.props.children}
            </header>
        );
    }
}

export default Navbar