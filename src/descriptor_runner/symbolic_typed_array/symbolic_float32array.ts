/**
 * @module webdnn
 */
/** Don't Remove This comment block */
import { SymbolicTypedArray } from "./symbolic_typed_array";

/**
 * Typed array used for input and output variables of [[webdnn.DescriptorRunner| `DescriptorRunner`]].
 * You can use `SymbolicFloat32Array` almost as same as `Float32Array`.
 *
 * To convert `SymbolicFloat32Array` into actual `Float32Array`, use [[webdnn.SymbolicFloat32Array.toActual| `toActual()`]]
 *
 * ```js
 *
 * let result = runner.outputs[0];  //runner.outputs is array of SymbolicFloat32Array
 *
 * // SymbolicFloat32Array does NOT support index access
 * console.log(result[0]);
 * >>> undefined
 *
 * // By conversion, you can access each element by index
 * console.log(result.toActual()[0]);
 * >>> 1.00  // Actual result
 * ```
 */
export default class SymbolicFloat32Array extends SymbolicTypedArray<Float32Array> implements Float32Array {
    /** @protected */
    [Symbol.toStringTag]: "Float32Array";

    /** @protected */
    [index: number]: number; // TODO

    /**
     * The size in bytes of each element in SymbolicFloat32Array.
     */
    static readonly BYTES_PER_ELEMENT: number = 4;

    /**
     * The size in bytes of each element in the array.
     */
    readonly BYTES_PER_ELEMENT: number = 4;

    /**
     * Convert SymbolicTypedArray instance into actual TypedArray instance.
     *
     * @returns actual typed array
     */
    toActual(): Float32Array {
        if (!this.buffer) {
            throw new Error('Internal buffer for this variable is not set. DescriptorRunner.setPlaceholderValue() have to be called before calling this function.');
        }
        return new Float32Array(this.buffer, this.byteOffset, this.length);
    }

    /**
     * Determines whether all the members of an array satisfy the specified test.
     * @param callbackfn A function that accepts up to three arguments. The every method calls
     * the callbackfn function for each element in array1 until the callbackfn returns false,
     * or until the end of the array.
     * @param thisArg An object to which the this keyword can refer in the callbackfn function.
     * If thisArg is omitted, undefined is used as the this value.
     */
    every(callbackfn: (value: number, index: number, array: Float32Array) => boolean, thisArg?: any): boolean {
        return this.toActual().every(callbackfn, thisArg);
    }

    /**
     * Returns the elements of an array that meet the condition specified in a callback function.
     * @param callbackfn A function that accepts up to three arguments. The filter method calls
     * the callbackfn function one time for each element in the array.
     * @param thisArg An object to which the this keyword can refer in the callbackfn function.
     * If thisArg is omitted, undefined is used as the this value.
     */
    filter(callbackfn: (value: number, index: number, array: Float32Array) => any, thisArg?: any): Float32Array {
        return this.toActual().filter(callbackfn, thisArg);
    }

    /**
     * Returns the value of the first element in the array where predicate is true, and undefined
     * otherwise.
     * @param predicate find calls predicate once for each element of the array, in ascending
     * order, until it finds one where predicate returns true. If such an element is found, find
     * immediately returns that element value. Otherwise, find returns undefined.
     * @param thisArg If provided, it will be used as the this value for each invocation of
     * predicate. If it is not provided, undefined is used instead.
     */
    find(predicate: (value: number, index: number, obj: Float32Array) => boolean, thisArg?: any): number | undefined {
        return this.toActual().find(predicate, thisArg);
    }

    /**
     * Returns the index of the first element in the array where predicate is true, and -1
     * otherwise.
     * @param predicate find calls predicate once for each element of the array, in ascending
     * order, until it finds one where predicate returns true. If such an element is found,
     * findIndex immediately returns that element index. Otherwise, findIndex returns -1.
     * @param thisArg If provided, it will be used as the this value for each invocation of
     * predicate. If it is not provided, undefined is used instead.
     */
    findIndex(predicate: (value: number, index: number, obj: Float32Array) => boolean, thisArg?: any): number {
        return this.toActual().findIndex(predicate, thisArg);
    }

    /**
     * Performs the specified action for each element in an array.
     * @param callbackfn  A function that accepts up to three arguments. forEach calls the
     * callbackfn function one time for each element in the array.
     * @param thisArg  An object to which the this keyword can refer in the callbackfn function.
     * If thisArg is omitted, undefined is used as the this value.
     */
    forEach(callbackfn: (value: number, index: number, array: Float32Array) => void, thisArg?: any): void {
        return this.toActual().forEach(callbackfn, thisArg);
    }

