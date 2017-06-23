///<reference path="./memory_layout.ts" />
///<reference path="./placeholder.ts" />

namespace WebDNN {
    export abstract class SymbolicArrayBufferView<T extends Float32Array | Int32Array> {
        protected arrayBuffer?: ArrayBuffer;
        protected allocation: Allocation;
        protected placeholderContext?: PlaceholderContext;

        /**
         * Convert symbolic buffer view into actual buffer view.
         * If this buffer view is initialized based on placeholder offset or size and the placeholder is not resolved,
         * the error is thrown.
         */
        abstract toActual(): T;

        constructor(allocation: Allocation, placeholderContext?: PlaceholderContext, protected ignoreOffsetOnActual: boolean = false) {
            this.allocation = allocation;

            if (this.isDynamic) {
                if (!placeholderContext) {
                    throw Error('PlaceholderContext must be required when SymbolicArrayBufferView is initialized as dynamic buffer view.')
                }
            }

            this.placeholderContext = placeholderContext;
        }

        setArrayBuffer(arrayBuffer) {
            this.arrayBuffer = arrayBuffer;
        }

        get isDynamic() {
            return (typeof this.allocation.offset !== 'number' || typeof this.allocation.size !== 'number')
        }

        get offset() {
            //TODO
            if (this.isDynamic) {
                return this.placeholderContext!.resolve(this.allocation.offset);

            } else {
                return (this.allocation as ResolvedAllocation).offset;
            }
        }

        get length() {
            if (this.isDynamic) {
                return this.placeholderContext!.resolve(this.allocation.size);

            } else {
                return (this.allocation as ResolvedAllocation).size;
            }
        }

        /**
         * Sets a value or an array of values.
         * @param array A typed or untyped array of values to set.
         * @param offset The index in the current array at which the values are to be written.
         */
        set(array: ArrayLike<number>, offset?: number): void {
            return this.toActual().set(array, offset);
        }
    }

    export class SymbolicFloat32Array extends SymbolicArrayBufferView<Float32Array> {
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

    export class SymbolicInt32Array extends SymbolicArrayBufferView<Int32Array> {
        toActual() {
            if (!this.arrayBuffer) {
                throw new Error('Internal buffer for this variable is not set. DescriptorRunner.setPlaceholderValue() have to be called before calling this function.');
            }
            return new Int32Array(
                this.arrayBuffer,
                this.ignoreOffsetOnActual ? 0 : this.offset * Int32Array.BYTES_PER_ELEMENT,
                this.length
            );
        }
    }
}
