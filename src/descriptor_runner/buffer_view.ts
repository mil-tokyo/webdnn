namespace WebDNN {
    export class BufferView {
        private internalView: Float32Array | null = null;

        getFloat32Array(): Float32Array {
            if (!this.internalView) throw Error('BufferView is not initialized');

            return this.internalView;
        }

        setFloat32Array(array: Float32Array) {
            this.internalView = array;
        }

        /**
         * The size in bytes of each element in the array.
         */
        get BYTES_PER_ELEMENT(): number {
            if (!this.internalView) throw Error('BufferView is not initialized.');

            return this.internalView.BYTES_PER_ELEMENT;
        }

        /**
         * The length in bytes of the array.
         */
        get byteLength(): number {
            if (!this.internalView) throw Error('BufferView is not initialized.');

            return this.internalView.byteLength;
        }

        /**
         * The offset in bytes of the array.
         */
        get byteOffset(): number {
            if (!this.internalView) throw Error('BufferView is not initialized.');

            return this.internalView.byteOffset;
        }

        /**
         * Returns the this object after copying a section of the array identified by start and end
         * to the same array starting at position target
         * @param target If target is negative, it is treated as length+target where length is the
         * length of the array.
         * @param start If start is negative, it is treated as length+start. If end is negative, it
         * is treated as length+end.
         * @param end If not specified, length of the this object is used as its default value.
         */
        copyWithin(target: number, start: number, end?: number): this {
            if (!this.internalView) throw Error('BufferView is not initialized.');

            this.internalView.copyWithin(target, start, end);

            return this;
        }


        /**
         * Returns the this object after filling the section identified by start and end with value
         * @param value value to fill array section with
         * @param start index to start filling the array at. If start is negative, it is treated as
         * length+start where length is the length of the array.
         * @param end index to stop filling the array at. If end is negative, it is treated as
         * length+end.
         */
        fill(value: number, start?: number, end?: number): this {
            if (!this.internalView) throw Error('BufferView is not initialized.');

            this.internalView.fill(value, start, end);

            return this;
        }


        /**
         * The length of the array.
         */
        get length(): number {
            return this.internalView ? this.internalView.length : 0;
        }

        /**
         * Sets a value or an array of values.
         * @param array A typed or untyped array of values to set.
         * @param offset The index in the current array at which the values are to be written.
         */
        set(array: ArrayLike<number>, offset?: number): void {
            if (!this.internalView) throw Error('BufferView is not initialized.');

            return this.internalView.set(array, offset);
        }

        //TODO: Override indexing access by using proxy
        [index: number]: number;
    }
}
