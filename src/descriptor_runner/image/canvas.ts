/**
 * @module webdnn/image
 */
/** Don't Remove This comment block */

/**
 * Get canvas rendering context and check whether it is nonnull value.
 *
 * @param {CanvasRenderingContext2D} canvas
 * @protected
 */
export function getContext2D(
  canvas: HTMLCanvasElement
): CanvasRenderingContext2D {
  const context = canvas.getContext("2d");
  if (!context) throw Error("CanvasRenderingContext2D initialization failed");

  return context as CanvasRenderingContext2D;
}
