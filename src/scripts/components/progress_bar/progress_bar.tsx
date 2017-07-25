import * as classNames from "classnames";
import * as React from "react";
import "./progress_bar.scss";

interface Props extends React.HTMLAttributes<HTMLDivElement> {
    running?: boolean,
}

interface State {
    running: boolean
}

export class ProgressBar extends React.Component<Props, State> {
    constructor() {
        super();

        this.state = {
            running: false
        }
    }

    get running(): boolean {
        return ('running' in this.props) ? this.props.running! : this.state.running;
    }

    render() {
        return (
            <div className={classNames('ProgressBar', this.props.className, {
                'ProgressBar--running': this.running,
            })}>
                <div className="ProgressBar-Inner" />
            </div>
        );
    }
}