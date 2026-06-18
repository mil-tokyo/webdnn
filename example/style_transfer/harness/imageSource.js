/** 入力ソースを統一し、現在の Drawable(video/img) を返す。DOM依存（手動検証）。 */
export class ImageSource {
  constructor({ webcamEl, sampleEl, imgEl }) {
    this.webcamEl = webcamEl;
    this.sampleEl = sampleEl;
    this.imgEl = imgEl;
    this.kind = "sample"; // 既定: 放置で動く看板
  }
  async startSample(src) {
    this.sampleEl.src = src;
    await this.sampleEl.play().catch(() => {});
    this.kind = "sample";
  }
  async startWebcam() {
    const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" }, audio: false });
    this.webcamEl.srcObject = stream;
    await this.webcamEl.play();
    this.kind = "webcam";
  }
  setImage(image) { this.imgEl = image; this.kind = "image"; }
  /** getImageArray が受け取れる Drawable を返す。 */
  current() {
    if (this.kind === "webcam") return this.webcamEl;
    if (this.kind === "image") return this.imgEl;
    return this.sampleEl;
  }
  /** 描画すべきフレームが用意できているか（video は readyState で判定）。 */
  ready() {
    const el = this.current();
    if (el instanceof HTMLVideoElement) return el.readyState >= 2;
    return !!(el && (el.complete ?? true));
  }
}
