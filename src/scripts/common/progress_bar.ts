export default class ProgressBar {
    bar: HTMLElement;

    constructor(bar: HTMLElement) {
        this.bar = bar;
    }

    update(ratio: number) {
        this.bar.style.width = `${Math.min(Math.max(ratio, 0), 1) * 100}%`;
    }
}