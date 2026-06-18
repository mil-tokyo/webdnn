import { stylize } from "./harness/infer.js";
import { Metrics } from "./harness/metrics.js";
import { ImageSource } from "./harness/imageSource.js";
import { StyleManager } from "./styleManager.js";

const LIVE_SIZE = 192;
const CAPTURE_SIZE = 256;
const CROP = 4; // light model(3x3端)なので小さめでよい

const out = document.getElementById("out");
const hud = document.getElementById("hud");
const msg = document.getElementById("msg");
const stylesBar = document.getElementById("styles");
const captureArea = document.getElementById("capture-area");

const metrics = new Metrics(30);
const source = new ImageSource({
  webcamEl: document.getElementById("webcam"),
  sampleEl: document.getElementById("sample"),
  imgEl: document.getElementById("dropimg"),
});

let manager = null;
let busy = false;
let showOriginal = false;

function loadRunner(dir) {
  const usp = new URLSearchParams(location.search);
  const backendOrder = (usp.get("backend") || "webgl").split(",");
  if (!backendOrder.includes("cpu")) backendOrder.push("cpu");
  return window.WebDNN.load(dir, { backendOrder });
}

function drawOriginal() {
  out.width = LIVE_SIZE;
  out.height = LIVE_SIZE;
  out.getContext("2d").drawImage(source.current(), 0, 0, LIVE_SIZE, LIVE_SIZE);
}

async function loop() {
  requestAnimationFrame(loop);
  const runner = manager && manager.active();
  if (!runner || busy || !source.ready()) return;
  busy = true;
  try {
    if (showOriginal) {
      drawOriginal();
      hud.textContent = "original";
      return;
    }
    const ms = await stylize(runner, source.current(), LIVE_SIZE, out, { cropBorder: CROP });
    metrics.inference(ms);
    metrics.frame(performance.now());
    hud.textContent = `${runner.backendName} | ${ms.toFixed(0)}ms | ${metrics.fps().toFixed(1)}fps`;
  } catch (e) {
    msg.textContent = "推論エラー: " + e;
  } finally {
    busy = false;
  }
}

async function capture() {
  const runner = manager && manager.active();
  if (!runner || !source.ready()) return;
  msg.textContent = "キャプチャ中…";
  const cap = document.createElement("canvas");
  try {
    const ms = await stylize(runner, source.current(), CAPTURE_SIZE, cap, { cropBorder: CROP });
    cap.id = "cap";
    const a = document.createElement("a");
    a.href = cap.toDataURL("image/png");
    a.download = "stylized.png";
    a.textContent = "⬇ 保存";
    a.className = "btn";
    a.style.cssText = "display:inline-block;margin-top:8px";
    captureArea.innerHTML = "";
    captureArea.appendChild(cap);
    captureArea.appendChild(document.createElement("br"));
    captureArea.appendChild(a);
    msg.textContent = `キャプチャ完了 (${CAPTURE_SIZE}², ${ms.toFixed(0)}ms)`;
  } catch (e) {
    msg.textContent = "キャプチャ失敗: " + e;
  }
}

function buildStyleBar(styles) {
  stylesBar.innerHTML = "";
  for (const s of styles) {
    const b = document.createElement("button");
    b.title = s.name;
    b.textContent = s.thumb ? "" : s.name;
    if (s.thumb) b.style.backgroundImage = `url(${s.thumb})`;
    b.onclick = async () => {
      msg.textContent = "ロード中: " + s.name;
      try {
        await manager.select(s.id);
        [...stylesBar.children].forEach((c) => c.classList.remove("active"));
        b.classList.add("active");
        msg.textContent = "";
      } catch (e) {
        msg.textContent = "ロード失敗: " + e;
      }
    };
    stylesBar.appendChild(b);
  }
}

document.getElementById("cam").onclick = () =>
  source.startWebcam().catch((e) => (msg.textContent = "カメラ不可: " + e));
document.getElementById("capture").onclick = capture;
document.getElementById("ba").onclick = () => {
  showOriginal = !showOriginal;
};
document.getElementById("file").onchange = (e) => {
  const f = e.target.files[0];
  if (!f) return;
  const img = new Image();
  img.onload = () => source.setImage(img);
  img.src = URL.createObjectURL(f);
};
out.addEventListener("dragover", (e) => e.preventDefault());
out.addEventListener("drop", (e) => {
  e.preventDefault();
  const f = e.dataTransfer.files[0];
  if (!f) return;
  const img = new Image();
  img.onload = () => source.setImage(img);
  img.src = URL.createObjectURL(f);
});

(async () => {
  let styles = [];
  try {
    styles = await (await fetch("styles/styles.json")).json();
  } catch (e) {
    /* no manifest yet */
  }
  // 既定の入力 = サンプル画像（webカメラボタンでライブに切替）
  const sampleImg = new Image();
  await new Promise((r) => {
    sampleImg.onload = r;
    sampleImg.onerror = r;
    sampleImg.src = "sample.jpg";
  });
  if (sampleImg.naturalWidth) source.setImage(sampleImg);
  if (!styles.length) {
    msg.textContent =
      "学習済みstyleがありません。train/README に従って学習し styles/styles.json を更新してください。";
    return;
  }
  manager = new StyleManager(styles, loadRunner);
  buildStyleBar(styles);
  try {
    await manager.select(styles[0].id);
    if (stylesBar.firstChild) stylesBar.firstChild.classList.add("active");
    hud.textContent = "backend: " + manager.active().backendName;
    loop();
  } catch (e) {
    msg.textContent = "モデルロード失敗: " + e;
  }
})();
