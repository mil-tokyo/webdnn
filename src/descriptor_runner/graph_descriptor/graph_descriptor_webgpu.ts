/**
 * @module webdnn
 */
/** Don't Remove This comment block */

import { Placeholder } from "../placeholder";
import { GraphDescriptor } from "./graph_descriptor";

/**
 * @protected
 */
export interface GraphDescriptorWebGPU extends GraphDescriptor {
    kernel_source: string;
    exec_infos: GraphDescriptorWebGPUExecInfos[];
}

/**
 * @protected
 */
export interface GraphDescriptorWebGPUExecInfos {
    entry_func_name: string;
    threadgroups_per_grid: WebGPUSize;
    threads_per_thread_group: WebGPUSize;
    meta_buffer: number[];
    unresolved_value_list: { offset: number, placeholder: Placeholder }[]
}
