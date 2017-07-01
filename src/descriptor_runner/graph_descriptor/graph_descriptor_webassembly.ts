/// <reference path="./graph_descriptor.ts" />

namespace WebDNN {
    export interface GraphDescriptorWebassembly extends GraphDescriptor {
        unresolved_value_lists: { offset: number, placeholder: Placeholder }[][];
    }
}
