/**
 * @module webdnn
 */
/** Don't Remove This comment block */

import { MemoryLayout } from "../graph_descriptor/memory_layout";

/**
 * @protected
 */
interface WeightDecoder {
    decode(data: Uint8Array, memory_layout: MemoryLayout): Promise<Float32Array>;
}

export default WeightDecoder
