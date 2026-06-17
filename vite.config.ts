import { defineConfig } from "vite";

// Actual build is driven per-entry by scripts/build.mjs (Vite build API in a loop).
// This file provides shared defaults for IDE/`vite` standalone use.
export default defineConfig({
  build: {
    target: "es2020",
    minify: false,
    emptyOutDir: false,
  },
});
