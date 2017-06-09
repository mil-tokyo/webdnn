import WebCam from "./modules/webcam";

function getElementById<T extends HTMLElement>(id: string): T {
    let element = document.getElementById(id) as T | null;
    if (!element) throw Error(`#${id} is not found.`);

    return element;
}

const App = new class {
    webcam: WebCam;

    async initialize() {
        let $activateButton = getElementById<HTMLButtonElement>('activateButton');
        $activateButton.addEventListener('click', (ev: MouseEvent) => this.onActivateButtonClick(ev));
    }

    async onActivateButtonClick(ev: MouseEvent) {
        try {
            await this.initializeCameraAsync('#previewContainer');
        } catch (e) {
            console.error(e);
        }
    }

    initializeCameraAsync(attachContainer: HTMLElement | string) {
        let webcam = new WebCam({
            width: 192,
            height: 144,
            fps: 60,
            imageFormat: 'png',
            flagForceFlash: false,
            swfURL: '/webdnn/webcam.swf'
        });
        this.webcam = webcam;
        return webcam.attachAsync(attachContainer);
    }

};

window.onload = () => {
    App.initialize();
};