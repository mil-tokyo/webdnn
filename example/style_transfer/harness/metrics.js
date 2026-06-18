/** FPS と直近推論msを保持する純ロジック（DOM非依存・テスト可能）。 */
export class Metrics {
  constructor(windowSize = 30) {
    this.windowSize = windowSize;
    this.stamps = [];
    this._lastMs = 0;
  }
  frame(now) {
    this.stamps.push(now);
    if (this.stamps.length > this.windowSize) this.stamps.shift();
  }
  inference(ms) { this._lastMs = ms; }
  lastMs() { return this._lastMs; }
  fps() {
    if (this.stamps.length < 2) return 0;
    const span = this.stamps[this.stamps.length - 1] - this.stamps[0];
    if (span <= 0) return 0;
    return ((this.stamps.length - 1) * 1000) / span;
  }
}
