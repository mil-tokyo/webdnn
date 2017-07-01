///<reference path="./placeholder.ts" />

namespace WebDNN {
    export interface Allocation {
        name: string,
        offset: number | Placeholder,
        size: number | Placeholder
    }

    export interface ResolvedAllocation extends Allocation {
        offset: number,
        size: number
    }

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
}
