import { WebGLUniformItem } from "../../interface/backend/webgl/webglContext";
import { WebGLTensor } from "../../interface/backend/webgl/webglTensor";
import { Tensor } from "../../interface/core/tensor";

// Float encode: https://community.khronos.org/t/packing-multiple-floats-into-a-single-float-value/59320/3
export const shaderFloatPack = `
vec4 encode_float (float val) {
  if (val == 0.0) return vec4(0, 0, 0, 0);
  float sign = val > 0.0 ? 192.0 : 64.0;
  float absval = abs(val);
  float exponent = ceil(log2(absval) + 0.0001);
  float scaled = absval * exp2(-exponent);
  vec3 enc = vec3(1.0, 255.0, 65025.0) * scaled;
  enc = fract(enc);
  enc -= enc.yzz * vec3(1.0/255.0, 1.0/255.0, 0.0);
  return vec4((sign + clamp(exponent, -63.0, 63.0)) * (1.0 / 255.0), enc.x, enc.y, enc.z);
}

float decode_float(vec4 code) {
  if (code.x == 0.0) {
    return 0.0;
  }
  float ebyte = code.x * 255.0;
  float sign, exponent;
  if (ebyte >= 128.0) {
    sign = 1.0;
    exponent = ebyte - 192.0;
  } else {
    sign = -1.0;
    exponent = ebyte - 64.0;
  }
  float scaled = code.w * (1.0 / 65025.0) + code.z * (1.0 / 255.0) + code.y;
  float value = scaled * exp2(exponent) * sign;
  return value;
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
  }
  return shaderHeaderWebGL1 + shaderFloatPack;
}

export function shaderGenOutput(expr: string, webgl2: boolean): string {
  if (webgl2) {
    return `fragColor = vec4((${expr}), 0.0, 0.0, 0.0);`;
  }
  return `gl_FragColor = encode_float(${expr});`;
}

export function shaderGenOutputVec4(expr: string, webgl2: boolean): string {
  if (webgl2) {
    return `fragColor = (${expr});`;
  }
  throw new Error("shaderGenOutputVec4 is only for WebGL2");
}

export function shaderGenTensorNDGet(
  name: string,
  ndim: number,
  webgl2: boolean
): string {
  let args: string, flat_index: string, uniforms: string;
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
    case 5:
      uniforms = `
  uniform int ${name}_stride_0;
  uniform int ${name}_stride_1;
  uniform int ${name}_stride_2;
  uniform int ${name}_stride_3;
  uniform int ${name}_stride_4;
          `;
      args = "int d0, int d1, int d2, int d3, int d4";
      flat_index = `d0 * ${name}_stride_0 + d1 * ${name}_stride_1 + d2 * ${name}_stride_2 + d3 * ${name}_stride_3 + d4 * ${name}_stride_4`;
      break;
    case 6:
      uniforms = `
  uniform int ${name}_stride_0;
  uniform int ${name}_stride_1;
  uniform int ${name}_stride_2;
  uniform int ${name}_stride_3;
  uniform int ${name}_stride_4;
  uniform int ${name}_stride_5;
          `;
      args = "int d0, int d1, int d2, int d3, int d4, int d5";
      flat_index = `d0 * ${name}_stride_0 + d1 * ${name}_stride_1 + d2 * ${name}_stride_2 + d3 * ${name}_stride_3 + d4 * ${name}_stride_4 + d5 * ${name}_stride_5`;
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
  }
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

export function shaderGenTensorNDGetVec4(
  name: string,
  ndim: number,
  webgl2: boolean
): string {
  let args: string, flat_index: string, uniforms: string;
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
    case 5:
      uniforms = `
  uniform int ${name}_stride_0;
  uniform int ${name}_stride_1;
  uniform int ${name}_stride_2;
  uniform int ${name}_stride_3;
  uniform int ${name}_stride_4;
          `;
      args = "int d0, int d1, int d2, int d3, int d4";
      flat_index = `d0 * ${name}_stride_0 + d1 * ${name}_stride_1 + d2 * ${name}_stride_2 + d3 * ${name}_stride_3 + d4 * ${name}_stride_4`;
      break;
    case 6:
      uniforms = `
  uniform int ${name}_stride_0;
  uniform int ${name}_stride_1;
  uniform int ${name}_stride_2;
  uniform int ${name}_stride_3;
  uniform int ${name}_stride_4;
  uniform int ${name}_stride_5;
          `;
      args = "int d0, int d1, int d2, int d3, int d4, int d5";
      flat_index = `d0 * ${name}_stride_0 + d1 * ${name}_stride_1 + d2 * ${name}_stride_2 + d3 * ${name}_stride_3 + d4 * ${name}_stride_4 + d5 * ${name}_stride_5`;
      break;
    default:
      throw new Error();
  }
  if (webgl2) {
    return `
uniform sampler2D ${name};
${uniforms}

vec4 get_vec4_${name}(${args}) {
int flat_index = ${flat_index};
int texture_w = textureSize(${name}, 0).x;
int y = flat_index / texture_w;
int x = flat_index - y * texture_w;
return texelFetch(${name}, ivec2(x, y), 0);
}
`;
  }
  throw new Error("shaderGenTensorNDGetVec4 is only for WebGL2");
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
  const name = "tex_output",
    uniforms: WebGLUniformItem[] = [];
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
    case 5:
      source = `
    int tmp4 = tex_output_flat / tex_output_shape_4;
    int tex_output_4 = tex_output_flat - tmp4 * tex_output_shape_4;
    int tmp3 = tmp4 / tex_output_shape_3;
    int tex_output_3 = tmp4 - tmp3 * tex_output_shape_3;
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
    case 6:
      source = `
        int tmp5 = tex_output_flat / tex_output_shape_5;
        int tex_output_5 = tex_output_flat - tmp5 * tex_output_shape_5;
      int tmp4 = tmp5 / tex_output_shape_4;
      int tex_output_4 = tmp5 - tmp4 * tex_output_shape_4;
      int tmp3 = tmp4 / tex_output_shape_3;
      int tex_output_3 = tmp4 - tmp3 * tex_output_shape_3;
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

  /*
   * Gl_FragCoord.x 's precision is mediump, which only has 10bit precision
   * force casting to highp is needed in iOS. Also, "-0.5" cannot be removed.
   */
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
  }
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
