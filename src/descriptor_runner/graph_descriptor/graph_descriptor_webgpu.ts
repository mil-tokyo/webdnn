/// <reference path="./graph_descriptor.ts" />

namespace WebDNN {
    export interface GraphDescriptorWebGPU extends GraphDescriptor {
        weight_allocation: {
            total_size: number;
            allocation: { [index: string]: { name: string, offset: number, size: number } }
        };
        variable_allocation: {
            total_size: number;
            allocation: { [index: string]: { name: string, offset: number, size: number } }
        };
        kernel_source: string;
        exec_infos: GraphDescriptorWebGPUExecInfos[];
    }

    export interface GraphDescriptorWebGPUExecInfos {
        entry_func_name: string;
        threadgroups_per_grid: WebGPUSize;
        threads_per_thread_group: WebGPUSize;
        meta_buffer: number[];
    }
}
