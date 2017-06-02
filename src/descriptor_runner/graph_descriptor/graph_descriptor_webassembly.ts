/// <reference path="./graph_descriptor.ts" />

namespace WebDNN {
    export interface GraphDescriptorWebassembly extends GraphDescriptor {
        memory_layout: MemoryLayout
    }
}
