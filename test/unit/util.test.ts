import { describe, it, expect } from "vitest";
import { intOrLongToInt, intOrLongToIntVector } from "../../src/descriptor_runner/util";

describe("intOrLongToInt", () => {
  it("passes through plain numbers", () => {
    expect(intOrLongToInt(264)).toBe(264);
    expect(intOrLongToInt(-5)).toBe(-5);
  });

  it("converts a Long-like object whose `instanceof Long` is false", () => {
    // protobufjs builds Long from its own copy of `long`, so `instanceof Long`
    // is false for a genuine Long. Such values must still be converted to a
    // number, otherwise `number + Long` string-concatenates downstream.
    expect(intOrLongToInt({ low: 0, high: 0, unsigned: false } as never)).toBe(0);
    expect(intOrLongToInt({ low: 9, high: 0, unsigned: false } as never)).toBe(9);
    expect(intOrLongToInt({ low: 256, high: 0, unsigned: false } as never)).toBe(256);
  });

  it("regression: Conv pads must add, not string-concatenate (264 + 0 + 0 === 264)", () => {
    const pad = intOrLongToInt({ low: 0, high: 0 } as never);
    expect(264 + pad + pad).toBe(264); // not "26400"
  });

  it("vector conversion handles mixed numbers and Long-likes", () => {
    expect(
      intOrLongToIntVector([1, { low: 2, high: 0 } as never, 3]),
    ).toEqual([1, 2, 3]);
  });
});
