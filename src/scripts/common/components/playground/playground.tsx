import * as React from "react";
import LinkButton from "../link_button/link_button";
import * as style from "./playground.scss";

interface Props extends React.HTMLAttributes<HTMLDivElement> {
    url: string,
    title: string
}

const Playground = (props: Props) => (<div className={style.playground}>
    <iframe className={style.iframe}
            width="728"
            height="475"
            frameBorder="0"
            title={props.title}
            src={props.url} />
    <LinkButton className={style.linkButton} href={props.url + '?run=1'}>
        Open This App
    </LinkButton>
</div>);

export default Playground;