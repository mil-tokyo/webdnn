import { onnx } from "onnx-proto";
import { Backend } from "../../interface/core/constants";
import { OperatorImpl } from "../operatorImpl";
import { getAttrFloat, getAttrInt } from "../operatorUtil";

// Version 13
export abstract class Gemm extends OperatorImpl {
  alpha!: number;

  beta!: number;

  transA!: number;

  transB!: number;

  constructor(backend: Backend) {
    super(backend);
  }

  initialize(attribute: onnx.IAttributeProto[]): void {
    super.initialize(attribute);
    this.alpha = getAttrFloat(attribute, "alpha", 1.0);
    this.beta = getAttrFloat(attribute, "beta", 1.0);
    this.transA = getAttrInt(attribute, "transA", 0);
    this.transB = getAttrInt(attribute, "transB", 0);
  }

  calcShape(dimsA: ReadonlyArray<number>, dimsB: ReadonlyArray<number>) {
    let k: number,
      kcheck: number,
      m: number,
      n: number,
      strideA: number[],
      strideB: number[];
    if (dimsA.length !== 2 || dimsB.length !== 2) {
      throw new Error();
    }
    if (this.transA) {
      k = dimsA[0];
      m = dimsA[1];
      strideA = [1, m];
    } else {
      m = dimsA[0];
      k = dimsA[1];
      strideA = [k, 1];
    }
    if (this.transB) {
      n = dimsB[0];
      kcheck = dimsB[1];
      strideB = [1, kcheck];
    } else {
      kcheck = dimsB[0];
      n = dimsB[1];
      strideB = [n, 1];
    }
    if (k !== kcheck) {
      throw new Error();
    }

    return { m, n, k, strideA, strideB };
  }
}
