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
    uniforms: {
        [name: string]: {
            type: 'int' | 'float' | 'vec2' | 'vec4' | 'sampler2D',
            value: number
        }
    }
    inputs: [{
        variable_name: string,
        uniform_name: string
    }]
    output: string
    width: number
}
