import Long from "long";

export function nonnull<T>(value: T | null | undefined): T {
  if (value != null) {
    return value;
  }
  throw new Error("value is null");
}

export function arange(stop: number): number[];
export function arange(start: number, stop: number): number[];
export function arange(start: number, stop: number, step: number): number[];
export function arange(start: number, stop?: number, step = 1): number[] {
  if (stop == null) {
    const len = start;
    const array = new Array(len);
    for (let i = 0; i < len; i++) {
      array[i] = i;
    }
    return array;
  } else {
    const array: number[] = [];
    if (step > 0) {
      for (let i = start; i < stop; i += step) {
        array.push(i);
      }
    } else {
      for (let i = start; i > stop; i += step) {
        array.push(i);
      }
    }
    return array;
  }
}

export function arraySum(vec: ArrayLike<number>): number {
  let x = 0;
  for (let i = 0; i < vec.length; i++) {
    x += vec[i];
  }
  return x;
}

export function arrayProd(vec: ArrayLike<number>): number {
  let x = 1;
  for (let i = 0; i < vec.length; i++) {
    x *= vec[i];
  }
  return x;
}

export function arrayEqual(
  vec1: ArrayLike<number>,
  vec2: ArrayLike<number>,
): boolean {
  if (vec1.length !== vec2.length) {
    return false;
  }

  for (let i = 0; i < vec1.length; i++) {
    if (vec1[i] !== vec2[i]) {
      return false;
    }
  }

  return true;
}

const longPositive32BitMax = new Long(0x7fffffff, 0),
  longPositive32BitMin = new Long(0x80000000, 0xffffffff);

// 符号付きLongを丸めて、-2^31から2^31-1の範囲のnumberを返す
export function clipLong(v: Long): number {
  // Long(0xfffffff6, 0xffffffff) => -10
  if (v.lessThan(longPositive32BitMin)) {
    return -0x80000000;
  } else if (v.greaterThan(longPositive32BitMax)) {
    return 0x7fffffff;
  }
  return v.toNumber();
}

export function intOrLongToInt(v: number | Long): number {
  if (typeof v === "number") {
    return v;
  }
  if (v instanceof Long) {
    return clipLong(v);
  }
  // protobufjs may build Long instances from a different copy of the `long`
  // package, so `instanceof Long` can be false for a genuine Long. In that case
  // the value would pass through unconverted and `number + Long` would
  // string-concatenate downstream (e.g. Conv `pads` -> corrupted output shape).
  // Reconstruct a local Long from its bit fields so clipLong() works.
  const l = v as unknown as { low: number; high: number; unsigned?: boolean };
  if (l && typeof l.low === "number" && typeof l.high === "number") {
    return clipLong(Long.fromBits(l.low, l.high, Boolean(l.unsigned)));
  }
  return Number(v);
}

export function intOrLongToIntVector(v: (number | Long)[]): number[] {
  return v.map(intOrLongToInt);
}
