import { onnx } from "onnx-proto";
import { OperatorImpl } from "../../../operatorImpl";
import { getAttrInt, getAttrInts } from "../../../operatorUtil";
import { WebDNNCPUContext } from "../../../../interface/backend/cpu/cpuContext";
import { Tensor } from "../../../../interface/core/tensor";
import { OperatorEntry } from "../../../../interface/core/operator";
import {
  DataArrayConstructor,
  DataArrayTypes,
} from "../../../../interface/core/constants";
import { arrayProd } from "../../../../util";
import { CPUTensor } from "../../../../interface/backend/cpu/cpuTensor";

// Opset 1
abstract class ReduceOp extends OperatorImpl {
  axes!: number[];

  keepdims!: boolean;

  constructor(
    private opType: string,
    private opNotFinalAxis: (
      dI: DataArrayTypes,
      dO: DataArrayTypes,
      outerLength: number,
      innerLength: number,
      reductionLength: number
    ) => void,
    private opFinalAxis?: (
      dI: DataArrayTypes,
      dO: DataArrayTypes,
      outerLength: number,
      innerLength: number,
      reductionLength: number,
      totalReductionLength: number
    ) => void
  ) {
    super("cpu");
  }

  protected async runCore(
    context: WebDNNCPUContext,
    input: CPUTensor,
    sortedAxes: number[]
  ): Promise<Tensor[]> {
    let lastOutputData = input.data;
    let lastShape = input.dims;
    let totalReductionLength = 1;
    for (let i = 0; i < sortedAxes.length; i++) {
      const axis = sortedAxes[i];
      const newShape = lastShape.slice();
      newShape[axis] = 1;
      const reductionLength = lastShape[axis];
      totalReductionLength *= reductionLength;
      const outerLength = arrayProd(lastShape.slice(0, axis));
      const innerLength = arrayProd(lastShape.slice(axis + 1));
      const newOutputData = new DataArrayConstructor[input.dataType](
        outerLength * innerLength
      );
      if (i < sortedAxes.length - 1) {
        this.opNotFinalAxis(
          lastOutputData,
          newOutputData,
          outerLength,
          innerLength,
          reductionLength
        );
      } else {
        if (this.opFinalAxis) {
          this.opFinalAxis(
            lastOutputData,
            newOutputData,
            outerLength,
            innerLength,
            reductionLength,
            totalReductionLength
          );
        } else {
          this.opNotFinalAxis(
            lastOutputData,
            newOutputData,
            outerLength,
            innerLength,
            reductionLength
          );
        }
      }
      lastOutputData = newOutputData;
      lastShape = newShape;
    }
    let finalShape: ReadonlyArray<number>;
    if (this.keepdims) {
      finalShape = lastShape;
    } else {
      finalShape = lastShape.filter((_, i) => !sortedAxes.includes(i));
    }
    const output = context.emptyTensor(
      finalShape,
      input.dataType,
      lastOutputData
    );
    return [output];
  }
}

class ReduceOp1 extends ReduceOp {
  axes!: number[];
  keepdims!: boolean;

  initialize(attribute: onnx.IAttributeProto[]): void {
    super.initialize(attribute);
    this.axes = getAttrInts(attribute, "axes", []);
    this.keepdims = getAttrInt(attribute, "keepdims", 1) !== 0;
  }

  async run(context: WebDNNCPUContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsCPUTensorArray(inputs);
    const input = inputs[0];
    let sortedAxes: number[];
    if (this.axes.length > 0) {
      sortedAxes = this.axes.map((a) => (a >= 0 ? a : input.ndim + a));
      sortedAxes.sort((a, b) => a - b);
    } else {
      sortedAxes = [];
      for (let i = 0; i < input.ndim; i++) {
        sortedAxes.push(i);
      }
    }

    return this.runCore(context, input, sortedAxes);
  }
}

// Only ReduceSum has backward-incompatible opset 13
class ReduceSum13 extends ReduceOp {
  keepdims!: boolean;
  noopWithEmptyAxes!: boolean;

  initialize(attribute: onnx.IAttributeProto[]): void {
    super.initialize(attribute);
    this.keepdims = getAttrInt(attribute, "keepdims", 1) !== 0;
    this.noopWithEmptyAxes =
      getAttrInt(attribute, "noop_with_empty_axes", 0) !== 0;
  }

  async run(context: WebDNNCPUContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsCPUTensorArray(inputs);
    const input = inputs[0],
      axes = inputs[1];
    let sortedAxes: number[];
    if (axes.length > 0) {
      sortedAxes = Array.from(axes.data).map((a) =>
        a >= 0 ? a : input.ndim + a
      );
      sortedAxes.sort((a, b) => a - b);
    } else {
      sortedAxes = [];
      if (!this.noopWithEmptyAxes) {
        for (let i = 0; i < input.ndim; i++) {
          sortedAxes.push(i);
        }
      }
    }

    return this.runCore(context, input, sortedAxes);
  }
}

