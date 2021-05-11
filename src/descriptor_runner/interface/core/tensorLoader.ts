import { CPUTensor } from "../backend/cpu/cpuTensor";

export interface TensorLoader {
  loadAll: () => Promise<Map<string, CPUTensor>>;
}
