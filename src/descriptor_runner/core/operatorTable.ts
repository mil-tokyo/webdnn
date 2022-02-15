import { Backend } from "../interface/core/constants";
import { Operator, OperatorEntry } from "../interface/core/operator";

const registeredOperators: {
  [opType: string]: OperatorEntry[];
} = {};

function registerOperator(operatorEntry: OperatorEntry) {
  if (!(operatorEntry.opType in registeredOperators)) {
    registeredOperators[operatorEntry.opType] = [];
  }
  registeredOperators[operatorEntry.opType].push(operatorEntry);
}

export function registerOperators(operatorEntries: OperatorEntry[]): void {
  for (const entry of operatorEntries) {
    registerOperator(entry);
  }
}

export function instantiateOperator(
  opType: string,
  opset: number,
  backendOrder: Backend[],
  currentTensorsBackends: Backend[][]
): Operator | null {
  const entries = registeredOperators[opType];
  if (!entries) {
    return null;
  }

  let localBackendOrder = backendOrder;
  // 特殊なオペレータ
  switch (opType) {
    case "Flatten":
    case "Pad":
    case "Reshape":
    case "Squeeze":
    case "Transpose":
    case "Unsqueeze":
      // データ側テンソル(currentTensorsBackends[0])のあるオペレータ上で実行
      for (const backend of backendOrder) {
        if (currentTensorsBackends[0].includes(backend)) {
          localBackendOrder = [backend];
        }
      }
      break;
    case "Shape":
      // 常にCPU
      localBackendOrder = ["cpu"];
      break;
  }

  for (const backend of localBackendOrder) {
    for (const entry of entries) {
      if (entry.backend !== backend) {
        continue;
      }
      if (entry.opsetMin > opset) {
        continue;
      }
      if (entry.opsetMax != null && entry.opsetMax <= opset) {
        continue;
      }
      return entry.factory();
    }
  }
  return null;
}
