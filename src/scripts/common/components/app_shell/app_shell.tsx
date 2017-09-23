import * as classNames from "classnames";
import * as React from "react";
import { BottomBar } from "../bottom_bar/bottom_bar";
import Button from "../button/button";
import { LayoutFrame } from "../layout/layout";
import { Navbar } from "../navbar/navbar";
import ProgressBar from "../progress_bar/progress_bar";
import * as style from "./app_shell.scss";

interface Props extends React.HTMLAttributes<HTMLDivElement> {
    title?: string
    subTitle?: string
    progressBar?: boolean
    bottomBar?: BottomBarDescriptor[]
}

export interface BottomBarDescriptor {
    label: string
    onClick?: React.MouseEventHandler<HTMLButtonElement>,
    icon?: React.ReactFragment,
    disabled?: boolean,
    primary?: boolean
}


export const AppShell = (props: Props) => (
    <div className={ classNames(style.appShell, props.className) }>
        { props.progressBar ? <ProgressBar running /> : null }
        <Navbar title={ props.title } subTitle={ props.subTitle } />
        <LayoutFrame className={ style.main } column>
            <LayoutFrame flex column>
                { props.children }
            </LayoutFrame>
            {
                props.bottomBar ? (
                    <BottomBar>
                        { props.bottomBar.map((desc, i) => (
                            <Button key={ i }
                                    onClick={ desc.onClick }
                                    disabled={ desc.disabled }
                                    primary={ desc.primary }>
                                { desc.icon }
                                <span>{ desc.label }</span>
                            </Button>
                        )) }
                    </BottomBar>
                ) : null
            }
        </LayoutFrame>
    </div>
);