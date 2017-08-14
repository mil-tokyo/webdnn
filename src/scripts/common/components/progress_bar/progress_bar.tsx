import * as classNames from "classnames";
import * as React from "react";
import * as style from "./progress_bar.scss";

const ProgressBar = (props: { running: boolean } & React.HTMLAttributes<HTMLElement>) => (
    <div className={classNames(
        style.progressBar,
        props.className,
        props.running ? style.running : null
    )}>
        <div className={style.inner} />
    </div>
);
export default ProgressBar