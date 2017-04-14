namespace WebDNN {
    export interface DNNDescriptorRunner {
        compile(): Promise<void>;
        loadWeights(weightsData: Float32Array): Promise<void>;
        run(): Promise<void>;
        getInputViews(): Promise<Float32Array[]>;
        getOutputViews(): Promise<Float32Array[]>;
    }
}
