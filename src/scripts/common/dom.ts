import * as react from "react";

const dom = {
    getElementById: function getElementById<T>(id: string) {
        let node = document.getElementById(id) as T | null;
        if (!node) throw Error(`#${id} is not found.`);

        return node!
    },
    querySelector: function querySelector<T>(element: HTMLElement, query: string) {
        let node = element.querySelector(query) as T | null;
        if (!node) throw Error(`${query} is not found.`);

        return node!
    },
    querySelectorAll: function querySelectorAll<T extends Element>(element: HTMLElement, query: string) {
        let nodes = element.querySelectorAll(query) as NodeListOf<T>;

        return Array.from(nodes);
    },
    getFromRef: function getFromRef<T extends Element>(component: react.Component, ref: string) {
        let node = component.refs[ref] as (T | null);
        if (!node) throw Error(`${ref} is not found in refs`);

        return node!
    }
};

export default dom;
