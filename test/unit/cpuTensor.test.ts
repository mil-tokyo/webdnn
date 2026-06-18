import { describe, it, expect } from "vitest";
import { CPUTensorImpl } from "../../src/descriptor_runner/backend/cpu/cpuTensorImpl";

describe("CPUTensorImpl", () => {
  it("allocates zero-filled data when none is given", () => {
    const t = new CPUTensorImpl([2, 3], "float32");
    expect(t.data).toBeInstanceOf(Float32Array);
    expect(t.data.length).toBe(6);
    expect(t.length).toBe(6);
    expect(t.ndim).toBe(2);
    expect(Array.from(t.dims)).toEqual([2, 3]);
  });

  it("computes strides matching the implementation", () => {
    const t = new CPUTensorImpl([2, 3], "float32");
    expect(Array.from(t.strides)).toEqual([3, 1]);
  });

  it("wraps an external buffer", () => {
    const buf = new Float32Array([1, 2, 3, 4, 5, 6]);
    const t = new CPUTensorImpl([2, 3], "float32", buf);
    expect(t.data).toBe(buf);
    expect(t.useExternalBuffer).toBe(true);
  });

  it("getValue / setValue use index math", () => {
    const t = new CPUTensorImpl([2, 3], "float32", new Float32Array([1, 2, 3, 4, 5, 6]));
    expect(t.getValue([0, 0])).toBe(1);
    expect(t.getValue([1, 2])).toBe(6);
    t.setValue(99, [1, 1]);
    expect(t.getValue([1, 1])).toBe(99);
  });

  it("respects int32 dataType", () => {
    const t = new CPUTensorImpl([2], "int32");
    expect(t.data).toBeInstanceOf(Int32Array);
    expect(t.dataType).toBe("int32");
  });
});
