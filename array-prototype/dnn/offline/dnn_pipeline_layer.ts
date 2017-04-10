namespace WebDNN {
  export interface DNNPipelineLayer {
    getKernels(ioBuffer: DNNPipelineLayerIOBuffer): DNNPipelineKernel[];
  }
}
