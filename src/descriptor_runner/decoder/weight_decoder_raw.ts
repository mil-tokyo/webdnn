///<reference path="./weight_decoder.ts" />

namespace WebDNN {
    export class WeightDecoderRaw implements WeightDecoder {
        async decode(data: Uint8Array, weight_allocation: WeightAllocation) : Promise<Float32Array> {
            return new Float32Array(data.buffer, data.byteOffset, data.byteLength / 4);
        }
    }
}
