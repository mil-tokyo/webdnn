/**
 * @module webdnn
 */
/** Don't Remove This comment block */

import { Placeholder } from "../placeholder";

/**
 * @protected
 */
export interface Allocation {
    name: string,
    offset: number | Placeholder,
    size: number | Placeholder
}

/**
 * @protected
 */
export interface ResolvedAllocation extends Allocation {
    offset: number,
    size: number
}

/**
 * @protected
 */
export interface MemoryLayout {
    'static': {
        size: number,
        allocations: {
            [index: string]: ResolvedAllocation
        }
    },
    dynamic: {
        size: number | Placeholder,
        allocations: {
            [index: string]: Allocation
        }
    }
}
