/* eslint-disable @typescript-eslint/no-explicit-any */
/* eslint-disable @typescript-eslint/no-non-null-assertion */
import { onnx } from "onnx-proto";
import {
  Backend,
  DataType,
  backendsWithoutCPU,
} from "../interface/core/constants";
import {
  clipLong,
  intOrLongToInt,
  intOrLongToIntVector,
  nonnull,
} from "../util";
import Long from "long";
import { InputProxy } from "./inputProxy";
import { OutputProxy } from "./outputProxy";
import { findTensorReleaseTiming, modelTransform } from "./modelTransform";
import { CPUTensor } from "../interface/backend/cpu/cpuTensor";
import { Tensor } from "../interface/core/tensor";
import { WebGPUTensor } from "../interface/backend/webgpu/webgpuTensor";
import { WebGLTensor } from "../interface/backend/webgl/webglTensor";
import { WasmTensor } from "../interface/backend/wasm/wasmTensor";
import { instantiateOperator } from "./operatorTable";
import { Runner } from "../interface/core/runner";
import { WebDNNCPUContext } from "../interface/backend/cpu/cpuContext";
import { WebDNNWasmContext } from "../interface/backend/wasm/wasmContext";
import { WebDNNWebGLContext } from "../interface/backend/webgl/webglContext";
import { WebDNNWebGPUContext } from "../interface/backend/webgpu/webgpuContext";
import { TensorLoaderImpl } from "./tensorLoaderImpl";
import { TensorLoader } from "../interface/core/tensorLoader";
import { WebDNNLogging } from "../logging";

const logger = WebDNNLogging.getLogger("WebDNN.runner");

export interface BackendContexts {
  cpu: WebDNNCPUContext;
  wasm?: WebDNNWasmContext;
  webgl?: WebDNNWebGLContext;
  webgpu?: WebDNNWebGPUContext;
}

export class RunnerImpl implements Runner {
  model?: onnx.ModelProto;

  loaded: boolean;

  initializerTensors!: Map<string, CPUTensor>;

  copiedInitializerTensors!: Map<Backend, Map<string, Tensor>>;

  useCompatibilityProxy: boolean;

  inputs!: InputProxy[];

  outputs!: OutputProxy[];

  opset!: number;

  tensorMoveOptions: { [key: string]: Record<string, any> };

  /**
   * key: operator name
   */
  forceOperatorBackendOrder: { [key: string]: Backend[] };

  /**
   * Primary backend
   */
  readonly backendName: Backend;

  constructor(
    public backendOrder: Backend[],
    private backendContexts: BackendContexts
  ) {
    this.backendName = this.backendOrder[0];
    this.loaded = false;
    this.useCompatibilityProxy = false;
    this.tensorMoveOptions = {};
    this.forceOperatorBackendOrder = {};
  }

  getTensorLoader(path: string[] | string): TensorLoader {
    return new TensorLoaderImpl(path, this.backendContexts.cpu);
  }

  async loadModel(directory: string, onnxBasename: string): Promise<void> {
    const f = await fetch(directory + onnxBasename),
      b = await f.arrayBuffer();
    this.model = onnx.ModelProto.decode(new Uint8Array(b));
    modelTransform(this.model, this.backendOrder);
    if (this.model!.opsetImport.length !== 1) {
      logger.warn(
        `Specifying multiple opset_import is not supported. Using first one.`
      );
    }
    this.opset = intOrLongToInt(this.model!.opsetImport[0].version!);
    this.initializerTensors = new Map();
    for (const [name, tensor] of this.extractInitializerTensor().entries()) {
      this.initializerTensors.set(name, tensor);
    }
    for (const [name, tensor] of (
      await this.loadExternalInitializerTensor(directory)
    ).entries()) {
      this.initializerTensors.set(name, tensor);
    }
    if (this.useCompatibilityProxy) {
      this.initInputProxy();
      this.initOutputProxy();
    }
    this.copiedInitializerTensors = new Map();
    for (const backend of this.backendOrder) {
      if (backend !== "cpu") {
        this.copiedInitializerTensors.set(backend, new Map());
      }
    }
    for (const md of this.model!.metadataProps) {
      if (md.key === "WebDNN2.TensorMoveOptions") {
        this.tensorMoveOptions = JSON.parse(md.value!);
      }
      if (md.key === "WebDNN2.ForceOperatorBackendOrder") {
        this.forceOperatorBackendOrder = JSON.parse(md.value!);
      }
    }
    this.loaded = true;
  }

