namespace WebDNN {
  export class DNNPipelineGenerator {
    constructor() {

    }

    generate(dnnGraph: DNNGraph): DNNPipelineData {
      // calculate buffer size
      let weight_buffers_assignment = this.calculateBufferAssignment(dnnGraph.weight_shapes);
      let data_buffers_assignment = this.calculateBufferAssignment(dnnGraph.data_shapes);

      // generate kernel for each layer
      let kernels: DNNPipelineKernel[] = [];
      for (let layer_idx = 0; layer_idx < dnnGraph.layers.length; layer_idx++) {
        let layer = dnnGraph.layers[layer_idx];
        let layer_inputs: DNNPipelineBuffer[] =
          layer.bottoms.map((data_idx) => { return data_buffers_assignment.buffers[data_idx]; });
        let layer_outputs: DNNPipelineBuffer[] =
          layer.tops.map((data_idx) => { return data_buffers_assignment.buffers[data_idx]; });
        let layer_weights: DNNPipelineBuffer[] =
          layer.weights.map((weight_idx) => { return weight_buffers_assignment.buffers[weight_idx]; });
        let layer_instance: DNNPipelineLayer;
        switch (layer.type) {
          case 'relu':
            layer_instance = new DNNPipelineReluLayer(layer.params);
            break;
          default:
            throw new Error('Unknown layer');
        }
        let layer_kernels = layer_instance.getKernels(layer_inputs, layer_outputs, layer_weights);
        Array.prototype.push.apply(kernels, layer_kernels);
      }

      return {
        weightBuffersAssignment: weight_buffers_assignment,
        dataBuffersAssignment: data_buffers_assignment,
        kernels: kernels
      };
    }

    calculateBufferAssignment(shapes: number[][]): { buffers: DNNPipelineBuffer[], totalSize: number } {
      let offset = 0;
      let buffers: DNNPipelineBuffer[] = [];
      for (let i = 0; i < shapes.length; i++) {
        let shape = shapes[i];
        let size = 1;
        for (let j = 0; j < shape.length; j++) {
          size *= shape[j];
        }
        buffers.push({ shape: shape, offset: offset, size: size });
        offset += size;
      }

      return { buffers: buffers, totalSize: offset };
    }
  }

  export interface DNNGraph {
    layers: DNNGraphLayer[];
    inputs: number[];
    outputs: number[];
    data_shapes: number[][];
    weight_shapes: number[][];
  }

  export interface DNNGraphLayer {
    name: string;
    type: string;
    params: any;
    bottoms: number[];
    tops: number[];
    weights: number[];
  }

  export interface DNNPipelineBuffer {
    shape: number[];
    offset: number;// unit: sizeof(float)
    size: number;// unit: sizeof(float)
  }

  export class DNNPipelineKernel {
    threadgroupsPerGrid: WebGPUSize;
    threadsPerThreadgroup: WebGPUSize;
    kernelString: string;
    kernelFunctionName: string;
  }

  export interface DNNPipelineWeightBufferAssignment {
    buffers: DNNPipelineBuffer[];
    totalSize: number;
  }

  export interface DNNPipelineDataBufferAssignment {
    buffers: DNNPipelineBuffer[];
    totalSize: number;
  }

  export interface DNNPipelineData {
    weightBuffersAssignment: DNNPipelineWeightBufferAssignment;
    dataBuffersAssignment: DNNPipelineDataBufferAssignment;
    kernels: DNNPipelineKernel[];
  }
}
