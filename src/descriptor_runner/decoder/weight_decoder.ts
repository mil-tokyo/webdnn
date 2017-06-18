///<reference path="./weight_decoder_raw.ts" />

namespace WebDNN {
    export interface Placeholder {
        eval: string
    }

    export interface WeightDecoder {
        decode(data: Uint8Array, memory_layout: MemoryLayout): Promise<Float32Array>;
    }

    export interface MemoryLayout {
        'static': {
            size: number,
            allocations: {
                [index: string]: {
                    name: string,
                    offset: number,
                    size: number
                }
            }
        },
        dynamic: {
            size: number | Placeholder,
            allocations: {
                [index: string]: {
                    name: string,
                    offset: number | Placeholder,
                    size: number | Placeholder
                }
            }
        }
    }
}
