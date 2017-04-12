/// <reference path="../../../array-prototype/webgpu_handler.ts" />

namespace WebDNN {
    export namespace PrototypeKernel {
        export let webgpu: WebGPUHandler;

        export async function init(_webgpu: WebGPUHandler) {
            webgpu = _webgpu;
        }

        export async function fetchKernel(scriptTag: HTMLScriptElement) {
            let res = await fetch(scriptTag.src);
            if (res.status != 200) throw Error('Kernel fetch failed.')

            let source = await res.text();
            webgpu.loadKernel(source, 'prototype');
        }
    }
}
