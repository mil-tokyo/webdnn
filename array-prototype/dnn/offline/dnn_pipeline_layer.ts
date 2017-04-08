namespace WebDNN {
  export interface DNNPipelineLayer {
    getKernels(inputs: DNNPipelineBuffer[], outputs: DNNPipelineBuffer[], weights: DNNPipelineBuffer[]): DNNPipelineKernel[];
  }
}