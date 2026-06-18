# カメラフィルタ（neural style transfer）Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** ブラウザの webカメラ/画像を WebDNN でリアルタイム画風変換し canvas に表示するデモを `example/style_transfer/` に作る。

**Architecture:** PyTorch で TransformerNet（Conv+InstanceNorm+ConvTranspose、新規op不要）を学習→ opset10 で ONNX 出力。Web 側は UMD グローバル `WebDNN` を使い、前処理 `WebDNN.Image.getImageArray`／後処理 `WebDNN.Image.setImageArrayToCanvas` の薄いグルー（入力ソース管理＋描画ループ＋StyleManager＋HUD）。純ロジック（StyleManager/Metrics）は vitest、モデル正当性は torch↔onnxruntime 一致＋ブラウザ4バックエンド目視。

**Tech Stack:** PyTorch / torchvision(VGG16) / ONNX(opset10) / onnxruntime（検証）/ WebDNN UMD(`dist/webdnn.js`) / ES modules / vitest。

仕様: [01-camera-filter.md](01-camera-filter.md)。実現性タグ🟢（自作 ConvTranspose 版は新規op不要、Pad reflect 対応確認済）。

---

## File Structure

```
example/style_transfer/
  index.html               # UMDグローバル WebDNN を読み、index.js を module で起動
  index.js                 # 配線（UI events / 描画ループ / 各moduleの結線）
  harness/
    metrics.js             # 純: FPS/推論ms 計算（vitest対象）
    imageSource.js         # DOM: webcam/sample/image の Drawable を統一提供
    infer.js               # グルー: getImageArray→CPUTensor→run→setImageArrayToCanvas
  styleManager.js          # 純(loadFn注入): style一覧/遅延ロード/現行runner切替（vitest対象）
  styles/                  # <id>/model.onnx + weights, <id>/thumb.jpg, styles.json
  train/
    model.py               # TransformerNet 定義
    train_style.py         # 学習ループ（COCO + 画風1枚, VGG16 perceptual）
    export_to_onnx.py      # .pth → ONNX(opset10) + expected.bin、torch↔onnxruntime検証
    convert_zoo.py         # ONNX zoo fast-style 変換 + アップサンプルop検査
test/unit/
  styleTransferMetrics.test.ts   # metrics.js の純ロジック
  styleTransferManager.test.ts   # styleManager.js の純ロジック（fake loadFn）
docs/demos/sample_video/         # サンプル動画（自動再生用、任意の小さいmp4）
```

各 phase は単体で動く成果を残す。Phase 0 で「モデルが WebDNN で動く」最大リスクを先に潰す。

---

## Phase 0: 動作リスクの先潰し（未学習モデルで端から端まで）

### Task 0.1: Python環境とモデル定義

**Files:**
- Create: `example/style_transfer/train/model.py`

- [ ] **Step 1: 依存を uv 環境に用意**

Run:
```bash
uv pip install torch torchvision onnx onnxruntime pillow numpy
```
Expected: 成功（既に入っていれば "already satisfied"）。`webdnn` python パッケージ（`src/graph_transpiler`）は既存 resnet 例で使えている前提。

- [ ] **Step 2: TransformerNet を実装**

`example/style_transfer/train/model.py`:
```python
import torch
import torch.nn as nn


class ConvLayer(nn.Module):
    """ReflectionPad + Conv（WebDNN は Pad reflect 対応）。"""
    def __init__(self, in_ch, out_ch, kernel_size, stride):
        super().__init__()
        self.pad = nn.ReflectionPad2d(kernel_size // 2)
        self.conv = nn.Conv2d(in_ch, out_ch, kernel_size, stride)

    def forward(self, x):
        return self.conv(self.pad(x))


class ResidualBlock(nn.Module):
    def __init__(self, ch):
        super().__init__()
        self.conv1 = ConvLayer(ch, ch, 3, 1)
        self.in1 = nn.InstanceNorm2d(ch, affine=True)
        self.conv2 = ConvLayer(ch, ch, 3, 1)
        self.in2 = nn.InstanceNorm2d(ch, affine=True)
        self.relu = nn.ReLU()

    def forward(self, x):
        residual = x
        out = self.relu(self.in1(self.conv1(x)))
        out = self.in2(self.conv2(out))
        return out + residual


class UpsampleConvT(nn.Module):
    """ConvTranspose による 2x アップサンプル（Resize op を使わず WebDNN 🟢 を保証）。"""
    def __init__(self, in_ch, out_ch):
        super().__init__()
        self.convt = nn.ConvTranspose2d(
            in_ch, out_ch, kernel_size=3, stride=2, padding=1, output_padding=1
        )

    def forward(self, x):
        return self.convt(x)


class TransformerNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = ConvLayer(3, 32, 9, 1)
        self.in1 = nn.InstanceNorm2d(32, affine=True)
        self.conv2 = ConvLayer(32, 64, 3, 2)
        self.in2 = nn.InstanceNorm2d(64, affine=True)
        self.conv3 = ConvLayer(64, 128, 3, 2)
        self.in3 = nn.InstanceNorm2d(128, affine=True)
        self.res1 = ResidualBlock(128)
        self.res2 = ResidualBlock(128)
        self.res3 = ResidualBlock(128)
        self.res4 = ResidualBlock(128)
        self.res5 = ResidualBlock(128)
        self.up1 = UpsampleConvT(128, 64)
        self.in4 = nn.InstanceNorm2d(64, affine=True)
        self.up2 = UpsampleConvT(64, 32)
        self.in5 = nn.InstanceNorm2d(32, affine=True)
        self.conv_out = ConvLayer(32, 3, 9, 1)
        self.relu = nn.ReLU()

    def forward(self, x):
        y = self.relu(self.in1(self.conv1(x)))
        y = self.relu(self.in2(self.conv2(y)))
        y = self.relu(self.in3(self.conv3(y)))
        y = self.res1(y)
        y = self.res2(y)
        y = self.res3(y)
        y = self.res4(y)
        y = self.res5(y)
        y = self.relu(self.in4(self.up1(y)))
        y = self.relu(self.in5(self.up2(y)))
        return self.conv_out(y)  # 活性化なし。後処理で[0,255]へclamp
```

