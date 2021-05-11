import { CPUTensor } from "../backend/cpu/cpuTensor";

export interface Runner {
  run(inputs?: CPUTensor[]): Promise<CPUTensor[]>;
}
