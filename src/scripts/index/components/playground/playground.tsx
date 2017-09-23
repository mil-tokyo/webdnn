import * as React from "react";
import { LayoutFrame } from "../../../common/components/layout/layout";
import { LinkButton } from "../link_button/link_button";
import * as style from "./playground.scss";

interface Props extends React.HTMLAttributes<HTMLDivElement> {
    url: string,
    title: string
}

interface State {
    isRunning: boolean
}

export default class Playground extends React.Component<Props, State> {
    constructor() {
        super();
        this.state = { isRunning: false };
    }

    onRunButtonClick() {
        this.setState({ isRunning: true });
    }

    render() {
        return (<div className={ style.playground }>
                <div className={ style.iframeWrapper }>
                    { this.state.isRunning ? (
                        <iframe className={ style.iframe }
                                width="728"
                                height="475"
                                frameBorder="0"
                                title={ this.props.title }
                                src={ this.props.url } />
                    ) : (
                          <LayoutFrame fit center>
                              <LinkButton onClick={ () => this.onRunButtonClick() }>Run This App</LinkButton>
                          </LayoutFrame>
                      ) }
                </div>
                <LinkButton className={ style.linkButton } href={ this.props.url + '?run=1' }>
                    Open This App
                </LinkButton>
            </div>
        );
    }
}