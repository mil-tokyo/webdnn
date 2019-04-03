/**
 * @module webdnn
 */
/** Don't Remove This comment block */

import { Placeholder } from "../placeholder";
import { GraphDescriptor } from "./graph_descriptor";

/**
 * @protected
 */
export interface GraphDescriptorWebMetal extends GraphDescriptor {
    kernel_source: string;
    exec_infos: GraphDescriptorWebMetalExecInfos[];
}

/**
 * @protected
 */
export interface GraphDescriptorWebMetalExecInfos {
    entry_func_name: string;
    threadgroups_per_grid: WebMetalSize;
    threads_per_thread_group: WebMetalSize;
    meta_buffer: number[];
    unresolved_value_list: { offset: number, placeholder: Placeholder }[]
}
