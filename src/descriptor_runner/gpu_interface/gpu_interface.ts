///<reference path="../descriptor_runner/descriptor_runner.ts" />

namespace WebDNN {
    export interface GPUInterface {
        init(): Promise<void>;
        createDescriptorRunner(): DescriptorRunner;
    }
}
