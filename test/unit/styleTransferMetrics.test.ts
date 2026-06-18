import { describe, it, expect } from "vitest";
import { Metrics } from "../../example/style_transfer/harness/metrics.js";

describe("Metrics", () => {
  it("computes fps from frame timestamps over a window", () => {
    const m = new Metrics(4);
    [0, 100, 200, 300, 400].forEach((t) => m.frame(t)); // 100ms間隔 = 10fps
    expect(Math.round(m.fps())).toBe(10);
  });
  it("tracks last inference ms", () => {
    const m = new Metrics(4);
    m.inference(33);
    expect(m.lastMs()).toBe(33);
  });
  it("returns 0 fps before enough frames", () => {
    expect(new Metrics(4).fps()).toBe(0);
  });
});
