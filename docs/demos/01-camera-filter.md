# Demo 01: カメラフィルタ（リアルタイム neural style transfer）— 設計仕様

> 2026-06-18。ギャラリー構想とオペレータ予算は [README.md](README.md) を参照。本書は1本目の実装仕様。
> 実現性: 🟢（自作 ConvTranspose 版は新規op不要）。

## 1. 目的・客層

webカメラ/画像をリアルタイムに画風変換し、`<canvas>` に表示する。

- **ランディング来訪者（エンジニア寄り）**: 「GPUでブラウザ内推論」「自分のPyTorchモデルを学習→ブラウザに載せる」を実演。
- **オープンキャンパス一般客（子供多数）**: 自分が即変身する驚き。タップで画風切替。回転率重視。

WebDNN の主張（サーバ不要・プライバシー＝顔がブラウザ外に出ない・実時間GPU推論）を最も素直に体現する。

## 2. スコープ

**In**: 入力＝webカメラ＋サンプル動画＋画像ファイル（両対応）。自作学習 style（本線）＋学習済みONNX（ボーナス）。
全画面出力＋画風サムネイル帯＋before/afterトグル＋HUD（推論ms/FPS/バックエンド）。4バックエンドで動作。

**Out（やらない）**: 動画ファイルの書き出し/録画、複数画風の同時合成、任意ユーザ画像からのオンザフライ学習。

## 3. アーキテクチャ

### 3.1 共通画像ハーネス（demos 03・04 で再利用前提に切り出す）

責務ごとに小さく分離する。各ユニットは「何をするか / どう使うか / 依存」が独立して言えること。

- **`ImageSource`** — 入力ソースを統一IF化。
  - `setSource(kind: "webcam" | "sample" | "image", payload?)` / `start()` / `stop()`
  - webcam は `getUserMedia` → `<video>`、sample はループ再生 `<video>`、image は `<img>`/ドラッグ&ドロップ。
  - `requestAnimationFrame` ループでフレームを供給（スロットル可）。依存: DOM。
- **`Preprocess(frame, {size, layout:"NCHW", scale})` → `CPUTensor([1,3,H,W])`**
  - フレームを `size`(=256) に縮小、RGB 抽出、**スケール `[0,255]` のまま**（fast-style は ImageNet 正規化しない。§4.3）、NCHW 充填。依存: OffscreenCanvas, `WebDNN.CPUTensor`。
- **推論** — `runner.run([tensor])`（`backendOrder: ["webgl","wasm","cpu"]`）。依存: WebDNN 公開API（`src/descriptor_runner/index.ts`）。
- **`Postprocess(outTensor, {clamp:[0,255]})` → `ImageData`** — clamp → CHW→RGBA → `putImageData`。依存: なし。
- **`Metrics`** — 推論時間・FPS・確定バックエンド名を計測/保持し HUD へ。

### 3.2 カメラフィルタ固有

- **`StyleManager`** — 画風モデル群のメタ（id, 表示名, サムネ, onnxパス）保持。`select(id)` で遅延ロード＆現行 runner 差替。プリロード戦略は「初期1個＋選択時ロード＋ロード中インジケータ」。
- **UI制御** — サムネイル帯のタップ、webカメラ許可ボタン、before/afterトグル、HUD。

データフロー: `ImageSource → Preprocess → runner(現行style) → Postprocess → canvas`（毎フレーム）。`StyleManager.select` は runner だけ差し替え、ループは継続。

## 4. モデル仕様

### 4.1 TransformerNet（Johnson 系）構成

| 段 | 層 | 備考 |
|---|---|---|
| in | Pad(reflect) + Conv(3→32, k9,s1) + InstanceNorm + ReLU | |
| down | Conv(32→64, k3,s2) + IN + ReLU | 1/2 |
| down | Conv(64→128, k3,s2) + IN + ReLU | 1/4 |
| res×5 | [Conv(128,128,k3,s1)+IN+ReLU + Conv(128,128,k3,s1)+IN] + skip(Add) | |
| up | **ConvTranspose(128→64, k3,s2,pad1,outpad1)** + IN + ReLU | ×2 |
| up | **ConvTranspose(64→32, k3,s2,pad1,outpad1)** + IN + ReLU | ×2 |
| out | Pad(reflect) + Conv(32→3, k9,s1) | 活性化なし、後処理で clamp[0,255] |

### 4.2 使用op と対応状況

Conv, **ConvTranspose**, InstanceNormalization, Relu, Add(skip), Pad, Clip(=clamp)。**全て CPU/WebGL に実装済み → 新規op不要（🟢）**。
- 確認済: **Pad は reflect モード対応**（`operators/{cpu,webgl}/operators/standard/pad11.ts` に constant/edge/reflect）。ReflectionPad2d はそのまま動く。
- 前処理/後処理は **`WebDNN.Image.getImageArray` / `WebDNN.Image.setImageArrayToCanvas`** を利用（後者は `Uint8ClampedArray` で[0,255]自動clamp＋境界クロップ `srcX/srcY/srcW/srcH` 対応＝チェッカーボード/パディングノイズ除去に使える）。

### 4.3 前処理・後処理（重要）

