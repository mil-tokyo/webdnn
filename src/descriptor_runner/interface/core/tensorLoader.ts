import { CPUTensor } from "../backend/cpu/cpuTensor";

export interface TensorLoader {
  loadAll: (
    progressCallback?: (loadedBytes: number) => unknown
  ) => Promise<Map<string, CPUTensor>>;
}
