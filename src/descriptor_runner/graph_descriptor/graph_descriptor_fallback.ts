/// <reference path="./graph_descriptor.ts" />

namespace WebDNN {
    export interface GraphDescriptorFallback extends GraphDescriptor {
        weight_allocation: {
            total_size: number;
            allocations: { [index: string]: { name: string, offset: number, size: number } }
        };
        variable_allocation: {
            total_size: number;
            allocations: { [index: string]: { name: string, offset: number, size: number } }
        };
        kernel_source: string;
        exec_infos: GraphDescriptorFallbackExecInfo[];
    }

    export interface GraphDescriptorFallbackExecInfo {
        entry_func_name: string;
        inputs: string[];
        outputs: string[];
        weights: string[];
        call_option: any;
    }
}
