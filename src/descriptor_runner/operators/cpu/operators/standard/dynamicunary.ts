import { onnx } from "onnx-proto";
import {
  DataArrayConstructor,
  DataType,
} from "../../../../interface/core/constants";
import { OperatorImpl } from "../../../operatorImpl";
import { WebDNNCPUContext } from "../../../../interface/backend/cpu/cpuContext";
import { Tensor } from "../../../../interface/core/tensor";
import { OperatorEntry } from "../../../../interface/core/operator";
import { getAttrFloat } from "../../../operatorUtil";

abstract class DynamicUnary extends OperatorImpl {
  constructor(public opType: string, private allowDataTypes: DataType[]) {
    super("cpu");
  }

  protected abstract getUnaryOp(): (value: number) => number;

  async run(context: WebDNNCPUContext, inputs: Tensor[]): Promise<Tensor[]> {
    context.assertsCPUTensorArray(inputs);
    const input = inputs[0];
    if (!this.allowDataTypes.includes(input.dataType)) {
      throw new Error(
        `${this.opType}: DataType ${input.dataType} not supported`
      );
    }
    const newData = new DataArrayConstructor[input.dataType](input.data.length),
      op = this.getUnaryOp();
    for (let i = 0; i < newData.length; i++) {
      newData[i] = op(input.data[i]);
    }
    const output = context.emptyTensor(input.dims, input.dataType, newData);
    return [output];
  }
}

class Elu extends DynamicUnary {
  alpha!: number;

  constructor() {
    super("Elu", ["float32"]);
  }

  initialize(attribute: onnx.IAttributeProto[]): void {
    super.initialize(attribute);
    this.alpha = getAttrFloat(attribute, "alpha", 1.0);
  }

  getUnaryOp(): (value: number) => number {
    const alpha = this.alpha;
    return (value: number) => {
      return value >= 0 ? value : (Math.exp(value) - 1) * alpha;
    };
  }
}

class HardSigmoid extends DynamicUnary {
  alpha!: number;
  beta!: number;

  constructor() {
    super("HardSigmoid", ["float32"]);
  }

  initialize(attribute: onnx.IAttributeProto[]): void {
    super.initialize(attribute);
    this.alpha = getAttrFloat(attribute, "alpha", 0.2);
    this.beta = getAttrFloat(attribute, "beta", 0.5);
  }

  getUnaryOp(): (value: number) => number {
    const alpha = this.alpha;
    const beta = this.beta;
    return (value: number) => {
      return Math.max(0, Math.min(1, value * alpha + beta));
    };
  }
}

class LeakyRelu extends DynamicUnary {
  alpha!: number;

  constructor() {
    super("LeakyRelu", ["float32"]);
  }

  initialize(attribute: onnx.IAttributeProto[]): void {
    super.initialize(attribute);
    this.alpha = getAttrFloat(attribute, "alpha", 0.01);
  }

  getUnaryOp(): (value: number) => number {
    const alpha = this.alpha;
    return (value: number) => {
      return value >= 0 ? value : value * alpha;
    };
  }
}

class Selu extends DynamicUnary {
  alpha!: number;
  gamma!: number;

  constructor() {
    super("Selu", ["float32"]);
  }

  initialize(attribute: onnx.IAttributeProto[]): void {
    super.initialize(attribute);
    this.alpha = getAttrFloat(
      attribute,
      "alpha",
      1.6732632423543772848170429916717
    );
    this.gamma = getAttrFloat(
      attribute,
      "gamma",
      1.0507009873554804934193349852946
    );
  }

  getUnaryOp(): (value: number) => number {
    const alpha = this.alpha;
    const gamma = this.gamma;
    return (value: number) => {
      return value > 0
        ? gamma * value
        : gamma * (alpha * Math.exp(value) - alpha);
    };
  }
}

class ThresholdedRelu extends DynamicUnary {
  alpha!: number;

  constructor() {
    super("ThresholdedRelu", ["float32"]);
  }

  initialize(attribute: onnx.IAttributeProto[]): void {
    super.initialize(attribute);
    this.alpha = getAttrFloat(attribute, "alpha", 1.0);
  }

  getUnaryOp(): (value: number) => number {
    const alpha = this.alpha;
    return (value: number) => {
      return value > alpha ? value : 0;
    };
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "Elu",
      backend: "cpu",
      opsetMin: 1,
      factory: () => new Elu(),
    },
    {
      opType: "HardSigmoid",
      backend: "cpu",
      opsetMin: 1,
      factory: () => new HardSigmoid(),
    },
    {
      opType: "LeakyRelu",
      backend: "cpu",
      opsetMin: 1,
      factory: () => new LeakyRelu(),
    },
    {
      opType: "Selu",
      backend: "cpu",
      opsetMin: 1,
      factory: () => new Selu(),
    },
    {
      opType: "ThresholdedRelu",
      backend: "cpu",
      opsetMin: 1,
      factory: () => new ThresholdedRelu(),
    },
  ];
}
