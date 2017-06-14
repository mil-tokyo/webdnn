/// <reference path="./graph_descriptor.ts" />

namespace WebDNN {
    export interface GraphDescriptorWebGPU extends GraphDescriptor {
        memory_layout: MemoryLayout;
        kernel_source: string;
        exec_infos: GraphDescriptorWebGPUExecInfos[];
    }

    export interface GraphDescriptorWebGPUExecInfos {
        entry_func_name: string;
        threadgroups_per_grid: WebGPUSize;
        threads_per_thread_group: WebGPUSize;
        meta_buffer: number[];
        unresolved_value_list: { offset: number, placeholder: PlaceHolder }[]
    }
}