export function getOpEntries(): OperatorEntry[] {
  const opEntries: OperatorEntry[] = [];
  const addOps = (
    opType: string,
    opNotFinalAxis: (
      dI: DataArrayTypes,
      dO: DataArrayTypes,
      outerLength: number,
      innerLength: number,
      reductionLength: number
    ) => void,
    opFinalAxis?: (
      dI: DataArrayTypes,
      dO: DataArrayTypes,
      outerLength: number,
      innerLength: number,
      reductionLength: number,
      totalReductionLength: number
    ) => void,
    reduceSum13?: boolean
  ) => {
    opEntries.push({
      opType: opType,
      backend: "cpu",
      opsetMin: 1,
      opsetMax: reduceSum13 ? 13 : undefined,
      factory: () => new ReduceOp1(opType, opNotFinalAxis, opFinalAxis),
    });
    if (reduceSum13) {
      opEntries.push({
        opType: opType,
        backend: "cpu",
        opsetMin: 13,
        factory: () => new ReduceSum13(opType, opNotFinalAxis, opFinalAxis),
      });
    }
  };
  addOps(
    "ReduceL1",
    (
      dI: DataArrayTypes,
      dO: DataArrayTypes,
      outerLength: number,
      innerLength: number,
      reductionLength: number
    ): void => {
      for (let outer = 0; outer < outerLength; outer++) {
        for (let inner = 0; inner < innerLength; inner++) {
          let s = 0;
          for (let r = 0; r < reductionLength; r++) {
            s += Math.abs(
              dI[(outer * reductionLength + r) * innerLength + inner]
            );
          }
          dO[outer * innerLength + inner] = s;
        }
      }
    }
  );
  addOps(
    "ReduceL2",
    (
      dI: DataArrayTypes,
      dO: DataArrayTypes,
      outerLength: number,
      innerLength: number,
      reductionLength: number
    ): void => {
      for (let outer = 0; outer < outerLength; outer++) {
        for (let inner = 0; inner < innerLength; inner++) {
          let s = 0;
          for (let r = 0; r < reductionLength; r++) {
            const v = dI[(outer * reductionLength + r) * innerLength + inner];
            s += v * v;
          }
          dO[outer * innerLength + inner] = s;
        }
      }
    },
    (
      dI: DataArrayTypes,
      dO: DataArrayTypes,
      outerLength: number,
      innerLength: number,
      reductionLength: number
    ): void => {
      for (let outer = 0; outer < outerLength; outer++) {
        for (let inner = 0; inner < innerLength; inner++) {
          let s = 0;
          for (let r = 0; r < reductionLength; r++) {
            const v = dI[(outer * reductionLength + r) * innerLength + inner];
            s += v * v;
          }
          dO[outer * innerLength + inner] = Math.sqrt(s);
        }
      }
    }
  );
  addOps(
    "ReduceLogSum",
    (
      dI: DataArrayTypes,
      dO: DataArrayTypes,
      outerLength: number,
      innerLength: number,
      reductionLength: number
    ): void => {
      for (let outer = 0; outer < outerLength; outer++) {
        for (let inner = 0; inner < innerLength; inner++) {
          let s = 0;
          for (let r = 0; r < reductionLength; r++) {
            s += dI[outer * reductionLength + r];
          }
          dO[outer * innerLength + inner] = s;
        }
      }
    },
    (
      dI: DataArrayTypes,
      dO: DataArrayTypes,
      outerLength: number,
      innerLength: number,
      reductionLength: number
    ): void => {
      for (let outer = 0; outer < outerLength; outer++) {
        for (let inner = 0; inner < innerLength; inner++) {
          let s = 0;
          for (let r = 0; r < reductionLength; r++) {
            s += dI[outer * reductionLength + r];
          }
          dO[outer * innerLength + inner] = Math.log(s);
        }
      }
    }
  );
  addOps(
    "ReduceLogSumExp",
    (
      dI: DataArrayTypes,
      dO: DataArrayTypes,
      outerLength: number,
      innerLength: number,
      reductionLength: number
    ): void => {
      for (let outer = 0; outer < outerLength; outer++) {
        for (let inner = 0; inner < innerLength; inner++) {
          let s = 0;
          for (let r = 0; r < reductionLength; r++) {
            s += Math.exp(
              dI[(outer * reductionLength + r) * innerLength + inner]
            );
          }
          dO[outer * innerLength + inner] = s;
        }
      }
    },
    (
      dI: DataArrayTypes,
      dO: DataArrayTypes,
      outerLength: number,
      innerLength: number,
      reductionLength: number
    ): void => {
      for (let outer = 0; outer < outerLength; outer++) {
        for (let inner = 0; inner < innerLength; inner++) {
          let s = 0;
          for (let r = 0; r < reductionLength; r++) {
            s += Math.exp(
              dI[(outer * reductionLength + r) * innerLength + inner]
            );
          }
          dO[outer * innerLength + inner] = Math.log(s);
        }
      }
    }
  );
  addOps(
    "ReduceMax",
    (
      dI: DataArrayTypes,
      dO: DataArrayTypes,
      outerLength: number,
      innerLength: number,
      reductionLength: number
    ): void => {
      for (let outer = 0; outer < outerLength; outer++) {
        for (let inner = 0; inner < innerLength; inner++) {
          let s = dI[outer * reductionLength * innerLength + inner];
          for (let r = 1; r < reductionLength; r++) {
            const v = dI[(outer * reductionLength + r) * innerLength + inner];
            if (v > s) {
              s = v;
            }
          }
          dO[outer * innerLength + inner] = s;
        }
      }
    }
  );
  addOps(
    "ReduceMean",
    (
      dI: DataArrayTypes,
      dO: DataArrayTypes,
      outerLength: number,
      innerLength: number,
      reductionLength: number
    ): void => {
      for (let outer = 0; outer < outerLength; outer++) {
        for (let inner = 0; inner < innerLength; inner++) {
          let s = 0;
          for (let r = 0; r < reductionLength; r++) {
            s += dI[(outer * reductionLength + r) * innerLength + inner];
          }
          dO[outer * innerLength + inner] = s;
        }
      }
    },

    (
      dI: DataArrayTypes,
      dO: DataArrayTypes,
      outerLength: number,
      innerLength: number,
      reductionLength: number,
      totalReductionLength: number
    ): void => {
      for (let outer = 0; outer < outerLength; outer++) {
        for (let inner = 0; inner < innerLength; inner++) {
          let s = 0;
          for (let r = 0; r < reductionLength; r++) {
            s += dI[(outer * reductionLength + r) * innerLength + inner];
          }
          dO[outer * innerLength + inner] = s / totalReductionLength;
        }
      }
    }
  );
  addOps(
    "ReduceMin",
    (
      dI: DataArrayTypes,
      dO: DataArrayTypes,
      outerLength: number,
      innerLength: number,
      reductionLength: number
    ): void => {
      for (let outer = 0; outer < outerLength; outer++) {
        for (let inner = 0; inner < innerLength; inner++) {
          let s = dI[outer * reductionLength * innerLength + inner];
          for (let r = 1; r < reductionLength; r++) {
            const v = dI[(outer * reductionLength + r) * innerLength + inner];
            if (v < s) {
              s = v;
            }
          }
          dO[outer * innerLength + inner] = s;
        }
      }
    }
  );
  addOps(
    "ReduceProd",
    (
      dI: DataArrayTypes,
      dO: DataArrayTypes,
      outerLength: number,
      innerLength: number,
      reductionLength: number
    ): void => {
      for (let outer = 0; outer < outerLength; outer++) {
        for (let inner = 0; inner < innerLength; inner++) {
          let s = 1;
          for (let r = 0; r < reductionLength; r++) {
            s *= dI[(outer * reductionLength + r) * innerLength + inner];
          }
          dO[outer * innerLength + inner] = s;
        }
      }
    }
  );
  addOps(
    "ReduceSum",
    (
      dI: DataArrayTypes,
      dO: DataArrayTypes,
      outerLength: number,
      innerLength: number,
      reductionLength: number
    ): void => {
      for (let outer = 0; outer < outerLength; outer++) {
        for (let inner = 0; inner < innerLength; inner++) {
          let s = 0;
          for (let r = 0; r < reductionLength; r++) {
            s += dI[(outer * reductionLength + r) * innerLength + inner];
          }
          dO[outer * innerLength + inner] = s;
        }
      }
    },
    undefined,
    true
  );
  addOps(
    "ReduceSumSquare",
    (
      dI: DataArrayTypes,
      dO: DataArrayTypes,
      outerLength: number,
      innerLength: number,
      reductionLength: number
    ): void => {
      for (let outer = 0; outer < outerLength; outer++) {
        for (let inner = 0; inner < innerLength; inner++) {
          let s = 0;
          for (let r = 0; r < reductionLength; r++) {
            const v = dI[(outer * reductionLength + r) * innerLength + inner];
            s += v * v;
          }
          dO[outer * innerLength + inner] = s;
        }
      }
    }
  );
  return opEntries;
}
