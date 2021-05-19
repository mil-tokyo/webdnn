import { Backend } from "../interface/core/constants";
import * as Image from "../image";
import * as Math from "../math";
export { Image, Math };
import { BackendContexts, RunnerImpl } from "../core/runnerImpl";
import { WebDNNCPUContextImpl } from "../backend/cpu/cpuContextImpl";
import { WebDNNWebGLContextImpl } from "../backend/webgl/webglContextImpl";
import { WebDNNWasmContextImpl } from "../backend/wasm/wasmContextImpl";
import { WebDNNWebGPUContextImpl } from "../backend/webgpu/webgpuContextImpl";
import { registerOperators } from "../core/operatorTable";
import { Runner } from "../interface/core/runner";
import { OperatorEntry } from "../interface/core/operator";
export { CPUTensorImpl as CPUTensor } from "../backend/cpu/cpuTensorImpl";

export interface InitOption {
  backendOrder?: Backend[];
  optimized?: boolean;
}

const defaultContexts = {
  cpu: null as WebDNNCPUContextImpl | null,
};

interface InjectionParams {
  operatorEntries: OperatorEntry[];
  wasmWorkerSrcUrl?: string;
}

let injectionCallback: ((params: InjectionParams) => void) | null = null;

export function injectOperators(params: InjectionParams): void {
  if (injectionCallback) {
    injectionCallback(params);
    injectionCallback = null;
  }
}

function loadJS(url: string): Promise<InjectionParams> {
  return new Promise((resolve) => {
    injectionCallback = resolve;
    const tag = document.createElement("script");
    tag.type = "text/javascript";
    tag.src = url;
    document.body.appendChild(tag);
  });
}

async function loadCPU(
  directory: string,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  options: InitOption,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  cpuContext: WebDNNCPUContextImpl
): Promise<void> {
  const injectionParams = await loadJS(`${directory}op-cpu.js`);
  registerOperators(injectionParams.operatorEntries);
}

async function loadWasm(
  directory: string,
  options: InitOption,
  cpuContext: WebDNNCPUContextImpl
): Promise<WebDNNWasmContextImpl> {
  const ctx = new WebDNNWasmContextImpl(cpuContext);
  const injectionParams = await loadJS(`${directory}op-wasm.js`);
  if (typeof injectionParams.wasmWorkerSrcUrl !== "string") {
    throw new Error("Invalid injection parameter");
  }
  await ctx.initialize(injectionParams.wasmWorkerSrcUrl);
  registerOperators(injectionParams.operatorEntries);
  return ctx;
}

async function loadWebGL(
  directory: string,
  options: InitOption,
  cpuContext: WebDNNCPUContextImpl
): Promise<WebDNNWebGLContextImpl> {
  const ctx = new WebDNNWebGLContextImpl(cpuContext);
  const injectionParams = await loadJS(`${directory}op-webgl.js`);
  await ctx.initialize();
  registerOperators(injectionParams.operatorEntries);
  return ctx;
}

async function loadWebGPU(
  directory: string,
  options: InitOption,
  cpuContext: WebDNNCPUContextImpl
): Promise<WebDNNWebGPUContextImpl> {
  const ctx = new WebDNNWebGPUContextImpl(cpuContext);
  const injectionParams = await loadJS(`${directory}op-webgpu.js`);
  await ctx.initialize();
  registerOperators(injectionParams.operatorEntries);
  return ctx;
}

export async function load(
  directory: string,
  options: InitOption = {}
): Promise<Runner> {
  const { backendOrder = ["webgl", "wasm", "cpu"], optimized } = options;
  if (!optimized) {
    throw new Error(
      "webdnn-core.js only accepts optimized model. Specify directory which contains model-cpu.onnx and specify {optimized: true} in options."
    );
  }
  if (!defaultContexts.cpu) {
    defaultContexts.cpu = new WebDNNCPUContextImpl();
    await defaultContexts.cpu.initialize();
  }
  const cpuContext: WebDNNCPUContextImpl = defaultContexts.cpu;
  const backendContexts: BackendContexts = { cpu: cpuContext };
  let succeedBackend: Backend | null = null;
  const opDirectory = directory;
  for (const tryBackend of backendOrder) {
    switch (tryBackend) {
      case "cpu":
        try {
          await loadCPU(opDirectory, options, cpuContext);
          succeedBackend = "cpu";
          // eslint-disable-next-line no-empty
        } catch {}
        break;
      case "wasm":
        {
          try {
            backendContexts.wasm = await loadWasm(
              opDirectory,
              options,
              cpuContext
            );
            succeedBackend = "wasm";
            // eslint-disable-next-line no-empty
          } catch {}
        }
        break;
      case "webgl":
        {
          try {
            backendContexts.webgl = await loadWebGL(
              opDirectory,
              options,
              cpuContext
            );
            succeedBackend = "webgl";
            // eslint-disable-next-line no-empty
          } catch {}
        }
        break;
      case "webgpu":
        {
          try {
            backendContexts.webgpu = await loadWebGPU(
              opDirectory,
              options,
              cpuContext
            );
            succeedBackend = "webgpu";
            // eslint-disable-next-line no-empty
          } catch {}
        }
        break;
      default:
        throw new Error(`Unknown backend ${tryBackend}`);
    }

    if (succeedBackend) {
      break;
    }
  }
  if (!succeedBackend) {
    throw new Error("No backend available");
  }
  const actualBackendOrder: Backend[] =
    succeedBackend === "cpu" ? ["cpu"] : [succeedBackend, "cpu"];
  const runner = new RunnerImpl(actualBackendOrder, backendContexts);
  await runner.loadModel(directory, `model-${actualBackendOrder[0]}.onnx`);
  return runner;
}
