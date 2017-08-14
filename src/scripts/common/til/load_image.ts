/**
 * Load image of specified url and return HTMLImageElement object
 * @param {string} url
 * @returns {HTMLImageElement}
 */
export async function loadImageByUrl(url: string): Promise<HTMLImageElement> {
    let image = new Image();

    await new Promise((resolve, reject) => {
        image.onload = resolve;
        image.onerror = reject;
        image.src = url;
    });

    return image;
}

/**
 * Pick an image by dialog, and load selected image.
 *
 * In current web standard, the cancel event of the dialog cannot be handled.
 * Therefore even if user cancel the instruction, no error is thrown and the promise is still pending.
 * However, when the dialog is re-opened and an image is picked, the previous promise is rejected and
 * new promise is resolved.
 *
 * @returns {Promise<HTMLImageElement>}
 */
let lastPromiseRejectHandler: (() => any) | null = null;

export async function loadImageByDialog(): Promise<HTMLImageElement> {
    if (lastPromiseRejectHandler) lastPromiseRejectHandler();

    let $input = document.createElement('input');
    $input.type = 'file';
    $input.multiple = false;
    $input.accept = 'image/*';
    $input.style.visibility = 'hidden';
    $input.style.position = 'absolute';
    document.body.appendChild($input);

    return new Promise<HTMLImageElement>((resolve, reject) => {
        $input.onchange = async () => {
            let $img = await loadImageFromFileInput($input);
            document.body.removeChild($input);

            resolve($img);
        };
        lastPromiseRejectHandler = () => reject(Error('File loading is canceled'));
        $input.click();
    });
}

/**
 * Load an image from <input type=file>.
 *
 * If no image file is selected, an error is thrown.
 *
 * @param $input file input element
 * @returns {Promise<HTMLImageElement>}
 */
export async function loadImageFromFileInput($input: HTMLInputElement): Promise<HTMLImageElement> {
    if (!$input.files || !$input.files[0]) throw Error('No file is selected.');
    return loadImageByUrl(URL.createObjectURL($input.files[0]));
}
