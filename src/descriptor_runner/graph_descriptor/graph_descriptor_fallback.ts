/// <reference path="./graph_descriptor.ts" />

namespace WebDNN {
    export interface GraphDescriptorFallback extends GraphDescriptor {
        memory_layout: MemoryLayout;
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
