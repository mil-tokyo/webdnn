/**
 * @module webdnn
 */
/** Don't Remove This comment block */

import { GraphDescriptor } from "./graph_descriptor";

/**
 * @protecte
 */
export type ChannelMode = 'RGBA' | 'R';

/**
 * @protected
 */
export interface GraphDescriptorWebGL extends GraphDescriptor {
    shader_sources: { [name: string]: string }
    exec_infos: GraphDescriptorWebGLExecInfos[],
    variables: {
        [variable_name: string]: {
            variable_size: number
            allocation_name: string
        }
    },
    allocations: {
        [allocation_name: string]: {
            allocation_size: number,
            channel_mode: ChannelMode
        }
    },
    constants_map: {
        [variable_name: string]: {
            size: number,
            byte_offset: number
        }
    }
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
        uniform_name: string,
        value: number
    }]
    output: string
    width: number
}
