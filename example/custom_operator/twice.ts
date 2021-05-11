// Example implementation of custom operator.
import { DataArrayConstructor } from "../../../../interface/core/constants";
import { OperatorImpl } from "../../../operatorImpl";
import { WebDNNCPUContext } from "../../../../interface/backend/cpu/cpuContext";
import { Tensor } from "../../../../interface/core/tensor";
import { OperatorEntry } from "../../../../interface/core/operator";

class Twice extends OperatorImpl {
  constructor() {
    super("cpu");
  }

  async run(context: WebDNNCPUContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsCPUTensorArray(inputs);
    const input = inputs[0];
    // constructs TypedArray (e.g. Float32Array) for output
    const newData = new DataArrayConstructor[input.dataType](input.data.length);
    // computation core
    for (let i = 0; i < newData.length; i++) {
      newData[i] = input.data[i] * 2;
    }
    // create output CPUTensor specifying shape, data type, data
    const output = context.emptyTensor(input.dims, input.dataType, newData);
    return [output];
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "Twice", // ONNX Operator name
      backend: "cpu",
      opsetMin: 1,
      factory: () => new Twice(), // Function to construct operator
    },
  ];
}
