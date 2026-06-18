import { describe, it, expect, vi } from "vitest";
import { StyleManager } from "../../example/style_transfer/styleManager.js";

const STYLES = [
  { id: "a", name: "A", dir: "styles/a/" },
  { id: "b", name: "B", dir: "styles/b/" },
];

describe("StyleManager", () => {
  it("loads a style runner via injected loadFn and caches it", async () => {
    const loadFn = vi.fn(async (dir) => ({ dir }));
    const m = new StyleManager(STYLES, loadFn);
    const r1 = await m.select("a");
    expect(r1).toEqual({ dir: "styles/a/" });
    expect(m.activeId).toBe("a");
    await m.select("a"); // 2回目はキャッシュ
    expect(loadFn).toHaveBeenCalledTimes(1);
  });

  it("loads different runner per style", async () => {
    const loadFn = vi.fn(async (dir) => ({ dir }));
    const m = new StyleManager(STYLES, loadFn);
    await m.select("a");
    const r2 = await m.select("b");
    expect(r2).toEqual({ dir: "styles/b/" });
    expect(loadFn).toHaveBeenCalledTimes(2);
  });

  it("throws on unknown id", async () => {
    const m = new StyleManager(STYLES, async () => ({}));
    await expect(m.select("zzz")).rejects.toThrow();
  });
});
