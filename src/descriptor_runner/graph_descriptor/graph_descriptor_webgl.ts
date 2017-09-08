/**
 * @module webdnn
 */
/** Don't Remove This comment block */

import { Placeholder } from "../placeholder";
import { GraphDescriptor } from "./graph_descriptor";
import { Allocation, MemoryLayout, ResolvedAllocation } from "./memory_layout";

/**
 * @protecte
 */
export type ChannelMode = 'RGBA' | 'R';

/**
 * @protected
 */
export interface WebGLMemoryLayout extends MemoryLayout {
    'static': {
        size: -1,
        allocations: {
            [index: string]: ResolvedWebGLAllocation
        }
    },
    dynamic: {
        size: -1,
        allocations: {
            [index: string]: WebGLAllocation
        }
    }
}

/**
 * @protected
 */
export interface ResolvedWebGLAllocation extends ResolvedAllocation, WebGLAllocation {
    name: string,
    offset: -1,
    size: number
    width: number,
    height: number,
    channel_mode: ChannelMode
}

/**
 * @protected
 */
export interface WebGLAllocation extends Allocation {
    name: string,
    offset: -1,
    size: number | Placeholder
    width: number | Placeholder,
    height: number | Placeholder,
    channel_mode: ChannelMode
}

/**
 * @protected
 */
export interface GraphDescriptorWebGL extends GraphDescriptor {
    shader_sources: { [name: string]: string }
    exec_infos: GraphDescriptorWebGLExecInfos[],
    memory_layout: WebGLMemoryLayout,
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
