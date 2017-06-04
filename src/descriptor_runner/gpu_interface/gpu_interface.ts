///<reference path="../descriptor_runner/descriptor_runner.ts" />

namespace WebDNN {
    export abstract class GPUInterface<D extends GraphDescriptor, R extends DescriptorRunner<D>> {
        readonly backendName: string;

        constructor(option?: any) {}

        abstract init(): Promise<void>;

        abstract createDescriptorRunner(): R;
    }
}
