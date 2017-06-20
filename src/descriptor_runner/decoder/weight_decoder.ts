///<reference path="../memory_layout.ts" />

namespace WebDNN {
    export interface WeightDecoder {
        decode(data: Uint8Array, memory_layout: MemoryLayout): Promise<Float32Array>;
    }
}
