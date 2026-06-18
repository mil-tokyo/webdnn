# Camera Filter — リアルタイム neural style transfer (WebDNN)

webカメラ/画像をブラウザ内の GPU 推論（WebDNN）でリアルタイム画風変換するデモ。
**ライブプレビュー 192²（~12fps @ Apple M2）＋ 高画質キャプチャ 256²（~150ms）**。
映像はサーバに送らず、ブラウザの外に出ない。

設計の詳細: [spec](../../docs/demos/01-camera-filter.md) /
[実装計画・Phase 0 実測](../../docs/demos/01-camera-filter-plan.md)。

## 起動

```bash
npm run build:all      # dist/webdnn.js を生成（emscripten 非依存）
npm run server         # http-server → http://localhost:8080
# ブラウザで http://localhost:8080/example/style_transfer/ を開く
```

- バックエンド切替: `?backend=webgl`（既定）/ `cpu` / `wasm`。例: `.../?backend=cpu`
- 操作: 📷webカメラ / ✨高画質キャプチャ（256²・PNG保存）/ ⇄before-after / 🖼画像を開く（ドラッグ&ドロップ可）
- 初期状態は `styles/styles.json` が空 →「学習済みstyleがありません」。下記で学習して追加する。

## 画風モデルの学習（RTX 4070 等の GPU で）

1 モデル = 1 画風。fully-convolutional なので **256² で学習すれば 192²/256² 両方で動く**。

```bash
# 1) 学習データ（COCO train2014, ImageFolder 形式）
mkdir -p ~/data/coco/train && cd ~/data/coco \
  && curl -O http://images.cocodataset.org/zips/train2014.zip \
  && unzip -q train2014.zip -d train

# 2) 学習（既定 = light: base16/res3/endk3, ~270K params, ~1-2h/style）
cd <repo>/example/style_transfer/train
uv run python train_style.py --dataset ~/data/coco/train \
  --style-image /path/to/ukiyoe.jpg --out ../styles/ukiyoe/transformer.pth

# 3) ONNX 化（★学習と同じ light フラグで。opset11 + ORT 最適化は自動）
uv run python export_to_onnx.py --weights ../styles/ukiyoe/transformer.pth \
  --out ../styles/ukiyoe --base 16 --num-res 3 --end-k 3

# 4) サムネ（128x128 程度）を styles/ukiyoe/thumb.jpg に置く（任意）
```

`styles/styles.json` にエントリ追加:

```json
[
  { "id": "ukiyoe", "name": "浮世絵", "dir": "styles/ukiyoe/", "thumb": "styles/ukiyoe/thumb.jpg" }
]
```

- `dir` は末尾 `/` 必須（WebDNN.load が `dir + model.onnx` を読む）。`thumb` 省略時はボタンに名前を表示。
- ディテール優先の heavy 構成にするなら学習・export とも `--base 32 --num-res 5 --end-k 9`（ただしライブは 128²/6fps が上限）。

## 性能（実測: Apple M2 / WebGL, steady-state）

| 解像度 | heavy (1.68M) | **light (270K, 既定)** |
|---|---|---|
| 128² | 167ms / 6fps | 36ms / 28fps |
| 192² | 1740ms / 0.6fps | 85ms / 12fps |
| 256² | 2500ms / 0.4fps | 142ms / 7fps |

→ ライブ = 192² light、キャプチャ = 256² light。heavy は 192² 以上で実用外。

## 前提（Phase 0 で判明・対応済）

- **export は opset 11 ＋ ORT BASIC 最適化が必須**。torch の legacy exporter が出す
  `Identity`/`Cast`/`Concat`/`ConstantOfShape` 等（ReflectionPad の動的padding機構）を定数畳み込みし、
  WebDNN 対応 op（Conv/ConvTranspose/InstanceNormalization/Relu/Add/Pad）だけに圧縮する。
  → `export_to_onnx.py` が自動で実施＋未対応 op が残らないか assert。
- **core 修正が前提**: `src/descriptor_runner/util.ts` の `intOrLongToInt` を修正済
  （protobufjs の Long を `instanceof` で取りこぼし、`number + Long` が文字列連結 → Conv `pads` 破損 →
  出力形状が爆発して誤って "Conv: buffer exceeds limit" を投げていた）。`dist` を再ビルドすれば反映。
- webカメラは **localhost か https** でのみ許可（`getUserMedia` の制約）。

## 構成

| ファイル | 役割 |
|---|---|
| `index.html` / `index.js` | UI と描画ループ（192 ライブ + 256 キャプチャ） |
| `harness/infer.js` | 前処理(`getImageArray`)→`run`→描画(`setImageArrayToCanvas`)。demos 03/04 で再利用予定 |
| `harness/imageSource.js` | webカメラ / 画像 / サンプルの統一入力 |
| `harness/metrics.js` | FPS・推論ms（unit test 有） |
| `styleManager.js` | 画風モデルの遅延ロード/切替（unit test 有） |
| `train/model.py` | parametric TransformerNet（heavy 既定 / light 引数） |
| `train/train_style.py` | 学習（COCO + 画風1枚, VGG16 perceptual loss） |
| `train/export_to_onnx.py` | .pth → ONNX(opset11) + ORT最適化 + parity/op 検証 |
