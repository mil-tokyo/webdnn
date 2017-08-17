/**
 * @module webdnn/image
 */

/** Don't Remove This comment block */

/**
 * Load image of specified url
 *
 * @param {string} url the image url
 * @returns {Promise<HTMLImageElement>} image element
 */
export async function loadImageByUrl(url: string): Promise<HTMLImageElement> {
    let image = document.createElement('img');

    return new Promise((resolve, reject) => {
        image.onload = resolve;
        image.onerror = reject;
        image.src = url;
    })
        .then(() => image);
}

/* istanbul ignore next */
/**
 * Load image file selected in `<input type="file">` element.
 *
 * @param {HTMLInputElement} input the `<input type="file">` element
 * @returns {Promise<HTMLImageElement>} image element
 */
export async function loadImageFromFileInput(input: HTMLInputElement): Promise<HTMLImageElement> {
    let files = input.files;
    if (!files || files.length == 0) throw new Error('No file is selected');

    let url = URL.createObjectURL(files[0]);

    return loadImageByUrl(url);
}

/* istanbul ignore next */
/**
 * Load image selected in file picker dialog
 *
 * Currently, web specification not supported the case if the dialog is canceled and no file is selected. In this case,
 * the returned promise will never be resolved.
 *
 * @returns {Promise<HTMLImageElement>} image element
 * @protected
 */
export async function loadImageByDialog(): Promise<HTMLImageElement> {
    if (navigator.userAgent.match(/Chrome|Firefox/)) {
        /* OK */
    } else {
        throw Error('This browser does not support opening File-Picker-Dialog programmatically.');
    }

    let input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';

    return new Promise<HTMLImageElement>((resolve) => {
        input.onchange = () => resolve(loadImageFromFileInput(input));
        input.click();
    });
}
