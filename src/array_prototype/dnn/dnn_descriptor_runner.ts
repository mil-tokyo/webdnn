namespace WebDNN {
    export interface DNNDescriptorRunner {
        load(directory: string): Promise<void>;
        setDescriptor(descriptor: any): void;
        compile(): Promise<void>;
        loadWeights(weightsData: Uint8Array): Promise<void>;
        run(): Promise<void>;
        getInputViews(): Promise<Float32Array[]>;
        getOutputViews(): Promise<Float32Array[]>;
    }
}
