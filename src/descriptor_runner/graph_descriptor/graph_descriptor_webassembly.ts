/// <reference path="./graph_descriptor.ts" />

namespace WebDNN {
    export interface GraphDescriptorWebassembly extends GraphDescriptor {
        weight_allocation: {
            total_size: number;
            allocation: { [index: string]: { name: string, offset: number, size: number } }
        };
        variable_allocation: {
            total_size: number;
            allocation: { [index: string]: { name: string, offset: number, size: number } }
        };
    }
}
