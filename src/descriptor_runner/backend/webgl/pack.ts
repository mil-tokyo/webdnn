export function packToFloat32Array(
  src: ArrayLike<number>,
  length: number
): Float32Array {
  const buffer = new Float32Array(length);
  buffer.set(src);
  return buffer;
}

export function packToFloat16Array(
  src: ArrayLike<number>,
  length: number
): Uint16Array {
  const srcLength = src.length;
  let srcUInt32: Uint32Array;
  if (src instanceof Float32Array) {
    srcUInt32 = new Uint32Array(src.buffer, src.byteOffset, srcLength);
  } else {
    const srcFloat32 = new Float32Array(srcLength);
    srcFloat32.set(src);
    srcUInt32 = new Uint32Array(srcFloat32.buffer);
  }

  const buffer = new Uint16Array(length);
  for (let i = 0; i < srcLength; i++) {
    const x = srcUInt32[i];
    // 非正規化数, NaNは不正確
    let exp = ((x >> 13) & 0x3fc00) - 0x1c000;
    if (exp < 0) {
      exp = 0;
    } else if (exp > 0x7c00) {
      exp = 0x7c00;
    }
    const packed = ((x >> 16) & 0x8000) | exp | ((x >> 13) & 0x3ff);
    buffer[i] = packed;
  }
  return buffer;
}

export function packToInt32Array(
  src: ArrayLike<number>,
  length: number
): Int32Array {
  const buffer = new Int32Array(length);
  buffer.set(src);
  return buffer;
}

export function packToUint8Array(
  src: ArrayLike<number>,
  length: number
): Uint8Array {
  const buffer = new Uint8Array(length);
  buffer.set(src);
  return buffer;
}

export function unpackFromFloat32Array(
  src: Float32Array,
  length: number
): Float32Array {
  const buffer = new Float32Array(length);
  const srcView = new Float32Array(src.buffer, src.byteOffset, length);
  buffer.set(srcView);
  return buffer;
}

export function unpackFromFloat16Array(
  src: Uint16Array,
  length: number
): Float32Array {
  const buffer = new Float32Array(length);
  const bufferUInt32 = new Uint32Array(buffer.buffer);
  for (let i = 0; i < length; i++) {
    const h = src[i];
    let exp = ((h << 13) & 0xf800000) + 0x38000000;
    if (exp === 0x38000000) {
      // 0
      exp = 0;
    } else if (exp === 0x47800000) {
      // inf
      exp = 0x7f800000;
    }
    const unpacked = ((h << 16) & 0x80000000) | exp | ((h & 0x3ff) << 13);
    bufferUInt32[i] = unpacked;
  }
  return buffer;
}

export function unpackFromInt32Array(
  src: Int32Array,
  length: number
): Int32Array {
  const buffer = new Int32Array(length);
  const srcView = new Int32Array(src.buffer, src.byteOffset, length);
  buffer.set(srcView);
  return buffer;
}

export function unpackFromUint8Array(
  src: Uint8Array,
  length: number
): Uint8Array {
  const buffer = new Uint8Array(length);
  const srcView = new Uint8Array(src.buffer, src.byteOffset, length);
  buffer.set(srcView);
  return buffer;
}
