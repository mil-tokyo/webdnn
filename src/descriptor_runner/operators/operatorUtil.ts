import Long from "long";
import { onnx } from "onnx-proto";
import { DataArrayTypes, DataType } from "../interface/core/constants";
import { clipLong, intOrLongToInt, intOrLongToIntVector } from "../util";

function getAttr(
  attribute: onnx.IAttributeProto[],
  name: string
): onnx.IAttributeProto | null {
  for (const attr of attribute) {
    if (attr.name === name) {
      return attr;
    }
  }

  return null;
}

export function getAttrFloat(
  attribute: onnx.IAttributeProto[],
  name: string,
  defaultValue: number
): number {
  const attr = getAttr(attribute, name);
  if (!attr) {
    return defaultValue;
  }
  const v = attr.f;
  if (v == null) {
    throw new Error(`Attribute ${name} is not float`);
  }
  return v;
}

export function getAttrInt(
  attribute: onnx.IAttributeProto[],
  name: string,
  defaultValue: number
): number {
  const attr = getAttr(attribute, name);
  if (!attr) {
    return defaultValue;
  }
  const v = attr.i;
  if (v == null) {
    throw new Error(`Attribute ${name} is not int`);
  }
  return intOrLongToInt(v);
}

export function getAttrInts(
  attribute: onnx.IAttributeProto[],
  name: string,
  defaultValue: number[]
): number[] {
  const attr = getAttr(attribute, name);
  if (!attr) {
    return defaultValue;
  }
  const v = attr.ints;
  if (v == null) {
    throw new Error(`Attribute ${name} is not int`);
  }
  return intOrLongToIntVector(v);
}

export function getAttrTensor(
  attribute: onnx.IAttributeProto[],
  name: string
): { data: DataArrayTypes; dataType: DataType; dims: number[] } | null {
  const attr = getAttr(attribute, name);
  if (!attr) {
    return null;
  }
  const v = attr.t;
  if (v == null) {
    throw new Error(`Attribute ${name} is not int`);
  }
  // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
  const dims = intOrLongToIntVector(v.dims!);
  const rawData = v.rawData;
  if (!rawData) {
    throw new Error(`rawData in TensorProto is empty`);
  }
  switch (v.dataType) {
    case onnx.TensorProto.DataType.FLOAT: {
      const data = new Uint8Array(rawData.length);
      data.set(rawData);
      const ab = new Float32Array(
        data.buffer,
        0,
        data.length / Float32Array.BYTES_PER_ELEMENT
      );
      return { dims, dataType: "float32", data: ab };
    }
    case onnx.TensorProto.DataType.INT64: {
      // 1要素が8byte (int64)
      const view = new DataView(
        rawData.buffer,
        rawData.byteOffset,
        rawData.byteLength
      );
      const ab = new Int32Array(view.byteLength / 8);
      for (let idx = 0; idx < ab.length; idx++) {
        ab[idx] = clipLong(
          new Long(
            view.getUint32(idx * 8, true),
            view.getUint32(idx * 8 + 4, true)
          )
        );
      }
      return { dims, dataType: "int32", data: ab };
    }
    default:
      throw new Error(`dataType ${v.dataType} of TensorProto is not supported`);
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
  vec2: ArrayLike<number>
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

export function calcStrides(dims: number[]): number[] {
  const strides = [];
  let length = 1;
  for (let i = dims.length - 1; i >= 0; i--) {
    strides.unshift(length);
    length *= dims[i];
  }
  return strides;
}

export function broadcastUni(
  dimsA: ReadonlyArray<number>,
  dimsB: ReadonlyArray<number>
): number[] {
  // 行列Bを行列Aのshapeに合うようにbroadcast
  // 行列Bのstridesを返す

  if (dimsA.length < dimsB.length) {
    throw new Error(`Unidirectional broadcast error: ${dimsA}, ${dimsB}`);
  }
  // step1 次元数が合うように先頭に1を付加
  const expandedDimsB = dimsB.slice();
  while (expandedDimsB.length < dimsA.length) {
    expandedDimsB.unshift(1);
  }
  const stridesB = calcStrides(expandedDimsB);
  // step2 行列Bの次元サイズが1の箇所はstrideを0にする
  for (let i = 0; i < dimsA.length; i++) {
    if (dimsA[i] !== expandedDimsB[i]) {
      if (expandedDimsB[i] === 1) {
        // broadcast
        stridesB[i] = 0;
      } else {
        throw new Error(`Unidirectional broadcast error: ${dimsA}, ${dimsB}`);
      }
    }
  }

  return stridesB;
}

export function broadcastMulti(allDims: ReadonlyArray<number>[]): {
  dims: number[];
  allStrides: number[][];
} {
  // 全行列をbroadcast
  const expandedNdims = Math.max(...allDims.map((dims) => dims.length));
  // step1 次元数が合うように先頭に1を付加
  const expandedAllDims = allDims.map((dims) => {
    const expandedDims = dims.slice();
    while (expandedDims.length < expandedNdims) {
      expandedDims.unshift(1);
    }
    return expandedDims;
  });
  const expandedDims: number[] = [];
  for (let i = 0; i < expandedNdims; i++) {
    expandedDims.push(Math.max(...expandedAllDims.map((ad) => ad[i])));
  }
  // step2 行列の次元サイズが1の箇所はstrideを0にする
  const allStrides = expandedAllDims.map((dims) => {
    const strides = calcStrides(dims);
    for (let i = 0; i < expandedNdims; i++) {
      if (dims[i] !== expandedDims[i]) {
        if (dims[i] === 1) {
          strides[i] = 0;
        } else {
          throw new Error(`Multidirectional broadcasting error: ${allDims}`);
        }
      }
    }
    return strides;
  });

  return { dims: expandedDims, allStrides };
}
