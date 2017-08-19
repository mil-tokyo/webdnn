/**
 * @module webdnn
 */
/** Don't Remove This comment block */

import { GraphDescriptor } from "./graph_descriptor";

/**
 * @protected
 */
export interface GraphDescriptorFallback extends GraphDescriptor {
    kernel_source: string;
    exec_infos: GraphDescriptorFallbackExecInfo[];
}

/**
 * @protected
 */
export interface GraphDescriptorFallbackExecInfo {
    entry_func_name: string;
    inputs: string[];
    outputs: string[];
    weights: string[];
    call_option: any;
}
