import { Tensor } from "../../../../interface/core/tensor";
import { OperatorEntry } from "../../../../interface/core/operator";
import { Pad11 } from "../../../base/pad11";
import {
  WebDNNWebGLContext,
  WebGLUniformItem,
} from "../../../../interface/backend/webgl/webglContext";
import {
  shaderGenHeader,
  shaderGenOutput,
  shaderGenTensorNDGet,
  shaderGenTensorNDGetUniformItem,
  shaderGenTensorOutputCoordsWithReturn,
  shaderGenTensorOutputUniform,
  shaderGenTensorOutputUniformItem,
} from "../../shaderHelper";
import { arange } from "../../../../util";

/*
 * Opset 11
 * opset 2は互換性なし
 */
class WebGLPad11 extends Pad11 {
  constructor() {
    super("webgl");
  }

  async run(context: WebDNNWebGLContext, inputs: Tensor[]): Promise<Tensor[]> {
    const [input, shapeTensor, constantValueTensor] = inputs;
    context.assertsWebGLTensor(input);
    context.cpuContext.assertsCPUTensor(shapeTensor);
    const { outputShape: outShape, pads } = this.calcShape(input, shapeTensor);
    let constantValue = 0;
    if (constantValueTensor) {
      context.cpuContext.assertsCPUTensor(constantValueTensor);
      constantValue = constantValueTensor.data[0];
    }
    const output = context.emptyTensor(outShape, "float32");
    const kernelName = `pad_${outShape.length}_${this.mode}`;
    const padUniforms = arange(outShape.length)
      .map((dim) => `uniform int pad${dim};`)
      .join("");
    const inShapeUniforms = arange(outShape.length)
      .map((dim) => `uniform int inShape${dim};`)
      .join("");
    const constantUniform =
      this.mode === "constant" ? "uniform float padConstant;" : "";
    const tex_input_idxs = arange(outShape.length)
      .map((dim) => `ti${dim}`)
      .join(",");
    const minusPad = arange(outShape.length)
      .map((dim) => `int ti${dim} = tex_output_${dim} - pad${dim};`)
      .join("");
    const outOfBoundCond = arange(outShape.length)
      .map((dim) => `ti${dim} < 0 || ti${dim} >= inShape${dim}`)
      .join("||");
    let indexAdjuster: string;
    let valueGetter: string;
    switch (this.mode) {
      case "constant":
        indexAdjuster = "";
        valueGetter = `if (${outOfBoundCond}) {s = padConstant;} else {s = get_tex_input(${tex_input_idxs});}`;
        break;
      case "edge":
        indexAdjuster = arange(outShape.length)
          .map(
            (dim) =>
              `if (ti${dim} < 0) {ti${dim} = 0;} else if (ti${dim} >= inShape${dim}) {ti${dim} = inShape${dim} - 1;}`
          )
          .join("");
        valueGetter = `s = get_tex_input(${tex_input_idxs});`;
        break;
      case "reflect":
        indexAdjuster = arange(outShape.length)
          .map(
            (dim) =>
              `if (ti${dim} < 0) {ti${dim} = pad_mod(-ti${dim}, inShape${dim} * 2 - 2); if (ti${dim} >= inShape${dim}) {ti${dim} = inShape${dim} * 2 - ti${dim} - 2;}} else if (ti${dim} >= inShape${dim}) {ti${dim} = pad_mod(ti${dim}, inShape${dim} * 2 - 2); if (ti${dim} >= inShape${dim}) {ti${dim} = inShape${dim} * 2 - ti${dim} - 2;}}`
          )
          .join("");
        valueGetter = `s = get_tex_input(${tex_input_idxs});`;
        break;
    }
    const kernelSource = `${shaderGenHeader(context.webgl2)}
int pad_mod(int x, int y) {
    int z = x / y;
    return x - z * y;
}
${padUniforms}
${constantUniform}
${inShapeUniforms}
${shaderGenTensorOutputUniform(outShape.length)}

${shaderGenTensorNDGet("tex_input", input.ndim, context.webgl2)}

void main() {
${shaderGenTensorOutputCoordsWithReturn(outShape.length)}
${minusPad}
${indexAdjuster}
float s;
${valueGetter}
${shaderGenOutput("s", context.webgl2)}
return;
}
`;
    context.addKernel(kernelName, kernelSource);

    const uniforms: WebGLUniformItem[] = [
      ...shaderGenTensorNDGetUniformItem(
        "tex_input",
        input.strides,
        input,
        context.webgl2
      ),
      ...shaderGenTensorOutputUniformItem(outShape, output, context.webgl2),
    ];
    for (let dim = 0; dim < outShape.length; dim++) {
      uniforms.push({ name: `pad${dim}`, value: pads[dim], type: "int" });
      uniforms.push({
        name: `inShape${dim}`,
        value: input.dims[dim],
        type: "int",
      });
    }
    if (this.mode === "constant") {
      uniforms.push({
        name: "padConstant",
        value: constantValue,
        type: "float",
      });
    }
    await context.runKernel(
      kernelName,
      [{ tensor: input, name: "tex_input" }],
      output,
      uniforms
    );
    return [output];
  }
}

export function getOpEntries(): OperatorEntry[] {
  return [
    {
      opType: "Pad",
      backend: "webgl",
      opsetMin: 11,
      factory: () => new WebGLPad11(),
    },
  ];
}