- [ ] **Step 3: 形状の自己確認**

Run:
```bash
cd example/style_transfer/train && uv run python -c "import torch;from model import TransformerNet;print(TransformerNet()(torch.zeros(1,3,256,256)).shape)"
```
Expected: `torch.Size([1, 3, 256, 256])`（入出力同形＝アップサンプルが正しく2x×2）。

- [ ] **Step 4: Commit**

```bash
git add example/style_transfer/train/model.py
git commit -m "feat(demo): add TransformerNet (ConvTranspose upsample, op-safe)"
```

### Task 0.2: 未学習モデルを ONNX 化し torch↔onnxruntime 一致を確認

**Files:**
- Create: `example/style_transfer/train/export_to_onnx.py`

- [ ] **Step 1: エクスポート＋検証スクリプト**

`example/style_transfer/train/export_to_onnx.py`:
```python
import argparse
import os
import numpy as np
import torch
from model import TransformerNet
from webdnn.tensor_export import serialize_tensors


def export(weights, out_dir, size=256):
    os.makedirs(out_dir, exist_ok=True)
    model = TransformerNet().eval()
    if weights and os.path.exists(weights):
        model.load_state_dict(torch.load(weights, map_location="cpu"))
    dummy = torch.rand(1, 3, size, size) * 255.0  # 入力は[0,255]スケール
    with torch.no_grad():
        ref = model(dummy).numpy()
    onnx_path = os.path.join(out_dir, "model.onnx")
    with torch.no_grad():
        torch.onnx.export(
            model, dummy, onnx_path, input_names=["input"],
            output_names=["output"], opset_version=10,
        )
    # ブラウザ4バックエンド突合用の期待値（resnet例と同じ仕組み）
    serialize_tensors(os.path.join(out_dir, "expected.bin"),
                      {"input": dummy.numpy(), "output": ref})
    # 自動検証: onnxruntime と torch の一致
    import onnxruntime as ort
    sess = ort.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])
    ort_out = sess.run(None, {"input": dummy.numpy()})[0]
    diff = float(np.abs(ort_out - ref).max())
    print(f"max|torch-onnxruntime| = {diff:.4e}")
    assert diff < 1e-3, f"ONNX export mismatch: {diff}"
    print(f"OK: {onnx_path}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--weights", default="")
    p.add_argument("--out", required=True)
    p.add_argument("--size", type=int, default=256)
    export(p.parse_args().weights, p.parse_args().out, p.parse_args().size)
```

- [ ] **Step 2: 未学習モデルでエクスポート＆検証（失敗しないこと＝export経路が健全）**

Run:
```bash
cd example/style_transfer/train && uv run python export_to_onnx.py --out ../styles/_smoke
```
Expected: `max|torch-onnxruntime| = ...`（<1e-3）→ `OK: .../model.onnx`。`assert` で落ちないこと。

- [ ] **Step 3: Commit**

```bash
git add example/style_transfer/train/export_to_onnx.py
git commit -m "feat(demo): ONNX export + torch/onnxruntime parity check"
```

### Task 0.3: WebDNN で未学習モデルが端から端まで動くことを確認（最大リスクの解消）

**Files:**
- Create: `example/style_transfer/_smoke.html`（後で削除する使い捨て検証ページ）

- [ ] **Step 1: 最小検証ページ**

`example/style_transfer/_smoke.html`:
```html
<!DOCTYPE html>
<html><head><meta charset="utf-8"><script src="../../dist/webdnn.js"></script></head>
<body><pre id="log">loading...</pre>
<script>
(async () => {
  const log = (m) => (document.getElementById("log").textContent += "\n" + m);
  try {
    const usp = new URLSearchParams(location.search);
    const backendOrder = (usp.get("backend") || "webgl").split(",");
    if (!backendOrder.includes("cpu")) backendOrder.push("cpu");
    const runner = await WebDNN.load("styles/_smoke/", { backendOrder });
    log("backend = " + runner.backendName);
    const N = 1 * 3 * 256 * 256;
    const input = new WebDNN.CPUTensor([1, 3, 256, 256], "float32",
      Float32Array.from({ length: N }, () => Math.random() * 255));
    const t0 = Date.now();
    const [out] = await runner.run([input]);
    const data = out.data || out.toActual().data; // 返り値CPUテンソルの実データ
    log("ran in " + (Date.now() - t0) + " ms, outLen = " + data.length + " (expect 196608)");
    log("sample out[0..3] = " + Array.from(data.slice(0, 3)).map(x => x.toFixed(2)));
    log("SUCCESS");
  } catch (e) { log("FAIL: " + e); console.error(e); }
})();
</script></body></html>
```

