/** style一覧と遅延ロード/キャッシュ/現行選択を管理（loadFn注入でテスト可能）。 */
export class StyleManager {
  constructor(styles, loadFn) {
    this.styles = styles;
    this.loadFn = loadFn; // (dir) => Promise<runner>
    this.cache = new Map();
    this.activeId = null;
  }
  async select(id) {
    const s = this.styles.find((x) => x.id === id);
    if (!s) throw new Error("unknown style id: " + id);
    if (!this.cache.has(id)) this.cache.set(id, await this.loadFn(s.dir));
    this.activeId = id;
    return this.cache.get(id);
  }
  active() { return this.activeId ? this.cache.get(this.activeId) : null; }
}
