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
    const newData = new DataArrayConstructor[input.dataType](input.data.length);
    const op = this.op;
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
      opType: "Ceil",
      backend: "cpu",
      opsetMin: 1,
      factory: () => new CPUUnary((value) => Math.ceil(value), ["float32"]),
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
      opType: "Relu",
      backend: "cpu",
      opsetMin: 1,
      factory: () =>
        new CPUUnary((value) => Math.max(value, 0), ["float32", "int32"]),
    },
    {
      opType: "Sigmoid",
      backend: "cpu",
      opsetMin: 1,
      factory: () =>
        new CPUUnary((value) => (Math.tanh(value / 2) + 1) / 2, ["float32"]),
    },
    {
      opType: "Sqrt",
      backend: "cpu",
      opsetMin: 1,
      factory: () => new CPUUnary((value) => Math.sqrt(value), ["float32"]),
    },
    {
      opType: "Tanh",
      backend: "cpu",
      opsetMin: 1,
      factory: () => new CPUUnary((value) => Math.tanh(value), ["float32"]),
    },
  ];
}
