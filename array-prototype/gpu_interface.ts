// interface for $M.gpu

namespace WebDNN {
  export interface GPUInterface {
    init(): Promise<void>;
    createDNNDescriptorRunner(dnnDescriptor: any): DNNDescriptorRunner;
  }
}
