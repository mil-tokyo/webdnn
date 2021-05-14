import { WebGLUniformItem } from "../../interface/backend/webgl/webglContext";
import { WebGLTensor } from "../../interface/backend/webgl/webglTensor";
import { Tensor } from "../../interface/core/tensor";

// float encode: https://stackoverflow.com/questions/17981163/webgl-read-pixels-from-floating-point-render-target/20859830#20859830
export const shaderFloatPack = `
float shift_right (float v, float amt) { 
  v = floor(v) + 0.5; 
  return floor(v / exp2(amt)); 
}
float shift_left (float v, float amt) { 
  return floor(v * exp2(amt) + 0.5); 
}
float mask_last (float v, float bits) { 
  return mod(v, shift_left(1.0, bits)); 
}
float extract_bits (float num, float from, float to) { 
  from = floor(from + 0.5); to = floor(to + 0.5); 
  return mask_last(shift_right(num, from), to - from); 
}
vec4 encode_float (float val) { 
  if (val == 0.0) return vec4(0, 0, 0, 0); 
  float sign = val > 0.0 ? 0.0 : 1.0; 
  val = abs(val); 
  float exponent = floor(log2(val)); 
  float biased_exponent = exponent + 127.0; 
  float fraction = ((val / exp2(exponent)) - 1.0) * 8388608.0; 
  float t = biased_exponent / 2.0; 
  float last_bit_of_biased_exponent = fract(t) * 2.0; 
  float remaining_bits_of_biased_exponent = floor(t); 
  float byte4 = extract_bits(fraction, 0.0, 8.0) / 255.0; 
  float byte3 = extract_bits(fraction, 8.0, 16.0) / 255.0; 
  float byte2 = (last_bit_of_biased_exponent * 128.0 + extract_bits(fraction, 16.0, 23.0)) / 255.0; 
  float byte1 = (sign * 128.0 + remaining_bits_of_biased_exponent) / 255.0; 
  return vec4(byte4, byte3, byte2, byte1); 
}

float decode_float(vec4 code) {
  if (all(equal(code, vec4(0.0)))) {
    return 0.0;
  }
  vec4 bytes = code * 255.0;
  float sign = bytes.w >= 128.0 ? -1.0 : 1.0;
  float biased_exponent = shift_left(extract_bits(bytes.w, 0.0, 7.0), 1.0) + extract_bits(bytes.z, 7.0, 8.0);
  float fraction = (extract_bits(bytes.z, 0.0, 7.0) * 65536.0 + bytes.y * 256.0 + bytes.x) / 8388608.0;
  float v = (fraction + 1.0) * exp2(biased_exponent - 127.0) * sign;
  return v;
}
`;

export const shaderHeaderWebGL1 = `#version 100
precision highp float;
precision highp int;
precision highp sampler2D;
`;

export const shaderHeaderWebGL2 = `#version 300 es
precision highp float;
precision highp int;
precision highp sampler2D;
out vec4 fragColor;
`;

export function shaderGenHeader(webgl2: boolean): string {
  if (webgl2) {
    return shaderHeaderWebGL2;
  } else {
    return shaderHeaderWebGL1 + shaderFloatPack;
  }
}

export function shaderGenOutput(expr: string, webgl2: boolean): string {
  if (webgl2) {
    return `fragColor = vec4((${expr}), 0.0, 0.0, 0.0);`;
  } else {
    return `gl_FragColor = encode_float(${expr});`;
  }
}

