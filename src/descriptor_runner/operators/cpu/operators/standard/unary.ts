import {
  DataArrayConstructor,
  DataType,
} from "../../../../interface/core/constants";
import { OperatorImpl } from "../../../operatorImpl";
import { WebDNNCPUContext } from "../../../../interface/backend/cpu/cpuContext";
import { Tensor } from "../../../../interface/core/tensor";
import { OperatorEntry } from "../../../../interface/core/operator";

class CPUUnary extends OperatorImpl {
  constructor(
    private op: (value: number) => number,
    private allowDataTypes: DataType[]
  ) {
    super("cpu");
  }

  async run(context: WebDNNCPUContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsCPUTensorArray(inputs);
    const input = inputs[0];
    if (!this.allowDataTypes.includes(input.dataType)) {
      throw new Error(`Unary: DataType ${input.dataType} not supported`);
    }
    const newData = new DataArrayConstructor[input.dataType](input.data.length),
      { op } = this;
    for (let i = 0; i < newData.length; i++) {
      newData[i] = op(input.data[i]);
    }
    const output = context.emptyTensor(input.dims, input.dataType, newData);
    return [output];
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "Abs",
      backend: "cpu",
      opsetMin: 1,
      factory: () =>
        new CPUUnary((value) => Math.abs(value), ["float32", "int32"]),
    },
    {
      opType: "Acos",
      backend: "cpu",
      opsetMin: 1,
      factory: () => new CPUUnary((value) => Math.acos(value), ["float32"]),
    },
    {
      opType: "Acosh",
      backend: "cpu",
      opsetMin: 1,
      factory: () => new CPUUnary((value) => Math.acosh(value), ["float32"]),
    },
    {
      opType: "Asin",
      backend: "cpu",
      opsetMin: 1,
      factory: () => new CPUUnary((value) => Math.asin(value), ["float32"]),
    },
    {
      opType: "Asinh",
      backend: "cpu",
      opsetMin: 1,
      factory: () => new CPUUnary((value) => Math.asinh(value), ["float32"]),
    },
    {
      opType: "Atan",
      backend: "cpu",
      opsetMin: 1,
      factory: () => new CPUUnary((value) => Math.atan(value), ["float32"]),
    },
    {
      opType: "Atanh",
      backend: "cpu",
      opsetMin: 1,
      factory: () => new CPUUnary((value) => Math.atanh(value), ["float32"]),
    },
    {
      opType: "Ceil",
      backend: "cpu",
      opsetMin: 1,
      factory: () => new CPUUnary((value) => Math.ceil(value), ["float32"]),
    },
    {
      opType: "Cos",
      backend: "cpu",
      opsetMin: 1,
      factory: () => new CPUUnary((value) => Math.cos(value), ["float32"]),
    },
    {
      opType: "Cosh",
      backend: "cpu",
      opsetMin: 1,
      factory: () => new CPUUnary((value) => Math.cosh(value), ["float32"]),
    },
    {
      opType: "Exp",
      backend: "cpu",
      opsetMin: 1,
      factory: () => new CPUUnary((value) => Math.exp(value), ["float32"]),
    },
    {
      opType: "Floor",
      backend: "cpu",
      opsetMin: 1,
      factory: () => new CPUUnary((value) => Math.floor(value), ["float32"]),
    },
    {
      opType: "HardSwish",
      backend: "cpu",
      opsetMin: 1,
      factory: () =>
        new CPUUnary(
          (value) => {
            if (value <= -3) {
              return 0;
            } else if (value >= 3) {
              return value;
            } else {
              return (value * (value + 3)) / 6;
            }
          },
          ["float32"]
        ),
    },
    {
      opType: "Log",
      backend: "cpu",
      opsetMin: 1,
      factory: () => new CPUUnary((value) => Math.log(value), ["float32"]),
    },
    {
      opType: "Neg",
      backend: "cpu",
      opsetMin: 1,
      factory: () => new CPUUnary((value) => -value, ["float32", "int32"]),
    },
    {
      opType: "Reciprocal",
      backend: "cpu",
      opsetMin: 1,
      factory: () => new CPUUnary((value) => 1 / value, ["float32"]),
    },
    {
      opType: "Relu",
      backend: "cpu",
      opsetMin: 1,
      factory: () =>
        new CPUUnary((value) => Math.max(value, 0), ["float32", "int32"]),
    },
    {
      opType: "Round",
      backend: "cpu",
      opsetMin: 1,
      factory: () => new CPUUnary((value) => Math.round(value), ["float32"]),
    },
    {
      opType: "Sigmoid",
      backend: "cpu",
      opsetMin: 1,
      factory: () =>
        new CPUUnary((value) => (Math.tanh(value / 2) + 1) / 2, ["float32"]),
    },
    {
      opType: "Sign",
      backend: "cpu",
      opsetMin: 1,
      factory: () =>
        new CPUUnary((value) => Math.sign(value), ["float32", "int32"]),
    },
    {
      opType: "Sin",
      backend: "cpu",
      opsetMin: 1,
      factory: () => new CPUUnary((value) => Math.sin(value), ["float32"]),
    },
    {
      opType: "Softplus",
      backend: "cpu",
      opsetMin: 1,
      factory: () =>
        new CPUUnary((value) => Math.log(Math.exp(value) + 1), ["float32"]),
    },
    {
      opType: "Softsign",
      backend: "cpu",
      opsetMin: 1,
      factory: () =>
        new CPUUnary((value) => value / (1 + Math.abs(value)), ["float32"]),
    },
    {
      opType: "Sqrt",
      backend: "cpu",
      opsetMin: 1,
      factory: () => new CPUUnary((value) => Math.sqrt(value), ["float32"]),
    },
    {
      opType: "Tan",
      backend: "cpu",
      opsetMin: 1,
      factory: () => new CPUUnary((value) => Math.tan(value), ["float32"]),
    },
    {
      opType: "Tanh",
      backend: "cpu",
      opsetMin: 1,
      factory: () => new CPUUnary((value) => Math.tanh(value), ["float32"]),
    },
  ];
}
