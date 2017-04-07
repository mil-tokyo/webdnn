namespace WebDNN {
  export class DNNLayerIONames {
    inputs: string[];
    outputs: string[];
    weights: string[];

    constructor(inputs: string[], outputs: string[], weights: string[] = []) {
      this.inputs = inputs;
      this.outputs = outputs;
      this.weights = weights;
    }
  }
}
