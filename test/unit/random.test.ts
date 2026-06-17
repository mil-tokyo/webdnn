import { describe, it, expect } from "vitest";
import { Random } from "../../src/descriptor_runner/math/random";

describe("Random", () => {
  it("is deterministic for a fixed seed", () => {
    const a = new Random(42);
    const b = new Random(42);
    const seqA = [a.random(), a.random(), a.random()];
    const seqB = [b.random(), b.random(), b.random()];
    expect(seqA).toEqual(seqB);
  });

  it("produces scalars in [0, 1)", () => {
    const r = new Random(1);
    for (let i = 0; i < 100; i++) {
      const v = r.random();
      expect(v).toBeGreaterThanOrEqual(0);
      expect(v).toBeLessThan(1);
    }
  });

  it("random(size) returns a Float32Array of that length", () => {
    const r = new Random(7);
    const vec = r.random(5);
    expect(vec).toBeInstanceOf(Float32Array);
    expect(vec.length).toBe(5);
  });

  it("different seeds diverge", () => {
    const a = new Random(1).random();
    const b = new Random(2).random();
    expect(a).not.toBe(b);
  });
});
