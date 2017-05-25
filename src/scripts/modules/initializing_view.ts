import ProgressBar from "./progress_bar";

export default class InitializingView {
    base: HTMLElement;
    message: HTMLElement;
    progressBar: ProgressBar;

    constructor(base: HTMLElement) {
        this.base = base;

        let message = base.querySelector('.InitializingView-Message') as HTMLElement;
        if (!message) throw Error('.InitializingView-Message not found');
        this.message = message;

        let progressBarInner = base.querySelector('.ProgressBar-Inner') as HTMLElement;
        if (!progressBarInner) throw Error('.ProgressBar-Inner not found');
        this.progressBar = new ProgressBar(progressBarInner);
    }

    updateProgress(ratio: number) {
        this.progressBar.update(ratio);
    }

    updateMessage(message: string) {
        this.message.textContent = message;
    }

    remove() {
        if (this.base.parentNode) {
            this.base.parentNode.removeChild(this.base);
        }
    }
}