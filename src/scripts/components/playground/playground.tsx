import * as React from "react";
import LinkButton from "../link_button/link_button";
import * as style from "./playground.scss";

interface Props extends React.HTMLAttributes<HTMLDivElement> {
    url: string,
    title: string
}

class Playground extends React.Component<Props, {}> {
    render() {
        return (<div className={style.playground}>
            <iframe className={style.iframe}
                    width="728"
                    height="475"
                    frameBorder="0"
                    title={this.props.title}
                    src={this.props.url} />
            <LinkButton className={style.linkButton} href={this.props.url + '?run=1'}>
                Open This App
            </LinkButton>
        </div>);
    }
}

export default Playground;