  private extractInitializerTensor(): Map<string, CPUTensor> {
    const tensors = new Map<string, CPUTensor>();
    for (const initializer of this.model!.graph!.initializer!) {
      const dims = intOrLongToIntVector(initializer.dims!);
      if (initializer.dataType === onnx.TensorProto.DataType.FLOAT) {
        if (initializer.rawData?.byteLength) {
          // Float32Array(initializer.rawData!.buffer) は不可(4byteにアライメントされていない場合がある)
          const newBuffer = new Uint8Array(initializer.rawData!.byteLength);
          newBuffer.set(initializer.rawData!);
          tensors.set(
            initializer.name!,
            this.backendContexts.cpu.emptyTensor(
              dims,
              "float32",
              new Float32Array(
                newBuffer.buffer,
                0,
                newBuffer.byteLength / Float32Array.BYTES_PER_ELEMENT
              )
            )
          );
        } else if (initializer.floatData) {
          tensors.set(
            initializer.name!,
            this.backendContexts.cpu.emptyTensor(
              dims,
              "float32",
              new Float32Array(initializer.floatData)
            )
          );
        }
      } else if (initializer.dataType === onnx.TensorProto.DataType.INT64) {
        // 1要素が8byte (int64)
        if (initializer.rawData?.byteLength) {
          const rawData = initializer.rawData!,
            view = new DataView(
              rawData.buffer,
              rawData.byteOffset,
              rawData.byteLength
            ),
            ab = new Int32Array(view.byteLength / 8);
          for (let idx = 0; idx < ab.length; idx++) {
            ab[idx] = clipLong(
              new Long(
                view.getUint32(idx * 8, true),
                view.getUint32(idx * 8 + 4, true)
              )
            );
          }
          tensors.set(
            initializer.name!,
            this.backendContexts.cpu.emptyTensor(dims, "int32", ab)
          );
        } else if (initializer.int64Data) {
          tensors.set(
            initializer.name!,
            this.backendContexts.cpu.emptyTensor(
              dims,
              "int32",
              new Int32Array(intOrLongToIntVector(initializer.int64Data))
            )
          );
        }
      } else if (initializer.dataType === onnx.TensorProto.DataType.INT32) {
        if (initializer.rawData?.byteLength) {
          // 1要素が4byte (int32)
          const rawData = initializer.rawData!,
            view = new DataView(
              rawData.buffer,
              rawData.byteOffset,
              rawData.byteLength
            ),
            ab = new Int32Array(view.byteLength / 4);
          for (let idx = 0; idx < ab.length; idx++) {
            ab[idx] = view.getInt32(idx * 4, true);
          }
          tensors.set(
            initializer.name!,
            this.backendContexts.cpu.emptyTensor(dims, "int32", ab)
          );
        } else if (initializer.int32Data) {
          tensors.set(
            initializer.name!,
            this.backendContexts.cpu.emptyTensor(
              dims,
              "int32",
              new Int32Array(initializer.int32Data)
            )
          );
        }
      } else {
        throw new Error(
          `Unsupported initializer dataType ${initializer.dataType}`
        );
      }
    }
    return tensors;
  }

  private async loadExternalInitializerTensor(
    directory: string
  ): Promise<Map<string, CPUTensor>> {
    for (const md of this.model!.metadataProps) {
      if (md.key === "WebDNN2.WeightPaths") {
        const paths = md.value!.split(":").map((bn) => directory + bn),
          loader = this.getTensorLoader(paths);
        return loader.loadAll();
      }
    }
    return new Map();
  }

  private getIOProxyShape(vi: onnx.IValueInfoProto) {
    const shape = nonnull(
      vi.type?.tensorType?.shape?.dim?.map((d) =>
        intOrLongToInt(nonnull(d.dimValue))
      )
    );
    let dataType: DataType;
    switch (vi.type?.tensorType?.elemType) {
      case onnx.TensorProto.DataType.FLOAT:
        dataType = "float32";
        break;
      case onnx.TensorProto.DataType.INT32:
      case onnx.TensorProto.DataType.INT64:
        dataType = "int32";
        break;
      default:
        throw new Error();
    }
    return { shape, dataType };
  }

