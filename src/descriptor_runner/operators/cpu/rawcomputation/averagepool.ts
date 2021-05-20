export function averagepool(
  dX: Float32Array,
  dI: Float32Array,
  countIncludePad: boolean,
  batch: number,
  kernelShape: number[],
  pads: number[],
  strides: number[],
  inShape: number[],
  outShape: number[],
  ch: number
): void {
  let idx = 0;
  for (let b = 0; b < batch; b++) {
    for (let c = 0; c < ch; c++) {
      for (let oy = 0; oy < outShape[0]; oy++) {
        for (let ox = 0; ox < outShape[1]; ox++) {
          let ctr = 0,
            sum = 0;
          for (let ky = 0; ky < kernelShape[0]; ky++) {
            for (let kx = 0; kx < kernelShape[1]; kx++) {
              const iny = oy * strides[0] - pads[0] + ky,
                inx = ox * strides[1] - pads[1] + kx;
              if (
                iny >= 0 &&
                iny < inShape[0] &&
                inx >= 0 &&
                inx < inShape[1]
              ) {
                const xidx =
                    ((b * ch + c) * inShape[0] + iny) * inShape[1] + inx,
                  v = dX[xidx];
                sum += v;
                ctr++;
              }
            }
          }

          dI[idx++] = countIncludePad
            ? sum / (kernelShape[0] * kernelShape[1])
            : sum / ctr;
        }
      }
    }
  }
}
