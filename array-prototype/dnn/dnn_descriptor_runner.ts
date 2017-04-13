namespace WebDNN {
  export interface DNNDescriptorRunner {
    compile(): Promise<void>;
    loadWeights(weightsData: Float32Array): Promise<void>;
    run(): Promise<void>;
  }
}
