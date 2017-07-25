import * as classNames from "classnames";
import * as React from "react";
import "./imagenet_classification_result.scss";

interface Props extends React.HTMLAttributes<HTMLDivElement> {
}

interface State {
}

export class ImageNetClassificationResult extends React.Component<Props, State> {
    constructor() {
        super();

        this.state = {}
    }

    render() {
        return (
            <div className={classNames('ImageNetClassificationResult', this.props.className)}>
                <div className="ImageNetClassificationResult-Body">{this.props.children}</div>
            </div>
        );
    }
}