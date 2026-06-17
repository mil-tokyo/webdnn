import { describe, it, expect } from "vitest";
import { WebDNNCPUContextImpl } from "../../src/descriptor_runner/backend/cpu/cpuContextImpl";
import { CPUTensorImpl } from "../../src/descriptor_runner/backend/cpu/cpuTensorImpl";
import { getOpEntries } from "../../src/descriptor_runner/operators/cpu/operators/standard/unary";

describe("CPU Relu operator", () => {
  it("clamps negatives to zero, keeps positives", async () => {
    const ctx = new WebDNNCPUContextImpl();
    await ctx.initialize();

    const reluEntry = getOpEntries().find((e) => e.opType === "Relu");
    expect(reluEntry).toBeDefined();
    const relu = reluEntry!.factory();

    const input = new CPUTensorImpl([5], "float32", new Float32Array([-2, -0.5, 0, 1, 3]));
    const [output] = (await relu.run(ctx, [input])) as CPUTensorImpl[];

    expect(Array.from(output.data)).toEqual([0, 0, 0, 1, 3]);
    expect(Array.from(output.dims)).toEqual([5]);
  });
});
