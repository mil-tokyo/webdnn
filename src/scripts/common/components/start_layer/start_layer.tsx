import * as classNames from "classnames";
import * as React from "react";
import { LayoutFrame } from "../layout/layout";
import LinkButton from "../link_button/link_button";
import * as style from "./start_layer.scss";

declare function require(path: string): any;

const RunIcon = require('./ic_play_arrow_black_24px.svg');


interface Props extends React.HTMLAttributes<HTMLDivElement> {
    onStart?: () => any
}

const StartLayer = (props: Props) => (
    <div className={classNames(style.startLayer, props.className)}>
        <LayoutFrame fit center column>
            <LinkButton onClick={props.onStart}>
                <RunIcon />
                <span>Run This App</span>
            </LinkButton>
        </LayoutFrame>
    </div>
);


export default StartLayer;