    /**
     * Calls a defined callback function on each element of an array, and returns an array that
     * contains the results.
     * @param callbackfn A function that accepts up to three arguments. The map method calls the
     * callbackfn function one time for each element in the array.
     * @param thisArg An object to which the this keyword can refer in the callbackfn function.
     * If thisArg is omitted, undefined is used as the this value.
     */
    map(callbackfn: (value: number, index: number, array: Float32Array) => number, thisArg?: any): Float32Array {
        return this.toActual().map(callbackfn, thisArg);
    }

    /**
     * Calls the specified callback function for all the elements in an array. The return value of
     * the callback function is the accumulated result, and is provided as an argument in the next
     * call to the callback function.
     * @param callbackfn A function that accepts up to four arguments. The reduce method calls the
     * callbackfn function one time for each element in the array.
     * @param initialValue If initialValue is specified, it is used as the initial value to start
     * the accumulation. The first call to the callbackfn function provides this value as an argument
     * instead of an array value.
     */
    reduce(callbackfn: (previousValue: number, currentValue: number, currentIndex: number, array: Float32Array) => number): number;
    reduce(callbackfn: (previousValue: number, currentValue: number, currentIndex: number, array: Float32Array) => number, initialValue: number): number;

    /**
     * Calls the specified callback function for all the elements in an array. The return value of
     * the callback function is the accumulated result, and is provided as an argument in the next
     * call to the callback function.
     * @param callbackfn A function that accepts up to four arguments. The reduce method calls the
     * callbackfn function one time for each element in the array.
     * @param initialValue If initialValue is specified, it is used as the initial value to start
     * the accumulation. The first call to the callbackfn function provides this value as an argument
     * instead of an array value.
     */
    reduce<U>(callbackfn: (previousValue: U, currentValue: number, currentIndex: number, array: Float32Array) => U, initialValue: U): U;
    reduce(callbackfn, initialValue?): any {
        return this.toActual().reduce(callbackfn, initialValue);
    }

    /**
     * Calls the specified callback function for all the elements in an array, in descending order.
     * The return value of the callback function is the accumulated result, and is provided as an
     * argument in the next call to the callback function.
     * @param callbackfn A function that accepts up to four arguments. The reduceRight method calls
     * the callbackfn function one time for each element in the array.
     * @param initialValue If initialValue is specified, it is used as the initial value to start
     * the accumulation. The first call to the callbackfn function provides this value as an
     * argument instead of an array value.
     */
    reduceRight(callbackfn: (previousValue: number, currentValue: number, currentIndex: number, array: Float32Array) => number): number;
    reduceRight(callbackfn: (previousValue: number, currentValue: number, currentIndex: number, array: Float32Array) => number, initialValue: number): number;

    /**
     * Calls the specified callback function for all the elements in an array, in descending order.
     * The return value of the callback function is the accumulated result, and is provided as an
     * argument in the next call to the callback function.
     * @param callbackfn A function that accepts up to four arguments. The reduceRight method calls
     * the callbackfn function one time for each element in the array.
     * @param initialValue If initialValue is specified, it is used as the initial value to start
     * the accumulation. The first call to the callbackfn function provides this value as an argument
     * instead of an array value.
     */
    reduceRight<U>(callbackfn: (previousValue: U, currentValue: number, currentIndex: number, array: Float32Array) => U, initialValue: U): U;
    reduceRight(callbackfn, initialValue?): any {
        return this.toActual().reduceRight(callbackfn, initialValue);
    }

    /**
     * Reverses the elements in an Array.
     */
    reverse(): Float32Array {
        return this.toActual().reverse();
    }

    /**
     * Returns a section of an array.
     * @param start The beginning of the specified portion of the array.
     * @param end The end of the specified portion of the array.
     */
    slice(start?: number, end?: number): Float32Array {
        return this.toActual().slice(start, end);
    }

    /**
     * Determines whether the specified callback function returns true for any element of an array.
     * @param callbackfn A function that accepts up to three arguments. The some method calls the
     * callbackfn function for each element in array1 until the callbackfn returns true, or until
     * the end of the array.
     * @param thisArg An object to which the this keyword can refer in the callbackfn function.
     * If thisArg is omitted, undefined is used as the this value.
     */
    some(callbackfn: (value: number, index: number, array: Float32Array) => boolean, thisArg?: any): boolean {
        return this.toActual().some(callbackfn, thisArg);
    }

    /**
     * Gets a new Float32Array view of the ArrayBuffer store for this array, referencing the elements
     * at begin, inclusive, up to end, exclusive.
     * @param begin The index of the beginning of the array.
     * @param end The index of the end of the array.
     */
    subarray(begin: number, end?: number): Float32Array {
        return this.toActual().subarray(begin, end);
    }

    /** @protected */
    includes(searchElement: number, fromIndex?: number | undefined): boolean {
        return this.toActual().includes(searchElement, fromIndex);
    }
}
