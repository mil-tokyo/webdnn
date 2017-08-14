import * as classNames from "classnames";
import * as React from "react";
import { LayoutFrame } from "../layout/layout";
import * as style from "./initialize_layer.scss";

interface Props extends React.HTMLAttributes<HTMLDivElement> {
    message?: string
    rate: number
}

class InitializeLayer extends React.Component<Props, {}> {
    render() {
        return (
            <div className={classNames(style.initializeLayer, this.props.className)}>
                <LayoutFrame fit center column>
                    <span className={style.message}>
                        {this.props.message || ""}
                    </span>
                    <div className={style.progress}>
                        <div className={style.progressOuter}>
                            <div className={style.progressInner} style={{
                                WebkitTransform: `scaleX(${this.props.rate})`,
                                MozTransform: `scaleX(${this.props.rate})`,
                                transform: `scaleX(${this.props.rate})`
                            }} />
                        </div>
                    </div>
                </LayoutFrame>
            </div>
        );
    }
}

export default InitializeLayer;