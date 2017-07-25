import * as classNames from "classnames";
import * as React from "react";
import "./control_bar.scss";

interface ControlBarProps extends React.HTMLAttributes<HTMLDivElement> {

}

interface ControlBarState {

}

export class ControlBar extends React.Component<ControlBarProps, ControlBarState> {
    render() {
        let header: React.ReactNode = null;
        if (this.props.title) {
            header = <header className="ControlBar-Header">
                {this.props.title}
            </header>
        }
        return (
            <div className={classNames('ControlBar', this.props.className)}>
                {header}
                <div className="ControlBar-Body">
                    {this.props.children}
                </div>
            </div>
        );
    }
}