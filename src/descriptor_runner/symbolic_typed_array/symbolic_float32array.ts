/**
 * @module webdnn
 */
/** Don't Remove This comment block */
import { SymbolicTypedArray } from "./symbolic_typed_array";

/**
 * @protected
 */
export default class SymbolicFloat32Array extends SymbolicTypedArray<Float32Array> {
    toActual() {
        if (!this.arrayBuffer) {
            throw new Error('Internal buffer for this variable is not set. DescriptorRunner.setPlaceholderValue() have to be called before calling this function.');
        }
        return new Float32Array(
            this.arrayBuffer,
            this.ignoreOffsetOnActual ? 0 : this.offset * Float32Array.BYTES_PER_ELEMENT,
            this.length
        );
    }
}
