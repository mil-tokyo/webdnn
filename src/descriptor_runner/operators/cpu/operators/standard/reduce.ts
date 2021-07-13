import { onnx } from "onnx-proto";
import { OperatorImpl } from "../../../operatorImpl";
import { getAttrInt, getAttrInts } from "../../../operatorUtil";
import { WebDNNCPUContext } from "../../../../interface/backend/cpu/cpuContext";
import { Tensor } from "../../../../interface/core/tensor";
import { OperatorEntry } from "../../../../interface/core/operator";
import { DataArrayTypes } from "../../../../interface/core/constants";

// Opset 1
class ReduceOp extends OperatorImpl {
  axes!: number[];

  keepdims!: boolean;

  constructor(
    private opType: string,
    private op: (
      dI: DataArrayTypes,
      dO: DataArrayTypes,
      outerLength: number,
      reductionLength: number
    ) => void
  ) {
    super("cpu");
  }

  initialize(attribute: onnx.IAttributeProto[]): void {
    super.initialize(attribute);
    this.axes = getAttrInts(attribute, "axes", []);
    this.keepdims = getAttrInt(attribute, "keepdims", 1) !== 0;
  }

  async run(context: WebDNNCPUContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsCPUTensorArray(inputs);
    const input = inputs[0];
    if (this.axes.length !== 1) {
      throw new Error(`${this.opType}: only single axis is supported`);
    }
    let axis = this.axes[0];
    if (axis < 0) {
      axis += input.ndim;
    }
    if (axis !== input.ndim - 1) {
      throw new Error(
        `${this.opType}: currently only reducing final axis is supported`
      );
    }
    // 最終軸のreductionに特化した実装
    const reductionLength = input.dims[axis],
      outerLength = input.length / reductionLength,
      outShape = input.dims.slice();
    if (this.keepdims) {
      outShape[axis] = 1;
    } else {
      outShape.pop();
    }
    const output = context.emptyTensor(outShape, input.dataType),
      dI = input.data,
      dO = output.data;
    this.op(dI, dO, outerLength, reductionLength);
    return [output];
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "ReduceL1",
      backend: "cpu",
      opsetMin: 1,
      factory: () =>
        new ReduceOp(
          "ReduceL1",
          (
            dI: DataArrayTypes,
            dO: DataArrayTypes,
            outerLength: number,
            reductionLength: number
          ): void => {
            for (let outer = 0; outer < outerLength; outer++) {
              let s = 0;
              for (let r = 0; r < reductionLength; r++) {
                s += Math.abs(dI[outer * reductionLength + r]);
              }
              dO[outer] = s;
            }
          }
        ),
    },
    {
      opType: "ReduceL2",
      backend: "cpu",
      opsetMin: 1,
      factory: () =>
        new ReduceOp(
          "ReduceL2",
          (
            dI: DataArrayTypes,
            dO: DataArrayTypes,
            outerLength: number,
            reductionLength: number
          ): void => {
            for (let outer = 0; outer < outerLength; outer++) {
              let s = 0;
              for (let r = 0; r < reductionLength; r++) {
                const v = dI[outer * reductionLength + r];
                s += v * v;
              }
              dO[outer] = Math.sqrt(s);
            }
          }
        ),
    },
    {
      opType: "ReduceLogSum",
      backend: "cpu",
      opsetMin: 1,
      factory: () =>
        new ReduceOp(
          "ReduceLogSum",
          (
            dI: DataArrayTypes,
            dO: DataArrayTypes,
            outerLength: number,
            reductionLength: number
          ): void => {
            for (let outer = 0; outer < outerLength; outer++) {
              let s = 0;
              for (let r = 0; r < reductionLength; r++) {
                s += dI[outer * reductionLength + r];
              }
              dO[outer] = Math.log(s);
            }
          }
        ),
    },
    {
      opType: "ReduceLogSumExp",
      backend: "cpu",
      opsetMin: 1,
      factory: () =>
        new ReduceOp(
          "ReduceLogSumExp",
          (
            dI: DataArrayTypes,
            dO: DataArrayTypes,
            outerLength: number,
            reductionLength: number
          ): void => {
            for (let outer = 0; outer < outerLength; outer++) {
              let s = 0;
              for (let r = 0; r < reductionLength; r++) {
                s += Math.exp(dI[outer * reductionLength + r]);
              }
              dO[outer] = Math.log(s);
            }
          }
        ),
    },
    {
      opType: "ReduceMax",
      backend: "cpu",
      opsetMin: 1,
      factory: () =>
        new ReduceOp(
          "ReduceMax",
          (
            dI: DataArrayTypes,
            dO: DataArrayTypes,
            outerLength: number,
            reductionLength: number
          ): void => {
            for (let outer = 0; outer < outerLength; outer++) {
              let s = dI[outer * reductionLength];
              for (let r = 1; r < reductionLength; r++) {
                const v = dI[outer * reductionLength + r];
                if (v > s) {
                  s = v;
                }
              }
              dO[outer] = s;
            }
          }
        ),
    },
    {
      opType: "ReduceMean",
      backend: "cpu",
      opsetMin: 1,
      factory: () =>
        new ReduceOp(
          "ReduceMean",
          (
            dI: DataArrayTypes,
            dO: DataArrayTypes,
            outerLength: number,
            reductionLength: number
          ): void => {
            for (let outer = 0; outer < outerLength; outer++) {
              let s = 0;
              for (let r = 0; r < reductionLength; r++) {
                s += dI[outer * reductionLength + r];
              }
              dO[outer] = s / reductionLength;
            }
          }
        ),
    },
    {
      opType: "ReduceMin",
      backend: "cpu",
      opsetMin: 1,
      factory: () =>
        new ReduceOp(
          "ReduceMin",
          (
            dI: DataArrayTypes,
            dO: DataArrayTypes,
            outerLength: number,
            reductionLength: number
          ): void => {
            for (let outer = 0; outer < outerLength; outer++) {
              let s = dI[outer * reductionLength];
              for (let r = 1; r < reductionLength; r++) {
                const v = dI[outer * reductionLength + r];
                if (v < s) {
                  s = v;
                }
              }
              dO[outer] = s;
            }
          }
        ),
    },
    {
      opType: "ReduceProd",
      backend: "cpu",
      opsetMin: 1,
      factory: () =>
        new ReduceOp(
          "ReduceProd",
          (
            dI: DataArrayTypes,
            dO: DataArrayTypes,
            outerLength: number,
            reductionLength: number
          ): void => {
            for (let outer = 0; outer < outerLength; outer++) {
              let s = 1;
              for (let r = 0; r < reductionLength; r++) {
                s *= dI[outer * reductionLength + r];
              }
              dO[outer] = s;
            }
          }
        ),
    },
    {
      opType: "ReduceSum",
      backend: "cpu",
      opsetMin: 1,
      factory: () =>
        new ReduceOp(
          "ReduceSum",
          (
            dI: DataArrayTypes,
            dO: DataArrayTypes,
            outerLength: number,
            reductionLength: number
          ): void => {
            for (let outer = 0; outer < outerLength; outer++) {
              let s = 0;
              for (let r = 0; r < reductionLength; r++) {
                s += dI[outer * reductionLength + r];
              }
              dO[outer] = s;
            }
          }
        ),
    },
    {
      opType: "ReduceSumSquare",
      backend: "cpu",
      opsetMin: 1,
      factory: () =>
        new ReduceOp(
          "ReduceSumSquare",
          (
            dI: DataArrayTypes,
            dO: DataArrayTypes,
            outerLength: number,
            reductionLength: number
          ): void => {
            for (let outer = 0; outer < outerLength; outer++) {
              let s = 0;
              for (let r = 0; r < reductionLength; r++) {
                const v = dI[outer * reductionLength + r];
                s += v * v;
              }
              dO[outer] = s;
            }
          }
        ),
    },
  ];
}
