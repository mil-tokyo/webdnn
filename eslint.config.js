// @ts-check
import eslint from "@eslint/js";
import tseslint from "typescript-eslint";
import prettierConfig from "eslint-config-prettier";

export default tseslint.config(
  {
    ignores: [
      "dist/**",
      "node_modules/**",
      "src/descriptor_runner/operators/**/opEntries*.ts",
      "src/descriptor_runner/operators/webgpu/shaders.ts",
      "src/descriptor_runner/operators/wasm/worker/**",
      "src/descriptor_runner/onnx/**",
      "src/shader/**",
      "scripts/**",
    ],
  },
  eslint.configs.recommended,
  ...tseslint.configs.recommended,
  {
    files: ["src/descriptor_runner/**/*.ts"],
    languageOptions: {
      parserOptions: {
        project: "./tsconfig.json",
      },
    },
  },
  prettierConfig,
  // Rules relaxed for pre-existing code during ESLint 9 migration.
  // These were not enforced under the previous @typescript-eslint v4 ruleset,
  // so we down-grade them rather than mass-editing existing sources.
  {
    files: ["src/descriptor_runner/**/*.ts"],
    rules: {
      // Logging module uses ...args: any[] intentionally; also used throughout
      // for typed-but-unknown parameters in operator code.
      "@typescript-eslint/no-explicit-any": "off",

      // Pre-existing unused variables in operator files (nInputs, nOutputs,
      // option params, etc.) that are part of interface contracts.
      "@typescript-eslint/no-unused-vars": "off",

      // Empty interfaces/option types used intentionally as future extension
      // points (e.g. WebDNNWasmContextOption {}). Was covered by the now-removed
      // ban-types rule; no-empty-object-type is its v8 replacement but we keep
      // these stubs to avoid breaking the public API shape.
      "@typescript-eslint/no-empty-object-type": "off",

      // Long mathematical constants (SELU alpha/gamma) exceed float64 precision;
      // the extra digits are cosmetic but pre-existing and harmless.
      "no-loss-of-precision": "off",

      // Allow @ts-expect-error WITH a description (as used for legacy WebGPU API
      // suppressions added in Phase 4). Bare @ts-expect-error without description
      // remains an error.
      "@typescript-eslint/ban-ts-comment": [
        "error",
        { "ts-expect-error": "allow-with-description" },
      ],
    },
  }
);
