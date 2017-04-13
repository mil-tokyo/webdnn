namespace WebDNN {
  export class DNNDescriptorRunnerFallback implements DNNDescriptorRunner {
    constructor(public descriptor: DNNDescriptorFallback) {
      throw new Error('Not implemented');
    }
    async compile(): Promise<void> {
    }
    async loadWeights(weightsData: Float32Array): Promise<void> {
      // when weight format becomes not flat array (such as using quantization), the interface should be changed
    }
    run(): Promise<void> {
      throw new Error('Not implemented');
    }
    async getInputViews(): Promise<Float32Array[]> {
      throw new Error('Not implemented');
    }
    async getOutputViews(): Promise<Float32Array[]> {
      throw new Error('Not implemented');
    }
  }
  export interface DNNDescriptorFallback {
  }
}
