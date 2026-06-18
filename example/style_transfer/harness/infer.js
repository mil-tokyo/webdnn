// WebDNN は UMD グローバル（dist/webdnn.js）として window.WebDNN に存在する前提。
const W = () => window.WebDNN;

/** Drawable(video/img/canvas) を size×size で画風変換し canvas へ描画。推論msを返す。 */
export async function stylize(runner, drawable, size, canvas, { cropBorder = 0 } = {}) {
  const wd = W();
  const arr = await wd.Image.getImageArray(drawable, {
    dstW: size, dstH: size,
    color: wd.Image.Color.RGB, order: wd.Image.Order.CHW,
    bias: [0, 0, 0], scale: [1, 1, 1], // 入力は[0,255]そのまま（fast-styleは正規化しない）
  });
  const input = new wd.CPUTensor([1, 3, size, size], "float32", arr);
  const t0 = performance.now();
  const [out] = await runner.run([input]);
  const ms = performance.now() - t0;
  const data = out.data || out.toActual().data;
  canvas.width = size; canvas.height = size;
  wd.Image.setImageArrayToCanvas(data, size, size, canvas, {
    order: wd.Image.Order.CHW,
    srcX: cropBorder, srcY: cropBorder,
    srcW: size - cropBorder * 2, srcH: size - cropBorder * 2,
    dstW: size, dstH: size, // クロップ後に元サイズへ拡大（境界ノイズ除去）
  });
  return ms;
}
