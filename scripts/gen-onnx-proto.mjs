import { execFileSync } from "node:child_process";
import { existsSync } from "node:fs";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const proto = resolve(root, "scripts", "onnx.proto");
const outDir = resolve(root, "src", "descriptor_runner", "onnx");
const jsOut = resolve(outDir, "onnx.js");
const dtsOut = resolve(outDir, "onnx.d.ts");

if (!existsSync(proto)) {
  console.error("Missing scripts/onnx.proto. Download:\n  curl -L -o scripts/onnx.proto https://raw.githubusercontent.com/onnx/onnx/v1.17.0/onnx/onnx.proto");
  process.exit(1);
}
execFileSync("npx", ["pbjs", "-t", "static-module", "-w", "es6", "--es6", "-o", jsOut, proto], { stdio: "inherit", cwd: root });
execFileSync("npx", ["pbts", "-o", dtsOut, jsOut], { stdio: "inherit", cwd: root });
console.log("generated", jsOut, dtsOut);
