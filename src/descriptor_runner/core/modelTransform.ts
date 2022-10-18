/* eslint-disable @typescript-eslint/no-non-null-assertion */
import { onnx } from "onnx-proto";
import { Backend } from "../interface/core/constants";
import { WebDNNLogging } from "../logging";

const logger = WebDNNLogging.getLogger("WebDNN.modelTransform");

export function modelTransform(
  model: onnx.ModelProto,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  backendOrder: Backend[]
): void {
  /*
   * TODO: implementation
   * if (backendOrder.includes("webgl")) {
   *   const webglContext = WebDNNWebGLContext.getInstance();
   *   if (webglContext.webgl2 && webglContext.canOnlyReadRGBA) {
   *     outputPackRGBA(graph, backendOrder);
   *   }
   * }
   */
  renameDuplicatedNode(model);
}

function renameDuplicatedNode(model: onnx.ModelProto): void {
  const usedNames = new Set<string>();
  for (const node of model.graph!.node!) {
    let origName = node.name;
    if (!origName) {
      origName = "unnamed";
    }
    if (usedNames.has(origName)) {
      let newName = origName + "_";
      while (usedNames.has(newName)) {
        newName = newName + "_";
      }
      node.name = newName;
      usedNames.add(newName);
      logger.warn(
        `node name ${origName} is already used: renaming to ${newName}`
      );
    } else {
      usedNames.add(origName);
    }
  }
}

/**
 * テンソルを開放するタイミングを計算する。
 * @param model 計算対象のモデル
 * @returns key: オペレータ名, value: そのオペレータ完了直後に開放するテンソルの名前
 */
export function findTensorReleaseTiming(
  model: onnx.ModelProto,
  initializerTensorNames: Set<string>
): Map<string, string[]> {
  const lastReferencedAt = new Map<string, string>(),
    graph = model.graph!;
  for (const node of graph.node!) {
    for (const inputName of node.input!) {
      lastReferencedAt.set(inputName, node.name!);
    }
  }
  // Optimized modelではgraph.initializer以外からテンソルを読み込むため、実際に読み込まれたテンソル名リストを用いる
  for (const initializer of initializerTensorNames) {
    lastReferencedAt.delete(initializer);
  }
  for (const input of graph.input!) {
    lastReferencedAt.delete(input.name!);
  }
  for (const output of graph.output!) {
    lastReferencedAt.delete(output.name!);
  }

  const timing = new Map<string, string[]>();
  for (const [name, last] of lastReferencedAt.entries()) {
    const t = timing.get(last) || [];
    t.push(name);
    timing.set(last, t);
  }

  return timing;
}
