///<reference path="./weight_decoder_raw.ts" />

namespace WebDNN {
    export interface WeightDecoder {
        decode(data: Uint8Array, weight_allocation: WeightAllocation): Promise<Float32Array>;
    }

    export interface WeightAllocation {
        total_size: number;
        allocation: { [index: string]: { name: string, offset: number, size: number } }
    }
}
