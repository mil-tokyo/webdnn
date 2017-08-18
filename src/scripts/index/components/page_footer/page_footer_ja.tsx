import * as classNames from "classnames";
import * as React from "react";
import * as style from "./page_footer.scss";

const PageFooterJA = (props: React.HTMLAttributes<HTMLElement>) => (
    <footer className={classNames(style.pageFooter, props.className)}>
        <p>
            &copy;&nbsp;<a href="http://www.mi.t.u-tokyo.ac.jp" target="_blank" rel="noopener">
            東京大学 情報理工学系研究科 知能機械情報学専攻 原田・牛久研究室</a>&nbsp;All Rights Reserved.
        </p>
    </footer>
);
export default PageFooterJA;
