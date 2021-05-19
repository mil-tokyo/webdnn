/* eslint-disable @typescript-eslint/no-non-null-assertion */
import { onnx } from "onnx-proto";
import { Backend } from "../interface/core/constants";

export function modelTransform(
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  model: onnx.ModelProto,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  backendOrder: Backend[]
): void {
  // TODO: implementation
  // if (backendOrder.includes("webgl")) {
  //   const webglContext = WebDNNWebGLContext.getInstance();
  //   if (webglContext.webgl2 && webglContext.canOnlyReadRGBA) {
  //     outputPackRGBA(graph, backendOrder);
  //   }
  // }
}

/**
 * テンソルを開放するタイミングを計算する。
 * @param model 計算対象のモデル
 * @returns key: オペレータ名, value: そのオペレータ完了直後に開放するテンソルの名前
 */
export function findTensorReleaseTiming(
  model: onnx.ModelProto
): Map<string, string[]> {
  const lastReferencedAt = new Map<string, string>();

  const graph = model.graph!;
  for (const node of graph.node!) {
    for (const inputName of node.input!) {
      lastReferencedAt.set(inputName, node.name!);
    }
  }
  for (const initializer of graph.initializer!) {
    lastReferencedAt.delete(initializer.name!);
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