export function shaderGenTensorNDGet(
  name: string,
  ndim: number,
  webgl2: boolean
): string {
  let uniforms: string;
  let args: string;
  let flat_index: string;
  switch (ndim) {
    case 0:
      uniforms = "";
      args = "";
      flat_index = "0";
      break;
    case 1:
      uniforms = `
  uniform int ${name}_stride_0;
          `;
      args = "int d0";
      flat_index = `d0 * ${name}_stride_0`;
      break;
    case 2:
      uniforms = `
    uniform int ${name}_stride_0;
    uniform int ${name}_stride_1;
            `;
      args = "int d0, int d1";
      flat_index = `d0 * ${name}_stride_0 + d1 * ${name}_stride_1`;
      break;
    case 3:
      uniforms = `
      uniform int ${name}_stride_0;
      uniform int ${name}_stride_1;
      uniform int ${name}_stride_2;
              `;
      args = "int d0, int d1, int d2";
      flat_index = `d0 * ${name}_stride_0 + d1 * ${name}_stride_1 + d2 * ${name}_stride_2`;
      break;
    case 4:
      uniforms = `
uniform int ${name}_stride_0;
uniform int ${name}_stride_1;
uniform int ${name}_stride_2;
uniform int ${name}_stride_3;
        `;
      args = "int d0, int d1, int d2, int d3";
      flat_index = `d0 * ${name}_stride_0 + d1 * ${name}_stride_1 + d2 * ${name}_stride_2 + d3 * ${name}_stride_3`;
      break;
    default:
      throw new Error();
  }
  if (webgl2) {
    return `
uniform sampler2D ${name};
${uniforms}

float get_${name}(${args}) {
int flat_index = ${flat_index};
int texture_w = textureSize(${name}, 0).x;
int y = flat_index / texture_w;
int x = flat_index - y * texture_w;
return texelFetch(${name}, ivec2(x, y), 0).r;
}
`;
  } else {
    return `
    uniform sampler2D ${name};
    ${uniforms}
    uniform int ${name}_texture_w;
    uniform int ${name}_texture_h;
    
    float get_${name}(${args}) {
      int flat_index = ${flat_index};
      int texture_w = ${name}_texture_w;
      int y = flat_index / texture_w;
      int x = flat_index - y * texture_w;
      vec4 p = texture2D(${name}, vec2((float(x) + 0.5) / float(${name}_texture_w), (float(y) + 0.5) / float(${name}_texture_h)));
      return decode_float(p);
    }
`;
  }
}

function isWebGLTensor(tensor: unknown): tensor is WebGLTensor {
  return typeof tensor === "object" && (tensor as Tensor).backend === "webgl";
}

export function shaderGenTensorNDGetUniformItem(
  name: string,
  strides: ReadonlyArray<number>,
  textureShape: ReadonlyArray<number> | WebGLTensor,
  webgl2: boolean
): WebGLUniformItem[] {
  let textureShapeArray: ReadonlyArray<number>;
  if (isWebGLTensor(textureShape)) {
    textureShapeArray = [textureShape.textureHeight, textureShape.textureWidth];
  } else {
    textureShapeArray = textureShape;
  }
  const uniforms: WebGLUniformItem[] = [];
  for (let i = 0; i < strides.length; i++) {
    uniforms.push({
      name: `${name}_stride_${i}`,
      type: "int",
      value: strides[i],
    });
  }
  if (!webgl2) {
    uniforms.push({
      name: `${name}_texture_h`,
      type: "int",
      value: textureShapeArray[0],
    });
    uniforms.push({
      name: `${name}_texture_w`,
      type: "int",
      value: textureShapeArray[1],
    });
  }
  return uniforms;
}

export function shaderGenTensorOutputUniformItem(
  shape: ReadonlyArray<number>,
  textureShape: ReadonlyArray<number> | WebGLTensor,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  webgl2: boolean
): WebGLUniformItem[] {
  let textureShapeArray: ReadonlyArray<number>;
  if (isWebGLTensor(textureShape)) {
    textureShapeArray = [textureShape.textureHeight, textureShape.textureWidth];
  } else {
    textureShapeArray = textureShape;
  }
  const name = "tex_output";
  const uniforms: WebGLUniformItem[] = [];
  for (let i = 0; i < shape.length; i++) {
    uniforms.push({
      name: `${name}_shape_${i}`,
      type: "int",
      value: shape[i],
    });
  }
  uniforms.push({
    name: `${name}_texture_w`,
    type: "int",
    value: textureShapeArray[1],
  });
  return uniforms;
}

