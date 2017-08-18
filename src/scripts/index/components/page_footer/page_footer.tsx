import * as classNames from "classnames";
import * as React from "react";
import * as style from "./page_footer.scss";

const PageFooter = (props: React.HTMLAttributes<HTMLElement>) => (
    <footer className={classNames(style.pageFooter, props.className)}>
        <p>
            &copy;&nbsp;
            <a href="http://www.mi.t.u-tokyo.ac.jp/en" target="_blank" rel="noopener">
                Harada Ushiku Laboratory (Machine Intelligence Laboratory, MIL), Department of Mechano Informatics, The
                University of Tokyo
            </a>&nbsp;
            All Rights Reserved.
        </p>
    </footer>
);
export default PageFooter;
