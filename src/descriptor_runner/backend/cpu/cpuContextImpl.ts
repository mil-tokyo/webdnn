import { CPUTensor } from "../..";
import { WebDNNCPUContext } from "../../interface/backend/cpu/cpuContext";
import { DataArrayTypes, DataType } from "../../interface/core/constants";
import { Tensor } from "../../interface/core/tensor";
import { CPUTensorImpl } from "./cpuTensorImpl";

export class WebDNNCPUContextImpl implements WebDNNCPUContext {
  backend = "cpu" as const;
  async initialize(): Promise<void> {
    return;
  }
  isCPUTensor(tensor: Tensor): tensor is CPUTensor {
    return tensor.backend === this.backend;
  }
  assertsCPUTensor(tensor: Tensor): asserts tensor is CPUTensor {
    if (tensor.backend !== this.backend) {
      throw new Error(
        `Tensor backend ${this.backend} is expected, but ${tensor.backend} is given.`
      );
    }
  }
  assertsCPUTensorArray(tensors: Tensor[]): asserts tensors is CPUTensor[] {
    for (const tensor of tensors) {
      if (tensor.backend !== this.backend) {
        throw new Error(
          `Tensor backend ${this.backend} is expected, but ${tensor.backend} is given.`
        );
      }
    }
  }
  emptyTensor(
    dims: ReadonlyArray<number>,
    dataType?: DataType,
    data?: DataArrayTypes
  ): CPUTensor {
    return new CPUTensorImpl(dims, dataType, data);
  }
  async moveTensor(tensor: Tensor): Promise<CPUTensor> {
    const dst = new CPUTensorImpl(
      tensor.dims,
      tensor.dataType,
      await tensor.getData()
    );
    return dst;
  }
}
