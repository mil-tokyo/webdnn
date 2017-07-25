import * as classNames from "classnames";
import * as React from "react";
import "./tab.scss";

interface Props extends React.HTMLAttributes<HTMLDivElement> {
    selectedIndex: number
}

interface State {
}

export class Tab extends React.Component<Props, State> {
    constructor() {
        super();

        this.state = {}
    }

    render() {
        return (
            <div className={classNames('Tab', this.props.className)}>
                {React.Children.toArray(this.props.children)[this.props.selectedIndex]}
            </div>
        );
    }
}