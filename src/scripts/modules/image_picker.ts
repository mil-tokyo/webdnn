export default class ImagePicker {
    input: HTMLInputElement;
    context: CanvasRenderingContext2D;
    onload: () => any;

    constructor(input: HTMLInputElement, context: CanvasRenderingContext2D) {
        this.input = input;
        this.context = context;

        this.input.addEventListener('change', (ev) => this.onInputChange(ev));
    }

    private onInputChange(ev: Event) {
        if (!this.input || !this.input.files || !this.input.files[0]) return;

        this.loadByFile(this.input.files[0])
            .then(() => {
                if (this.onload) {
                    this.onload();
                }
            })
            .catch(err => {
                throw err
            });
    }

    async loadByFile(file: File) {
        let reader = new FileReader();

        return new Promise(resolve => {
            reader.onload = ev => this.loadByUrl(reader.result);
            reader.readAsDataURL(file);
        });
    }

    async loadByUrl(url: string) {
        let image;
        try {
            image = await this.fetchImageAsync(url);
        } catch (err) {
            throw err;
        }
        this.setImageToCanvas(image);
        if (this.onload) {
            this.onload();
        }
    }

    private setImageToCanvas(image: HTMLImageElement) {
        this.context.drawImage(image, 0, 0, image.width, image.height, 0, 0, this.context.canvas.width, this.context.canvas.height);
    }

    private fetchImageAsync(url: string): Promise<HTMLImageElement> {
        let image = new Image();

        return new Promise(resolve => {
            image.onload = () => resolve(image);
            image.src = url;
        });
    }
}