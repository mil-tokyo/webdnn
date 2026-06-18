import { build } from "vite";
import { copyFileSync, rmSync } from "node:fs";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const outDir = resolve(root, "dist");

const targets = [
  { file: "webdnn.js", entry: "src/descriptor_runner/index.ts", name: "WebDNN", format: "umd" },
  { file: "webdnn-core.js", entry: "src/descriptor_runner/separateBuild/coreOnly.ts", name: "WebDNN", format: "umd" },
  { file: "op-cpu.js", entry: "src/descriptor_runner/separateBuild/operatorCPU.ts", format: "iife" },
  { file: "op-wasm.js", entry: "src/descriptor_runner/separateBuild/operatorWasm.ts", format: "iife" },
  { file: "op-webgpu.js", entry: "src/descriptor_runner/separateBuild/operatorWebGPU.ts", format: "iife" },
  { file: "op-webgl-base.js", entry: "src/descriptor_runner/separateBuild/operatorWebGL.ts", format: "iife" },
];

for (const t of targets) {
  await build({
    configFile: false,
    logLevel: "warn",
    build: {
      target: "es2020",
      minify: false,
      emptyOutDir: false,
      outDir,
      lib: {
        entry: resolve(root, t.entry),
        formats: [t.format],
        name: t.name ?? "WebDNNOp",
        fileName: () => t.file,
      },
    },
  });
  console.log("built", t.file);
}

const webglBase = resolve(outDir, "op-webgl-base.js");
for (const name of ["op-webgl1-4096.js", "op-webgl1-16384.js", "op-webgl2-4096.js", "op-webgl2-16384.js"]) {
  copyFileSync(webglBase, resolve(outDir, name));
  console.log("copied", name);
}
// Remove the intermediate base bundle so dist/ ships exactly the 9 contract files.
rmSync(webglBase);
console.log("done");