- [ ] **Step 2: dist をビルド（無ければ）**

Run:
```bash
cd /Users/milhidaka/dev/webdnn && npm run build:all
```
Expected: `dist/webdnn.js` が生成される（既存なら再生成）。

- [ ] **Step 3: サーバ起動しブラウザで確認（WebGL→CPU）**

Run:
```bash
npm run server
```
ブラウザで `http://localhost:8000/example/style_transfer/_smoke.html` を開く。
Expected: `backend = webgl` / `outLen = 196608` / `SUCCESS`。
`?backend=cpu` でも `SUCCESS`。**ここで Conv/ConvTranspose/InstanceNorm/Pad(reflect)/Add/出力 が WebDNN で通ることが確定する。**

- [ ] **Step 4: 失敗時の分岐を記録**

もし特定opで失敗したら、エラーop名を `docs/demos/01-camera-filter.md` の §10 に追記し、原因（未対応op等）を切り分けてから次へ進む。InstanceNorm/ConvTranspose/Pad は実装確認済なので、通常は成功する想定。

- [ ] **Step 5: Commit**

```bash
git add example/style_transfer/_smoke.html
git commit -m "test(demo): end-to-end WebDNN smoke page for untrained net"
```

---

## Phase 1: 学習と1スタイルの生成

### Task 1.1: 学習スクリプト

**Files:**
- Create: `example/style_transfer/train/train_style.py`

- [ ] **Step 1: 学習ループ（COCO + 画風1枚, VGG16 perceptual）**

`example/style_transfer/train/train_style.py`:
```python
import argparse
import os
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
from PIL import Image
from model import TransformerNet

MEAN = torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1)
STD = torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1)


def normalize_batch(x):  # x は [0,255] → VGG 入力へ
    return (x / 255.0 - MEAN.to(x.device)) / STD.to(x.device)


class Vgg16(torch.nn.Module):
    def __init__(self):
        super().__init__()
        vgg = models.vgg16(weights=models.VGG16_Weights.DEFAULT).features.eval()
        for p in vgg.parameters():
            p.requires_grad_(False)
        self.slices = torch.nn.ModuleList(
            [vgg[0:4], vgg[4:9], vgg[9:16], vgg[16:23]]  # relu1_2,2_2,3_3,4_3
        )

    def forward(self, x):
        feats, h = [], x
        for s in self.slices:
            h = s(h)
            feats.append(h)
        return feats  # [relu1_2, relu2_2, relu3_3, relu4_3]


def gram(x):
    b, c, h, w = x.shape
    f = x.view(b, c, h * w)
    return f.bmm(f.transpose(1, 2)) / (c * h * w)


def load_style(path, size, device):
    img = Image.open(path).convert("RGB").resize((size, size))
    t = transforms.ToTensor()(img).mul(255).unsqueeze(0).to(device)
    return t


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", required=True, help="COCO train2014 親ディレクトリ（ImageFolder形式）")
    p.add_argument("--style-image", required=True)
    p.add_argument("--out", required=True, help=".pth 出力先")
    p.add_argument("--size", type=int, default=256)
    p.add_argument("--epochs", type=int, default=2)
    p.add_argument("--batch", type=int, default=4)
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--content-weight", type=float, default=1e5)
    p.add_argument("--style-weight", type=float, default=1e10)
    args = p.parse_args()
    device = "cuda" if torch.cuda.is_available() else "cpu"

    tfm = transforms.Compose([
        transforms.Resize(args.size), transforms.CenterCrop(args.size),
        transforms.ToTensor(), transforms.Lambda(lambda x: x.mul(255)),
    ])
    loader = DataLoader(datasets.ImageFolder(args.dataset, tfm),
                        batch_size=args.batch, shuffle=True, num_workers=4, drop_last=True)

    net = TransformerNet().to(device).train()
    opt = torch.optim.Adam(net.parameters(), args.lr)
    vgg = Vgg16().to(device)
    style = load_style(args.style_image, args.size, device)
    style_grams = [gram(f) for f in vgg(normalize_batch(style))]

    step = 0
    for epoch in range(args.epochs):
        for x, _ in loader:
            x = x.to(device)
            opt.zero_grad()
            y = net(x)
            fx, fy = vgg(normalize_batch(x)), vgg(normalize_batch(y.clamp(0, 255)))
            content = args.content_weight * F.mse_loss(fy[1], fx[1])  # relu2_2
            style_loss = 0.0
            for fyl, sg in zip(fy, style_grams):
                style_loss = style_loss + F.mse_loss(gram(fyl), sg.expand(fyl.size(0), -1, -1))
            style_loss = args.style_weight * style_loss
            (content + style_loss).backward()
            opt.step()
            if step % 200 == 0:
                print(f"e{epoch} s{step} content={content.item():.1f} style={style_loss.item():.1f}")
            step += 1
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    torch.save(net.cpu().eval().state_dict(), args.out)
    print("saved", args.out)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Commit**

```bash
git add example/style_transfer/train/train_style.py
git commit -m "feat(demo): fast-style training script (VGG16 perceptual loss)"
```

### Task 1.2: COCO 取得と1スタイル学習・エクスポート

**Files:**
- Create: `example/style_transfer/styles/<style_id>/`（学習成果）, `example/style_transfer/styles/styles.json`

- [ ] **Step 1: COCO train2014 を取得（ImageFolder 形式に）**

Run:
```bash
mkdir -p ~/data/coco/train && cd ~/data/coco \
 && curl -O http://images.cocodataset.org/zips/train2014.zip \
 && unzip -q train2014.zip -d train
