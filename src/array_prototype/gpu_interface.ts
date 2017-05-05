///<reference path="./dnn/dnn_descriptor_runner.ts" />

// interface for $M.gpu

namespace WebDNN {
    export interface GPUInterface {
        init(): Promise<void>;
        createDNNDescriptorRunner(): DNNDescriptorRunner;
    }
}
