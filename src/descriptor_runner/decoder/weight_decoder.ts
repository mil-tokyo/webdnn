/**
 * @module webdnn
 */

/** Don't Remove This comment block */

/**
 * @protected
 */
interface WeightDecoder {
    decode(data: Uint8Array): Promise<Float32Array>;
}

export default WeightDecoder
