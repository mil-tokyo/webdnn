/**
 * @module webdnn
 */
/** Don't Remove This comment block */

import { GraphDescriptor } from "./graph_descriptor";

/**
 * @protected
 */
export interface GraphDescriptorWebGL extends GraphDescriptor {
    shader_sources: { [name: string]: string }
    exec_infos: GraphDescriptorWebGLExecInfos[]
}


/**
 * @protected
 */
export interface GraphDescriptorWebGLExecInfos {
    shader_name: string,
    uniforms: { [name: string]: { type: 'int' | 'float', value: number } }
    inputs: { [name: string]: string }
    output: string
    width: number
}