export function shaderGenTensorOutputUniform(ndim: number): string {
  let source = `
  uniform int tex_output_texture_w;
`;
  for (let i = 0; i < ndim; i++) {
    source += `uniform int tex_output_shape_${i};`;
  }
  return source;
}

export function shaderGenTensorOutputCoordsWithReturn(ndim: number): string {
  let source: string;
  switch (ndim) {
    case 0:
      source = `
    int tex_output_0 = 0;
    if (tex_output_0 >= 1) {
      return;
    }
    `;
      break;
    case 1:
      source = `
    int tex_output_0 = tex_output_flat;
    if (tex_output_0 >= tex_output_shape_0) {
      return;
    }
    `;
      break;
    case 2:
      source = `
    int tmp1 = tex_output_flat / tex_output_shape_1;
    int tex_output_1 = tex_output_flat - tmp1 * tex_output_shape_1;
    int tex_output_0 = tmp1;
    if (tex_output_0 >= tex_output_shape_0) {
      return;
    }
    `;
      break;
    case 3:
      source = `
    int tmp2 = tex_output_flat / tex_output_shape_2;
    int tex_output_2 = tex_output_flat - tmp2 * tex_output_shape_2;
    int tmp1 = tmp2 / tex_output_shape_1;
    int tex_output_1 = tmp2 - tmp1 * tex_output_shape_1;
    int tex_output_0 = tmp1;
    if (tex_output_0 >= tex_output_shape_0) {
      return;
    }
    `;
      break;
    case 4:
      source = `
    int tmp3 = tex_output_flat / tex_output_shape_3;
    int tex_output_3 = tex_output_flat - tmp3 * tex_output_shape_3;
    int tmp2 = tmp3 / tex_output_shape_2;
    int tex_output_2 = tmp3 - tmp2 * tex_output_shape_2;
    int tmp1 = tmp2 / tex_output_shape_1;
    int tex_output_1 = tmp2 - tmp1 * tex_output_shape_1;
    int tex_output_0 = tmp1;
    if (tex_output_0 >= tex_output_shape_0) {
      return;
    }
    `;
      break;
    default:
      throw new Error();
  }

  // gl_FragCoord.x 's precision is mediump, which only has 10bit precision
  // force casting to highp is needed in iOS. Also, "-0.5" cannot be removed.
  return `
  highp float helper_gfcx = gl_FragCoord.x;
  highp float helper_gfcy = gl_FragCoord.y;
  int tex_output_flat = int(helper_gfcx - 0.5) + tex_output_texture_w * int(helper_gfcy - 0.5);
  ${source}
  `;
}

export function shaderGenTensorElementwiseGet(
  name: string,
  webgl2: boolean
): string {
  if (webgl2) {
    return `
uniform sampler2D ${name};

float get_${name}() {
  return texelFetch(${name}, ivec2(int(gl_FragCoord.x), int(gl_FragCoord.y)), 0).r;
}
`;
  } else {
    return `
uniform sampler2D ${name};
uniform int ${name}_texture_w;
uniform int ${name}_texture_h;

float get_${name}() {
  vec4 p = texture2D(${name}, vec2(gl_FragCoord.x / float(${name}_texture_w), gl_FragCoord.y / float(${name}_texture_h)));
  return decode_float(p);
}
`;
  }
}

export function shaderGenTensorElementwiseGetUniformItem(
  name: string,
  textureShape: ReadonlyArray<number> | WebGLTensor,
  webgl2: boolean
): WebGLUniformItem[] {
  let textureShapeArray: ReadonlyArray<number>;
  if (isWebGLTensor(textureShape)) {
    textureShapeArray = [textureShape.textureHeight, textureShape.textureWidth];
  } else {
    textureShapeArray = textureShape;
  }
  const uniforms: WebGLUniformItem[] = [];
  if (!webgl2) {
    uniforms.push({
      name: `${name}_texture_h`,
      type: "int",
      value: textureShapeArray[0],
    });
    uniforms.push({
      name: `${name}_texture_w`,
      type: "int",
      value: textureShapeArray[1],
    });
  }
  return uniforms;
}
