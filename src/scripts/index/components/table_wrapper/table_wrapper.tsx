import * as classNames from "classnames";
import * as React from "react";
import * as style from "./table_wrapper.scss";

const TableWrapper = (props: React.HTMLAttributes<HTMLDivElement>) => (
    <div className={classNames(style.tableWrapper, props.className)}>
        {props.children}
    </div>
);

export default TableWrapper;