```
Expected: `~/data/coco/train/train2014/*.jpg`（ImageFolder はサブディレクトリ必須なので `train/` を親に指定）。
注: 全量13GB。短縮するなら一部画像のみでも可（品質は落ちる）。

- [ ] **Step 2: 1スタイル学習（画風画像は任意の1枚、例 ukiyoe.jpg）**

Run:
```bash
cd example/style_transfer/train && uv run python train_style.py \
  --dataset ~/data/coco/train --style-image styles_src/ukiyoe.jpg \
  --out ../styles/ukiyoe/transformer.pth --epochs 2
```
Expected: content/style ロスが減少しつつ `saved ../styles/ukiyoe/transformer.pth`（RTX4070 で ~1–2h）。

- [ ] **Step 3: ONNX 化＋検証**

Run:
```bash
cd example/style_transfer/train && uv run python export_to_onnx.py \
  --weights ../styles/ukiyoe/transformer.pth --out ../styles/ukiyoe
```
Expected: `OK: ../styles/ukiyoe/model.onnx`（torch↔onnxruntime <1e-3）。

- [ ] **Step 4: styles.json を作成（1件）**

`example/style_transfer/styles/styles.json`:
```json
[
  { "id": "ukiyoe", "name": "浮世絵", "dir": "styles/ukiyoe/", "thumb": "styles/ukiyoe/thumb.jpg" }
]
```
`styles/ukiyoe/thumb.jpg` は画風画像の縮小（任意の手段で 128x128 程度）。

- [ ] **Step 5: ブラウザで _smoke を学習済みに向けて確認**

`_smoke.html` の `WebDNN.load("styles/_smoke/")` を一時的に `"styles/ukiyoe/"` にして `http://localhost:8000/example/style_transfer/_smoke.html` を開く。
Expected: `SUCCESS`（学習済みでも通る）。確認後 `_smoke.html` の変更は戻す。

- [ ] **Step 6: Commit**

```bash
git add example/style_transfer/styles/ukiyoe/model.onnx example/style_transfer/styles/ukiyoe/*.bin \
        example/style_transfer/styles/ukiyoe/thumb.jpg example/style_transfer/styles/styles.json
git commit -m "feat(demo): first trained style (ukiyoe) + styles manifest"
```

---

## Phase 2: 推論グルーで静止画1枚を変換（最小デモ）

### Task 2.1: infer.js（getImageArray→run→setImageArrayToCanvas）

**Files:**
- Create: `example/style_transfer/harness/infer.js`

- [ ] **Step 1: 実装**

`example/style_transfer/harness/infer.js`:
```js
// WebDNN は UMD グローバル（dist/webdnn.js）として window.WebDNN に存在する前提。
const W = () => window.WebDNN;

/** Drawable(video/img/canvas) を size×size で画風変換し canvas へ描画。推論msを返す。 */
export async function stylize(runner, drawable, size, canvas, { cropBorder = 0 } = {}) {
  const wd = W();
  const arr = await wd.Image.getImageArray(drawable, {
    dstW: size, dstH: size,
    color: wd.Image.Color.RGB, order: wd.Image.Order.CHW,
    bias: [0, 0, 0], scale: [1, 1, 1], // 入力は[0,255]そのまま（fast-styleは正規化しない）
  });
  const input = new wd.CPUTensor([1, 3, size, size], "float32", arr);
  const t0 = Date.now();
  const [out] = await runner.run([input]);
  const ms = Date.now() - t0;
  const data = out.data || out.toActual().data;
  canvas.width = size; canvas.height = size;
  wd.Image.setImageArrayToCanvas(data, size, size, canvas, {
    order: wd.Image.Order.CHW,
    srcX: cropBorder, srcY: cropBorder,
    srcW: size - cropBorder * 2, srcH: size - cropBorder * 2,
    dstW: size, dstH: size, // クロップ後に元サイズへ拡大（境界ノイズ除去）
  });
  return ms;
}
```

- [ ] **Step 2: Commit**

```bash
git add example/style_transfer/harness/infer.js
git commit -m "feat(demo): infer glue (getImageArray -> run -> setImageArrayToCanvas)"
```

### Task 2.2: 最小 index.html / index.js（画像1枚＋1スタイル）

**Files:**
- Create: `example/style_transfer/index.html`, `example/style_transfer/index.js`

- [ ] **Step 1: index.html（UMD→module 起動、最小UI）**

`example/style_transfer/index.html`:
```html
<!DOCTYPE html>
<html lang="ja"><head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>WebDNN リアルタイム画風変換</title>
  <script src="../../dist/webdnn.js"></script>
  <style>
    body { font-family: sans-serif; text-align: center; background: #111; color: #eee; margin: 0; }
    #stage { display: inline-block; position: relative; margin-top: 12px; }
    #out { max-width: 90vw; image-rendering: auto; background: #000; }
    #hud { position: absolute; top: 6px; left: 6px; font-size: 12px; background: #0008; padding: 2px 6px; border-radius: 4px; }
    #styles button { width: 84px; height: 84px; margin: 4px; border: 3px solid transparent; cursor: pointer; background-size: cover; }
    #styles button.active { border-color: #4cf; }
    .controls { margin: 10px; }
  </style>
</head><body>
  <h1>WebDNN 画風変換</h1>
  <div class="controls">
    <button id="cam">webカメラを許可</button>
    <button id="ba">before/after</button>
    <input id="file" type="file" accept="image/*" />
    <span>ファイルはドラッグ&ドロップも可</span>
  </div>
  <div id="stage"><canvas id="out" width="256" height="256"></canvas><span id="hud">…</span></div>
  <div id="styles"></div>
  <video id="sample" loop muted playsinline style="display:none"></video>
  <video id="webcam" muted playsinline style="display:none"></video>
  <img id="dropimg" style="display:none" />
  <script type="module" src="index.js"></script>
</body></html>
```

- [ ] **Step 2: index.js（まず画像1枚を1スタイルで変換できる所まで）**

`example/style_transfer/index.js`:
```js
import { stylize } from "./harness/infer.js";

const SIZE = 256;
const out = document.getElementById("out");
const hud = document.getElementById("hud");

async function loadRunner(dir) {
  const usp = new URLSearchParams(location.search);
  const backendOrder = (usp.get("backend") || "webgl").split(",");
  if (!backendOrder.includes("cpu")) backendOrder.push("cpu");
  return window.WebDNN.load(dir, { backendOrder });
}

(async () => {
  const styles = await (await fetch("styles/styles.json")).json();
  const runner = await loadRunner(styles[0].dir);
  hud.textContent = "backend: " + runner.backendName;
  // 既定のサンプル画像（COCOの1枚をstyles配下に置くか、resnet例の画像を流用）
  const img = new Image();
  img.onload = async () => {
    const ms = await stylize(runner, img, SIZE, out, { cropBorder: 8 });
    hud.textContent = `backend:${runner.backendName} ${ms}ms`;
  };
  img.src = "sample.jpg"; // example/style_transfer/sample.jpg を用意
})();
```

- [ ] **Step 3: サンプル画像を置く**

Run:
```bash
cp example/resnet/output/000000039769.jpg example/style_transfer/sample.jpg 2>/dev/null \
 || curl -o example/style_transfer/sample.jpg http://images.cocodataset.org/val2017/000000039769.jpg
```

- [ ] **Step 4: ブラウザで確認**

`npm run server` → `http://localhost:8000/example/style_transfer/`。
Expected: sample.jpg が画風変換されて 256x256 で表示、HUD に backend と推論ms。

- [ ] **Step 5: Commit**

```bash
git add example/style_transfer/index.html example/style_transfer/index.js example/style_transfer/sample.jpg
git commit -m "feat(demo): minimal static-image stylization page"
```

---

## Phase 3: 入力ソース（webcam/sample/image）＋描画ループ

### Task 3.1: metrics.js（純ロジック・TDD）

**Files:**
- Create: `example/style_transfer/harness/metrics.js`
- Test: `test/unit/styleTransferMetrics.test.ts`

- [ ] **Step 1: 失敗するテストを書く**

`test/unit/styleTransferMetrics.test.ts`:
```ts
import { describe, it, expect } from "vitest";
import { Metrics } from "../../example/style_transfer/harness/metrics.js";

describe("Metrics", () => {
  it("computes fps from frame timestamps over a window", () => {
    const m = new Metrics(4);
    [0, 100, 200, 300, 400].forEach((t) => m.frame(t)); // 100ms間隔 = 10fps
    expect(Math.round(m.fps())).toBe(10);
  });
  it("tracks last inference ms", () => {
    const m = new Metrics(4);
    m.inference(33);
    expect(m.lastMs()).toBe(33);
  });
  it("returns 0 fps before enough frames", () => {
    expect(new Metrics(4).fps()).toBe(0);
  });
});
```

- [ ] **Step 2: テスト失敗を確認**

Run: `npx vitest run test/unit/styleTransferMetrics.test.ts`
Expected: FAIL（`metrics.js` 未作成で import エラー）。

- [ ] **Step 3: 実装**

`example/style_transfer/harness/metrics.js`:
```js
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
```

- [ ] **Step 4: テスト成功を確認**

Run: `npx vitest run test/unit/styleTransferMetrics.test.ts`
Expected: PASS（3 tests）。

- [ ] **Step 5: Commit**

```bash
git add example/style_transfer/harness/metrics.js test/unit/styleTransferMetrics.test.ts
git commit -m "feat(demo): Metrics (fps/inference-ms) with unit tests"
```

### Task 3.2: imageSource.js（webcam/sample/image の統一）

**Files:**
- Create: `example/style_transfer/harness/imageSource.js`

- [ ] **Step 1: 実装**

`example/style_transfer/harness/imageSource.js`:
```js
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
```

- [ ] **Step 2: Commit**

```bash
git add example/style_transfer/harness/imageSource.js
git commit -m "feat(demo): ImageSource (webcam/sample/image unified)"
```

### Task 3.3: index.js を描画ループ化（ライブ変換）

**Files:**
- Modify: `example/style_transfer/index.js`（全面置換）
- 要: `docs/demos/sample_video/sample.mp4`（小さい人物/風景mp4。手元の任意素材か、後で差し替え可）

- [ ] **Step 1: index.js を描画ループ版に置換**

`example/style_transfer/index.js`:
```js
import { stylize } from "./harness/infer.js";
import { Metrics } from "./harness/metrics.js";
import { ImageSource } from "./harness/imageSource.js";

const SIZE = 256;
const out = document.getElementById("out");
const hud = document.getElementById("hud");
const metrics = new Metrics(30);
const source = new ImageSource({
  webcamEl: document.getElementById("webcam"),
  sampleEl: document.getElementById("sample"),
  imgEl: document.getElementById("dropimg"),
});

let runner = null;
let busy = false;

async function loadRunner(dir) {
  const usp = new URLSearchParams(location.search);
  const backendOrder = (usp.get("backend") || "webgl").split(",");
  if (!backendOrder.includes("cpu")) backendOrder.push("cpu");
  return window.WebDNN.load(dir, { backendOrder });
}

async function loop() {
  requestAnimationFrame(loop);
  if (!runner || busy || !source.ready()) return;
  busy = true;
  try {
    const ms = await stylize(runner, source.current(), SIZE, out, { cropBorder: 8 });
    metrics.inference(ms);
    metrics.frame(Date.now());
    hud.textContent = `${runner.backendName} | ${ms}ms | ${metrics.fps().toFixed(1)}fps`;
  } finally { busy = false; }
}

document.getElementById("cam").onclick = () => source.startWebcam().catch((e) => alert("カメラ不可: " + e));
document.getElementById("file").onchange = (e) => {
  const f = e.target.files[0]; if (!f) return;
  const img = new Image();
  img.onload = () => source.setImage(img);
  img.src = URL.createObjectURL(f);
};

(async () => {
  const styles = await (await fetch("styles/styles.json")).json();
  await source.startSample("../../docs/demos/sample_video/sample.mp4");
  runner = await loadRunner(styles[0].dir);
  hud.textContent = "backend: " + runner.backendName;
  loop();
})();
```

- [ ] **Step 2: サンプル動画を用意**

`docs/demos/sample_video/sample.mp4` に小さい mp4 を置く（任意素材。無ければ一時的に画像ループでも可だが、looping video が望ましい）。

- [ ] **Step 3: ブラウザで確認**

`npm run server` → デモを開く。
Expected: サンプル動画がリアルタイム画風変換され、HUD に backend/ms/fps。`webカメラを許可`でカメラ映像に切替、ファイル選択で静止画に切替。

- [ ] **Step 4: Commit**

```bash
git add example/style_transfer/index.js docs/demos/sample_video/sample.mp4
git commit -m "feat(demo): live render loop with webcam/sample/image switching"
```

---

## Phase 4: StyleManager ＋ 画風切替UI ＋ before/after

### Task 4.1: styleManager.js（純ロジック・TDD）

**Files:**
- Create: `example/style_transfer/styleManager.js`
- Test: `test/unit/styleTransferManager.test.ts`

- [ ] **Step 1: 失敗するテストを書く**

`test/unit/styleTransferManager.test.ts`:
```ts
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
```

- [ ] **Step 2: テスト失敗を確認**

Run: `npx vitest run test/unit/styleTransferManager.test.ts`
Expected: FAIL（`styleManager.js` 未作成）。

- [ ] **Step 3: 実装**

`example/style_transfer/styleManager.js`:
```js
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
```

- [ ] **Step 4: テスト成功を確認**

Run: `npx vitest run test/unit/styleTransferManager.test.ts`
Expected: PASS（3 tests）。

- [ ] **Step 5: 全テスト（既存20＋新規）が緑**

Run: `npm test`
Expected: 全 PASS（既存20 + metrics3 + manager3 = 26）。

- [ ] **Step 6: Commit**

```bash
git add example/style_transfer/styleManager.js test/unit/styleTransferManager.test.ts
git commit -m "feat(demo): StyleManager with lazy-load cache + unit tests"
```

### Task 4.2: 画風サムネイル帯 ＋ before/after を index.js に結線

**Files:**
- Modify: `example/style_transfer/index.js`

- [ ] **Step 1: StyleManager と UI を結線（差分を反映した全文）**

`example/style_transfer/index.js`:
```js
import { stylize } from "./harness/infer.js";
import { Metrics } from "./harness/metrics.js";
import { ImageSource } from "./harness/imageSource.js";
import { StyleManager } from "./styleManager.js";

const SIZE = 256;
const out = document.getElementById("out");
const hud = document.getElementById("hud");
const stylesBar = document.getElementById("styles");
const metrics = new Metrics(30);
const source = new ImageSource({
  webcamEl: document.getElementById("webcam"),
  sampleEl: document.getElementById("sample"),
  imgEl: document.getElementById("dropimg"),
});

let manager = null;
let busy = false;
let showOriginal = false; // before/after トグル

function loadRunner(dir) {
  const usp = new URLSearchParams(location.search);
  const backendOrder = (usp.get("backend") || "webgl").split(",");
  if (!backendOrder.includes("cpu")) backendOrder.push("cpu");
  return window.WebDNN.load(dir, { backendOrder });
}

function drawOriginal() {
  const el = source.current();
  const ctx = out.getContext("2d");
  out.width = SIZE; out.height = SIZE;
  ctx.drawImage(el, 0, 0, SIZE, SIZE);
}

async function loop() {
  requestAnimationFrame(loop);
  const runner = manager && manager.active();
  if (!runner || busy || !source.ready()) return;
  busy = true;
  try {
    if (showOriginal) { drawOriginal(); hud.textContent = "original"; return; }
    const ms = await stylize(runner, source.current(), SIZE, out, { cropBorder: 8 });
    metrics.inference(ms); metrics.frame(Date.now());
    hud.textContent = `${runner.backendName} | ${ms}ms | ${metrics.fps().toFixed(1)}fps`;
  } finally { busy = false; }
}

function buildStyleBar(styles) {
  stylesBar.innerHTML = "";
  for (const s of styles) {
    const b = document.createElement("button");
    b.title = s.name;
    b.style.backgroundImage = `url(${s.thumb})`;
    b.onclick = async () => {
      await manager.select(s.id);
      [...stylesBar.children].forEach((c) => c.classList.remove("active"));
      b.classList.add("active");
    };
    stylesBar.appendChild(b);
  }
  if (stylesBar.firstChild) stylesBar.firstChild.classList.add("active");
}

document.getElementById("cam").onclick = () => source.startWebcam().catch((e) => alert("カメラ不可: " + e));
document.getElementById("ba").onclick = () => { showOriginal = !showOriginal; };
document.getElementById("file").onchange = (e) => {
  const f = e.target.files[0]; if (!f) return;
  const img = new Image(); img.onload = () => source.setImage(img); img.src = URL.createObjectURL(f);
};
out.addEventListener("dragover", (e) => e.preventDefault());
out.addEventListener("drop", (e) => {
  e.preventDefault(); const f = e.dataTransfer.files[0]; if (!f) return;
  const img = new Image(); img.onload = () => source.setImage(img); img.src = URL.createObjectURL(f);
});

(async () => {
  const styles = await (await fetch("styles/styles.json")).json();
  manager = new StyleManager(styles, loadRunner);
  buildStyleBar(styles);
  await source.startSample("../../docs/demos/sample_video/sample.mp4");
  await manager.select(styles[0].id);
  hud.textContent = "backend: " + manager.active().backendName;
  loop();
})();
```

- [ ] **Step 2: ブラウザで確認**

Expected: サムネイルをタップで画風が即切替、`before/after` で原画と比較、カメラ/ファイル/ドロップが動作、HUD 更新。

- [ ] **Step 3: Commit**

```bash
git add example/style_transfer/index.js
git commit -m "feat(demo): style thumbnail switcher + before/after toggle"
```

---

## Phase 5: スタイル追加 ＋ 学習済みzoo変換（ボーナス）

### Task 5.1: 追加スタイルを学習（合計5–6種）

**Files:**
- Modify: `example/style_transfer/styles/styles.json`
- Create: `example/style_transfer/styles/<id>/`（×4–5）

- [ ] **Step 1: 各画風を学習→エクスポート（Task 1.2 と同手順を画風ごとに）**

例（ゴッホ/ムンク/モザイク/点描）:
```bash
cd example/style_transfer/train
for s in gogh munch mosaic pointillism; do
  uv run python train_style.py --dataset ~/data/coco/train \
    --style-image styles_src/$s.jpg --out ../styles/$s/transformer.pth --epochs 2
  uv run python export_to_onnx.py --weights ../styles/$s/transformer.pth --out ../styles/$s
done
```
Expected: 各 `../styles/<s>/model.onnx` が `OK`。各 thumb.jpg を用意。

- [ ] **Step 2: styles.json に5–6件を列挙**

`example/style_transfer/styles/styles.json` に全エントリを追記（id/name/dir/thumb）。

- [ ] **Step 3: ブラウザで全画風切替を確認 → Commit**

```bash
git add example/style_transfer/styles
git commit -m "feat(demo): add 4-5 more trained styles"
```

### Task 5.2: 学習済みzoo変換とアップサンプルop検査（乗ればボーナス）

**Files:**
- Create: `example/style_transfer/train/convert_zoo.py`

- [ ] **Step 1: 変換＋op検査スクリプト**

`example/style_transfer/train/convert_zoo.py`:
```python
import argparse, os, onnx

UPSAMPLE_OPS = {"Resize", "Upsample"}

def inspect(onnx_path):
    m = onnx.load(onnx_path)
    ops = [n.op_type for n in m.graph.node]
    used_upsample = sorted(set(ops) & UPSAMPLE_OPS)
    print(f"{onnx_path}: nodes={len(ops)} upsample_ops={used_upsample or 'none(ConvTranspose可能性)'}")
    return used_upsample

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--onnx", required=True, help="zoo の fast-style ONNX")
    p.add_argument("--out", required=True)
    a = p.parse_args()
    used = inspect(a.onnx)
    os.makedirs(a.out, exist_ok=True)
    # WebDNN は model.onnx を読む。コピー配置のみ（変換不要なら）。
    onnx.save(onnx.load(a.onnx), os.path.join(a.out, "model.onnx"))
    if used:
        print("NOTE: Resize/Upsample を含む → WebDNN に Resize op 追加が必要（🟡）。"
              "未実装なら本zooは見送り、自作styleのみで🟢を維持。")
```

- [ ] **Step 2: zoo モデル取得＆検査**

Run:
```bash
cd example/style_transfer/train
curl -L -o /tmp/mosaic.onnx https://github.com/onnx/models/raw/main/validated/vision/style_transfer/fast_neural_style/model/mosaic-9.onnx
uv run python convert_zoo.py --onnx /tmp/mosaic.onnx --out ../styles/zoo_mosaic
```
Expected: `upsample_ops=...` が表示される。
- `none` の場合 → `_smoke.html` を `styles/zoo_mosaic/` に向けてブラウザで `SUCCESS` を確認 → styles.json に追加。
- `Resize/Upsample` を含む場合 → **本タスクはここで停止**。判断: (a) Resize op を WebDNN に追加する別計画を起票（カタログ §無いop 参照、深度/背景除去にも波及し高ROI）か、(b) zoo は見送り自作styleのみ。`docs/demos/01-camera-filter.md` §10-2 に結果を追記。

- [ ] **Step 3: Commit（結果に応じて）**

```bash
git add example/style_transfer/train/convert_zoo.py
git commit -m "feat(demo): zoo fast-style converter + upsample-op inspector"
```

---

## Phase 6: 仕上げ（性能フォールバック / 4バックエンド検証 / README）

### Task 6.1: 解像度フォールバック（重い端末で192²）

**Files:**
- Modify: `example/style_transfer/index.js`

- [ ] **Step 1: 推論msが閾値超で SIZE を 256→192 に落とす**

`index.js` の先頭 `const SIZE = 256;` を可変にし、`loop()` 内の計測後に追加:
```js
// 先頭: let SIZE = 256;  （const から let へ）
// loop() の stylize 後（metrics.inference(ms) の直後）に:
if (ms > 120 && SIZE === 256) { SIZE = 192; }       // 重い端末は解像度を落とす
```
（CPU フォールバックや低速GPUでも“動く”体感を保つ。閾値は実測で調整。）

- [ ] **Step 2: ブラウザで `?backend=cpu` でも破綻せず動くこと（低fpsでも可）を確認 → Commit**

```bash
git add example/style_transfer/index.js
git commit -m "feat(demo): auto downscale to 192 on slow devices"
```

### Task 6.2: 4バックエンド突合（CPU基準）

- [ ] **Step 1: 1スタイルを4バックエンドで実行し出力を目視突合**

`_smoke.html` を対象 style に向け、`?backend=webgl` / `wasm` / `cpu` を開く（WebGPUは現状Conv等限定なので動けば確認、不可なら記録）。
Expected: WebGL/WASM/CPU で SUCCESS、出力テンソルが概ね一致（`expected.bin` と突合する場合は許容差内）。差異・失敗は `docs/demos/01-camera-filter.md` に記録。

- [ ] **Step 2: 使い捨て検証ページを削除 → Commit**

```bash
git rm example/style_transfer/_smoke.html
git commit -m "chore(demo): remove smoke page after backend verification"
```

### Task 6.3: README と仕様の整合

**Files:**
- Create: `example/style_transfer/README.md`
- Modify: `docs/demos/README.md`（ステータス更新）

- [ ] **Step 1: デモ README（起動手順・学習手順・既知の制約）**

`example/style_transfer/README.md` に: 概要 / 起動（`npm run build:all` → `npm run server` → URL）/ 学習（COCO取得→train_style→export）/ backend切替（`?backend=`）/ 既知の制約（zooがResize要なら未対応 等）を記載。

- [ ] **Step 2: カタログのステータス更新**

`docs/demos/README.md` の `## ステータス` の「01 カメラフィルタ」を実装済みに更新（動作確認済の旨）。

- [ ] **Step 3: 全テスト緑を確認**

Run: `npm test`
Expected: 全 PASS。

- [ ] **Step 4: Commit**

```bash
git add example/style_transfer/README.md docs/demos/README.md
git commit -m "docs(demo): style transfer README + catalog status update"
```

---

## 受け入れ基準（spec §11 と対応）

- [ ] 自作 ConvTranspose style 1個以上が ONNX 化（Task 1.2）＆ WebGL でリアルタイム動作（Task 3.3/4.2）。
- [ ] webカメラ／サンプル自動再生／画像D&D の3入力（Task 3.3/4.2）。
- [ ] 画風サムネイル帯切替・before/after・HUD（Task 4.2）。
- [ ] 4バックエンドで実行可能・CPU基準と突合（Task 6.2）。
- [ ] 共通ハーネス（infer/imageSource/metrics）が分離され demos 03・04 へ転用可能な粒度（Phase 2–4）。
- [ ] 学習スクリプト（train+export）が RTX 4070 で完走・README 記載（Task 1.x/6.3）。

## メモ: 実装中に判断が要る分岐

- **zooモデルが Resize 依存**（Task 5.2）→ 自作styleで🟢を維持しつつ、Resize op 追加は別計画（カタログ参照）。
- **チェッカーボード**が目立つ → `stylize` の `cropBorder` を増やす／学習を伸ばす。
- **CPUバックエンドが遅すぎ** → 既定 backendOrder は webgl 優先、CPUは最終手段（既存挙動どおり）。
