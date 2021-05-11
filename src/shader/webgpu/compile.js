const glslang = require("@webgpu/glslang")();

const fs = require("fs");

let shaderList = "export const webgpuShaders = {\n";

// TODO: support custom/autogen

const sourcesDir = __dirname + "/shadersources/standard";

const files = fs.readdirSync(sourcesDir);
files.forEach((file) => {
  if (/^.*\.glsl$/.test(file)) {
    const shaderSource = fs.readFileSync(`${sourcesDir}/${file}`, {encoding: "utf-8"});
    const glslShader = glslang.compileGLSL(shaderSource, "compute");
    shaderList += `${file.split(".")[0]}: new Uint32Array([${Array.from(glslShader).toString()}]),\n`;
  }
});

shaderList += "};";

fs.writeFileSync(`${__dirname}/../../descriptor_runner/operators/webgpu/shaders.ts`, shaderList);
