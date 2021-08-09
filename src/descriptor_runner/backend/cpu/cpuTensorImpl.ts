import {
  DataArrayConstructor,
  DataArrayTypes,
  DataType,
} from "../../interface/core/constants";
import { TensorImpl } from "../../core/tensorImpl";
import { CPUTensor } from "../../interface/backend/cpu/cpuTensor";
import { WebDNNLogging } from "../../logging";

const logger = WebDNNLogging.getLogger("WebDNN.CPUTensorImpl");

let perfTotalMemory = 0;

export class CPUTensorImpl extends TensorImpl implements CPUTensor {
  data: DataArrayTypes;

  constructor(
    dims: ReadonlyArray<number>,
    dataType: DataType = "float32",
    data?: DataArrayTypes
  ) {
    super(dims, dataType, "cpu");
    this.data = data || new DataArrayConstructor[dataType](this.length);
    perfTotalMemory += this.data.byteLength;
    logger.debug("CPU memory allocation", {
      size: this.data.byteLength,
      total: perfTotalMemory,
    });
  }

  async getData(): Promise<DataArrayTypes> {
    return this.data;
  }

  async setData(data: DataArrayTypes): Promise<void> {
    this.data.set(data);
  }

  dispose(): void {
    perfTotalMemory -= this.data.byteLength;
    logger.debug("CPU memory free", {
      size: this.data.byteLength,
      total: perfTotalMemory,
    });
    this.data = new Float32Array(1);
  }

  static isCPUTensor(tensor: TensorImpl): tensor is CPUTensorImpl {
    return tensor.backend === "cpu";
  }

  getDataSync(): DataArrayTypes {
    return this.data;
  }

  getValue(idxs: number[]): number {
    if (idxs.length !== this.ndim) {
      throw new Error("length of idxs does not match tensor.ndim");
    }
    let ofs = 0;
    for (let i = 0; i < this.ndim; i++) {
      ofs += this.strides[i] * idxs[i];
    }
    return this.data[ofs];
  }

  setValue(value: number, idxs: number[]): void {
    if (idxs.length !== this.ndim) {
      throw new Error("length of idxs does not match tensor.ndim");
    }
    let ofs = 0;
    for (let i = 0; i < this.ndim; i++) {
      ofs += this.strides[i] * idxs[i];
    }
    this.data[ofs] = value;
  }
}
