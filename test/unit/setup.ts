// Stub browser globals required by src/descriptor_runner/logging.ts
// which accesses `window.WebDNNLoggingManagerInstance` at module load time.
if (typeof globalThis.window === "undefined") {
  (globalThis as Record<string, unknown>).window = globalThis;
}
