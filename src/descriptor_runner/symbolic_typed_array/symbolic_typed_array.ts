/**
 * @module webdnn
 */
/** Don't Remove This comment block */
import PlaceholderContext, { Placeholder } from "../placeholder";

/**
 * @protected
 */
function flatten(arr: any) {
    let result = [] as any[];
    for (let i = 0; i < arr.length; i++) {
        let v = arr[i];
        if (v instanceof Array) {
            result.splice(result.length, 0, flatten(v))
        } else {
            result[result.length] = v;
        }
    }
    return result
}

/**
 * @protected
 */
export abstract class SymbolicTypedArray<T extends Float32Array | Int32Array> {
    /**
     * @protected
     */
    readonly _length: number | Placeholder;

    /**
     * @protected
     */
    readonly _byteOffset: number | Placeholder;

    /**
     * The size in bytes of each element in the array.
     */
    readonly BYTES_PER_ELEMENT: number; // removed "abstract" due to TS2715

    /**
     * @protected
     */
    protected _buffer: ArrayBufferLike | null;

    /**
     * @protected
     */
    name: string;

    /**
     * @protected
     */
    constructor(buffer: ArrayBufferLike | null = null,
                byteOffset: number | Placeholder = 0,
                length?: number | Placeholder,
                protected placeholderContext: PlaceholderContext | null = null) {
        this._byteOffset = byteOffset;
        this._buffer = buffer;

        if (buffer) {
            this._length = length === undefined ? (buffer.byteLength / this.BYTES_PER_ELEMENT) : length;

        } else {
            if (length === undefined) throw Error('"butter" or "length" must be specified.');
            this._length = length;
        }

        if (this.isDynamic) {
            if (!placeholderContext) {
                throw Error('PlaceholderContext must be required when SymbolicTypedArray is initialized as dynamic buffer view.')
            }
        }
    }

    /**
     * Convert SymbolicTypedArray instance into actual TypedArray instance.
     *
     * @returns actual typed array
     */
    abstract toActual(): T;

    /**
     * The ArrayBuffer instance referenced by the array.
     */
    get buffer(): ArrayBufferLike {
        if (!this._buffer) this._buffer = new ArrayBuffer(this.byteOffset + this.byteLength);
        return this._buffer;
    }

    /**
     * The ArrayBuffer instance referenced by the array.
     */
    set buffer(buffer: ArrayBufferLike) {
        this._buffer = buffer;
    }

    /**
     * The length in bytes of the array.
     */
    get byteLength(): number {
        return this.length * this.BYTES_PER_ELEMENT;
    }

    /**
     * The number in this buffer. Actual offset size is `(offset * SIZE_OF_FLOAT)`.
     */
    get offset(): number {
        return this.byteOffset / this.BYTES_PER_ELEMENT;
    }

    /**
     * @protected
     */
    get isDynamic() {
        return (typeof this._byteOffset !== 'number' || typeof this._length !== 'number')
    }

    /**
     * The number of elements in this buffer. Actual byte size is `(length * SIZE_OF_FLOAT)`.
     */
    get length() {
        if (this.isDynamic) {
            return this.placeholderContext!.resolve(this._length) as number;

        } else {
            return this._length as number;
        }
    }

    /**
     * The offset in bytes of the array.
     */
    get byteOffset() {
        if (this.isDynamic) {
            return this.placeholderContext!.resolve(this._byteOffset);

        } else {
            return this._byteOffset as number;
        }
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
        this.toActual().copyWithin(target, start, end);
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
        this.toActual().fill(value, start, end);
        return this;
    }

    /**
     * Returns the index of the first occurrence of a value in an array.
     * @param searchElement The value to locate in the array.
     * @param fromIndex The array index at which to begin the search. If fromIndex is omitted, the
     *  search starts at index 0.
     */
    indexOf(searchElement: number, fromIndex?: number): number {
        return this.toActual().indexOf(searchElement, fromIndex);
    }

    /**
     * Adds all the elements of an array separated by the specified separator string.
     * @param separator A string used to separate one element of an array from the next in the
     * resulting String. If omitted, the array elements are separated with a comma.
     */
    join(separator?: string): string {
        return this.toActual().join(separator);
    }

    /**
     * Returns the index of the last occurrence of a value in an array.
     * @param searchElement The value to locate in the array.
     * @param fromIndex The array index at which to begin the search. If fromIndex is omitted, the
     * search starts at index 0.
     */
    lastIndexOf(searchElement: number, fromIndex?: number): number {
        return this.toActual().lastIndexOf(searchElement, fromIndex);
    }

    /**
     * Sorts an array.
     * @param compareFn The name of the function used to determine the order of the elements. If
     * omitted, the elements are sorted in ascending, ASCII character order.
     */
    sort(compareFn?: (a: number, b: number) => number): this {
        this.toActual().sort(compareFn);
        return this;
    }

    includes(searchElement: number, fromIndex?: number | undefined): boolean {
        return this.toActual().includes(searchElement, fromIndex);
    }

    /**
     * Sets a value or an array of values.
     * @param array A typed or untyped array of values to set.
     * @param offset The index in the current array at which the values are to be written.
     */
    set(array: ArrayLike<number>, offset?: number | undefined): void {
        return this.toActual().set(flatten(array), offset);
    }

    /**
     * Converts a number to a string by using the current locale.
     */
    toLocaleString(): string {
        return this.toActual().toLocaleString();
    }

    /**
     * Returns a string representation of an array.
     */
    toString(): string {
        return this.toActual().toString();
    }

    /** @protected */
    [Symbol.iterator](): IterableIterator<number> {
        return this.toActual()[Symbol.iterator]();
    }

    /**
     * Returns an iterable of key, value pairs for every entry in the array
     */
    entries(): IterableIterator<[number, number]> {
        return this.toActual().entries();
    }

    /**
     * Returns an iterable of keys in the array
     */
    keys(): IterableIterator<number> {
        return this.toActual().keys();
    }

    /**
     * Returns an iterable of values in the array
     */
    values(): IterableIterator<number> {
        return this.toActual().values();
    }
}
