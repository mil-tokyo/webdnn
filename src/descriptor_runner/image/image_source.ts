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
  const image = document.createElement("img");

  return new Promise((resolve, reject) => {
    image.onload = resolve;
    image.onerror = reject;
    image.src = url;
  }).then(() => image);
}

/* istanbul ignore next */
/**
 * Load image file selected in `<input type="file">` element.
 *
 * @param {HTMLInputElement} input the `<input type="file">` element
 * @returns {Promise<HTMLImageElement>} image element
 */
export async function loadImageFromFileInput(
  input: HTMLInputElement
): Promise<HTMLImageElement> {
  const files = input.files;
  if (!files || files.length == 0) throw new Error("No file is selected");

  const url = URL.createObjectURL(files[0]);

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
  const input = document.createElement("input");
  input.style.display = "none";
  input.type = "file";
  input.accept = "image/*";
  // avoid GC for iOS Safari
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  (window as any)._webdnn_image_input = input;

  return new Promise<HTMLImageElement>((resolve) => {
    input.onchange = () => {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      delete (window as any)._webdnn_image_input;
      resolve(loadImageFromFileInput(input));
    };
    input.click();
  });
}