  private initInputProxy() {
    const graph = nonnull(this.model?.graph);
    this.inputs = graph.input!.map((input) => {
      const { shape, dataType } = this.getIOProxyShape(input);
      return new InputProxy(shape, dataType);
    });
  }

  private initOutputProxy() {
    const graph = nonnull(this.model?.graph);
    this.outputs = graph.output!.map((input) => {
      const { shape, dataType } = this.getIOProxyShape(input);
      return new OutputProxy(shape, dataType);
    });
  }

  getInputNames(): string[] {
    const graph = nonnull(this.model?.graph);
    return graph.input!.map((gi) => gi.name!);
  }

  getOutputNames(): string[] {
    const graph = nonnull(this.model?.graph);
    return graph.output!.map((gi) => gi.name!);
  }

  async run(inputs?: CPUTensor[]): Promise<CPUTensor[]> {
    if (!this.model || !this.loaded) {
      throw new Error("not initialized");
    }
    const graph = nonnull(this.model.graph),
      tensorsForBackends = {
        cpu: new Map<string, CPUTensor>(),
        wasm: new Map<string, WasmTensor>(),
        webgl: new Map<string, WebGLTensor>(),
        webgpu: new Map<string, WebGPUTensor>(),
      };

    for (const [name, tensor] of this.initializerTensors.entries()) {
      tensorsForBackends.cpu.set(name, tensor);
    }
    for (const [backend, kv] of this.copiedInitializerTensors.entries()) {
      for (const [name, tensor] of kv.entries()) {
        tensorsForBackends[backend].set(name, tensor as any);
      }
    }

    if (!inputs) {
      // From inputProxy
      if (this.useCompatibilityProxy) {
        inputs = this.inputs.map((v) => {
          const t = this.backendContexts.cpu.emptyTensor(v.dims, v.dataType);
          t.data.set(v);
          return t;
        });
      } else {
        throw new Error();
      }
    }

    // 入力設定
    if (graph.input!.length !== inputs.length) {
      throw new Error("length of inputs mismatch");
    }
    for (let i = 0; i < inputs.length; i++) {
      const graphInput = graph.input![i];
      // if (graphInput.type!.tensorType!.elemType !== 1) {
      //   throw new Error("graph input type must be float32");
      // }
      tensorsForBackends.cpu.set(graphInput.name!, inputs[i]);
    }

    const tensorReleaseTiming = findTensorReleaseTiming(
        this.model!,
        new Set(this.initializerTensors.keys())
      ),
      nodePerformances: {
        opType: string;
        name: string;
        backend: Backend;
        inputDims: ReadonlyArray<number>[];
        outputDims: ReadonlyArray<number>[];
        elapsed: number;
      }[] = [];

    for (let i = 0; i < graph.node!.length; i++) {
      const nodeStartTime = Date.now(),
        node = graph.node![i],
        opType = nonnull(node.opType);
      let actualBackend: Backend,
        actualInputDims: ReadonlyArray<number>[],
        actualOutputDims: ReadonlyArray<number>[],
        backendOrderForNode =
          this.forceOperatorBackendOrder[node.name!] || this.backendOrder;
      let firstTry = true;
      // eslint-disable-next-line no-constant-condition
      while (true) {
        try {
          // テンソルがどこにあるのか調べる
          const currentTensorsBackends: Backend[][] = [];
          for (let j = 0; j < node.input!.length; j++) {
            const inputName = node.input![j],
              bs: Backend[] = [];
            for (const backend of backendOrderForNode) {
              if (tensorsForBackends[backend].has(inputName)) {
                bs.push(backend);
              }
            }
            currentTensorsBackends.push(bs);
          }
          const operator = instantiateOperator(
            opType,
            this.opset,
            backendOrderForNode,
            currentTensorsBackends
          );
          if (!operator) {
            throw new Error(
              `Operator implementation for ${opType}, opset=${this.opset} does not exist.`
            );
          }
          operator.initialize(nonnull(node.attribute));
          const tensorBackendRequirement = operator.getTensorBackendRequirement(
              node.input!.length,
              node.output!.length
            ),
            // 入力を集める
            operatorInputs: Tensor[] = [];
          for (let j = 0; j < node.input!.length; j++) {
            const inputName = node.input![j],
              reqBackend = tensorBackendRequirement[j];
            if (!reqBackend) {
              // どこでもいい
              const t =
                tensorsForBackends[currentTensorsBackends[j][0]].get(inputName);
              if (!t) {
                throw new Error();
              }
              operatorInputs.push(t);
            } else {
              const t = tensorsForBackends[reqBackend].get(inputName);
              if (t) {
                operatorInputs.push(t);
              } else {
                let found = false;
                for (const otherBackend of this.backendOrder) {
                  const otherT =
                    tensorsForBackends[otherBackend].get(inputName);
                  if (otherT) {
                    const tensorMoveOption =
                        this.tensorMoveOptions[inputName] || {},
                      movedT = await this.backendContexts[
                        reqBackend
                      ]!.moveTensor(otherT, tensorMoveOption);
                    tensorsForBackends[reqBackend].set(
                      inputName,
                      movedT as any
                    );
                    operatorInputs.push(movedT);
                    found = true;
                    break;
                  }
                }
                if (!found) {
                  throw new Error(`Input ${inputName} not found`);
                }
              }
            }
          }

          let context: any = {};
          switch (operator.backend) {
            case "wasm":
              context = this.backendContexts.wasm;
              break;
            case "webgpu":
              context = this.backendContexts.webgpu;
              break;
            case "webgl":
              context = this.backendContexts.webgl;
              break;
            case "cpu":
              context = this.backendContexts.cpu;
              break;
            default:
              throw new Error();
          }
          logger.debug(
            `Running ${node.name!}(${opType}) on ${operator.backend}`
          );
          const operatorOutputs = await operator.run(
            context,
            operatorInputs,
            node.output!.length
          );
          actualInputDims = operatorInputs.map((t) => t.dims);
          actualOutputDims = operatorOutputs.map((t) => t.dims);
          for (let j = 0; j < node.output!.length; j++) {
            const outputName = node.output![j];
            tensorsForBackends[operatorOutputs[j].backend].set(
              outputName,
              operatorOutputs[j] as any
            );
          }
          actualBackend = operator.backend;
          break;
        } catch (error) {
          if (firstTry) {
            logger.warn(`Failed to run ${node.name}. Retrying on cpu.`, error);
            firstTry = false;
            backendOrderForNode = ["cpu"];
            continue;
          } else {
            throw error;
          }
        }
      }

      const tensorNamesToRelease = tensorReleaseTiming.get(node.name!) || [];
      for (const name of tensorNamesToRelease) {
        for (const backend of Object.keys(tensorsForBackends) as Backend[]) {
          const t = tensorsForBackends[backend].get(name);
          if (t) {
            t.dispose();
            tensorsForBackends[backend].delete(name);
          }
        }
      }
      const nodeEndTime = Date.now();
      nodePerformances.push({
        opType: node.opType!,
        name: node.name!,
        backend: actualBackend,
        inputDims: actualInputDims,
        outputDims: actualOutputDims,
        elapsed: nodeEndTime - nodeStartTime,
      });
    }

    const outputs = [];
    for (let j = 0; j < graph.output!.length; j++) {
      const outputInfo = graph.output![j];
      let outputTensor = tensorsForBackends.cpu.get(outputInfo.name!);
      if (!outputTensor) {
        for (const otherBackend of this.backendOrder) {
          const otherT = tensorsForBackends[otherBackend].get(outputInfo.name!);
          if (otherT) {
            const movedT = await this.backendContexts.cpu.moveTensor(
              otherT,
              {}
            );
            tensorsForBackends.cpu.set(outputInfo.name!, movedT as any);
            outputTensor = movedT;
            break;
          }
        }
      }
      if (!outputTensor) {
        throw new Error(`Output ${outputInfo.name} not found`);
      }

      if (this.useCompatibilityProxy) {
        // Copy value to output proxy
        this.outputs[j].set(outputTensor.data);
      }

      outputs.push(outputTensor);
    }

    for (const backend of backendsWithoutCPU) {
      for (const [name, t] of tensorsForBackends[backend].entries()) {
        if (this.initializerTensors.has(name)) {
          this.copiedInitializerTensors.get(backend)!.set(name, t);
        } else {
          t.dispose();
        }
      }
    }

    logger.debug("Performance", nodePerformances);

    return outputs;
  }
}