- 入力: RGB を **`[0,255]` スケールのまま**（fast-style の TransformerNet は ImageNet mean/std 正規化を**しない**。VGG 正規化は学習時の損失内のみ）。NCHW。
- 出力: 生値を **`clamp(0,255)`** → uint8 → RGBA。最終 Tanh は付けない（pytorch/examples 準拠）。Tanh×scale 版は任意。

## 5. 学習

### 5.1 自作学習（本線・🟢）

- 環境: RTX 4070 (12GB) で余裕（VRAM ~3–5GB）。
- データ: COCO train2014（無料・容易入手）。画風は画像1枚/style。
- 損失: VGG16 perceptual（content + style(gram)）。torchvision の VGG16 を凍結利用。total variation は任意。
- 設定: 256² crop, batch 4, 約2 epoch, **~1–2時間/style**。
- 出力: `export_to_onnx.py`（`example/resnet/export_pytorch_model.py` に倣う）。1 style = 1 ONNX。
- **アップサンプルは ConvTranspose 固定**（resize-conv は使わない＝Resize op を呼ばないため🟢を保証）。

### 5.2 学習済みONNX（ボーナス）

- ONNX Model Zoo の fast-neural-style（candy / mosaic / rain_princess / udnie / pointilism）を変換。
- **要検証**: これらのアップサンプルが ConvTranspose か Upsample(Resize) か（onnx を読んで op 確認）。
  - ConvTranspose なら即🟢で採用。
  - Upsample(Resize) なら → (a) Resize op を WebDNN に追加（カタログ的に高ROI、深度/背景除去/検出にも波及）、または (b) 学習済みは見送り自作 style のみ。
- **1本目の必達ライン**: 自作 ConvTranspose style が動くこと。学習済みは乗ればボーナス。

### 5.3 チェッカーボード対策

ConvTranspose 由来の格子模様は kernel/stride 調整＋学習で緩和。残るなら sub-pixel(DepthToSpace) 代替を検討（別途 op 追加）。

## 6. UI / UX

- 全画面に**変換後映像**、下部に**画風サムネイル帯**（タップで即切替、子供向けに大きく）。
- 画風は **5–6種**を初期搭載（例: 浮世絵・ゴッホ・ムンク・モザイク・点描＋アニメ風）。自作 style を足せる構成。
- 「**webカメラを許可**」ボタン。未許可でも**サンプル動画を自動再生**（放置で動く看板＝ランディング）。
- 画像ファイルはドラッグ&ドロップ受け。
- **before/after** トグル（or ドラッグ split）で原画と比較（エンジニア向け）。
- **HUD**: 推論ms / FPS / 確定バックエンド名（「GPUでブラウザ内推論」を可視化）。

## 7. 性能・フォールバック

- 既定 256²、WebGL でインタラクティブ（目標 ~10–30fps / ラップトップ）。
- 重い端末は 192² に自動ダウンスケール。`backendOrder: webgl→wasm→cpu` で非対応環境も動作（低速）。
- 毎フレーム推論が重い場合はフレームスキップ（入力 fps と推論 fps を分離）。

## 8. テスト

- ユニット（vitest, GPU不要）: `Preprocess`/`Postprocess` の数値（既知入力→期待RGBA）、`StyleManager` の状態遷移。
- モデル目視: 1 style ONNX を 4バックエンドで実行し、CPU 出力を基準に WebGL/WASM の差が許容内（既存 `test/model_test/runner` 流儀）。
- 手動: webカメラ/サンプル/画像の3経路、画風切替、before/after、HUD 表示。

## 9. 成果物・ファイル配置

```
example/style_transfer/
  index.html            # デモUI
  index.js              # 配線（ImageSource/StyleManager/ループ）
  harness/              # 共通画像ハーネス（demos 03・04 へ昇格予定）
    imageSource.js
    preprocess.js
    postprocess.js
    metrics.js
  styles/               # *.onnx（自作＋変換済み）, サムネ
  train/
    train_style.py      # 自作学習
    export_to_onnx.py   # ONNX書き出し
    convert_zoo.py      # 学習済みzoo変換＋op検査
```

## 10. 実装時に検証する未確定事項

1. ~~Pad reflect~~ → **解決済**: CPU/WebGL とも reflect 対応（`pad11.ts`）。
2. **学習済み zoo モデルのアップサンプルop**（ConvTranspose か Resize か）→ §5.2 の分岐。
3. **WebGL での実FPS**（256²/192²）と端末差。
4. ConvTranspose の**チェッカーボード**実害の程度（`setImageArrayToCanvas` の境界クロップで緩和可）。

## 11. 受け入れ基準

- [ ] 自作 ConvTranspose style 1個以上が ONNX 化され、WebGL でリアルタイム変換が動く。
- [ ] webカメラ／サンプル自動再生／画像D&D の3入力が動作。
- [ ] 画風サムネイル帯で切替、before/after、HUD（ms/FPS/backend）表示。
- [ ] 4バックエンドで実行可能（CPU基準と出力一致）。
- [ ] 共通ハーネスが demos 03・04 から再利用できる粒度で分離されている。
- [ ] 自作学習スクリプト（train + export）が RTX 4070 で完走し、README に手順記載。
