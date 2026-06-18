import { describe, it, expect } from "vitest";
import { argmax, argmin } from "../../src/descriptor_runner/math/argsort";
import {
  arange,
  arrayProd,
  arraySum,
  arrayEqual,
} from "../../src/descriptor_runner/util";

describe("argmax", () => {
  it("returns index of the single max by default", () => {
    expect(argmax([1, 3, 2])).toEqual([1]);
  });
  it("returns top-k indices", () => {
    const top2 = argmax([5, 1, 4, 2], 2);
    expect(top2).toEqual([0, 2]);
  });
});

describe("argmin", () => {
  it("returns index of the single min by default", () => {
    expect(argmin([1, 3, 2])).toEqual([0]);
  });
  it("accepts Int32Array", () => {
    expect(argmin(new Int32Array([4, 0, 9]))).toEqual([1]);
  });
});

describe("arange", () => {
  it("one-arg form counts from 0", () => {
    expect(arange(3)).toEqual([0, 1, 2]);
  });
  it("two-arg form", () => {
    expect(arange(2, 5)).toEqual([2, 3, 4]);
  });
  it("negative step counts down", () => {
    expect(arange(3, 0, -1)).toEqual([3, 2, 1]);
  });
});

describe("array helpers", () => {
  it("arrayProd multiplies all elements", () => {
    expect(arrayProd([2, 3, 4])).toBe(24);
  });
  it("arraySum adds all elements", () => {
    expect(arraySum([2, 3, 4])).toBe(9);
  });
  it("arrayEqual compares element-wise", () => {
    expect(arrayEqual([1, 2], [1, 2])).toBe(true);
    expect(arrayEqual([1, 2], [1, 3])).toBe(false);
  });
});
