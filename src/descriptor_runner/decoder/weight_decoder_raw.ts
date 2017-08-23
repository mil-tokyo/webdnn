/**
 * @module webdnn
 */
/** Don't Remove This comment block */

import WeightDecoder from "./weight_decoder";

/**
 * @protected
 */
export default class WeightDecoderRaw implements WeightDecoder {
    async decode(data: Uint8Array): Promise<Float32Array> {
        return new Float32Array(data.buffer, data.byteOffset, data.byteLength / 4);
    }
}
