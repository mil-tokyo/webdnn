/**
 * @module webdnn
 */
/** Don't Remove This comment block */

import { Placeholder } from "../placeholder";
import { GraphDescriptor } from "./graph_descriptor";

/**
 * @protected
 */
export interface GraphDescriptorWebassembly extends GraphDescriptor {
    unresolved_value_lists: { offset: number, placeholder: Placeholder }[][];
}
