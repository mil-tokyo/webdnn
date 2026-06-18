# WebDNN デモ・ギャラリー構想 / 実現可能性カタログ

> 2026-06-18 起票。ブラウザ向け ONNX 推論ランタイム WebDNN の「魅力的なデモ」を増やすための
> アイデア棚卸しと実現可能性（オペレータ予算）の調査記録。**今後デモを実装するときに再調査しないで済むよう、
> 一次情報をここに固定する。** ResNet50 デモ（`example/resnet/`）は原点として維持する前提。

## 目的と客層

2つの客層に同時に効くデモ群（ギャラリー）を作る。

- **ランディングページ来訪者（少しエンジニア寄り）** — 「WebDNN で自分も何か作れそう」と思わせる。
  技術的な幅・説得力が刺さる。
- **大学研究室オープンキャンパスの一般来訪者（子供多数）** — 読まずに即わかる・自分が関与できる・
  "魔法"感。ブース運用なので**回転率**（1人が長く占有しないか）も評価軸になる。

## 最重要の制約: WebDNN のオペレータ予算

デモの実現可能性はサポート済み ONNX オペレータで決まる。調査時点の実装状況：

| バックエンド | op数(概算) | 位置づけ |
|---|---|---|
| **CPU** | ~65 | 最も網羅的。リファレンス実装。低速だが必ず動く |
| **WebGL** | ~59 | GPU 加速・実用本命。視覚系デモはここで動かす |
| **WASM** | 18 | 最小フォールバック |
| **WebGPU** | 4 (Add/Conv/Gemm/Relu) | ごく初期段階 |

- オペレータ実装: `src/descriptor_runner/operators/{cpu,wasm,webgl,webgpu}/operators/standard/*.ts`
- 登録: `src/descriptor_runner/operators/{backend}/opEntriesStandard.ts`（および `opEntriesAll.ts`）
- **新規 op を足す**ときは「standard/ に実装ファイル追加 + opEntriesStandard.ts に登録」。
  WebGPU は WGSL シェーダ生成（`src/shader/webgpu/`, `npm run shader:webgpu`）も要る。

### 使える主なop（デモ設計の土台）

Conv, **ConvTranspose**（学習可能アップサンプル）, MatMul, Gemm, Softmax, **InstanceNormalization**,
Gather（**CPUのみ**）, Pad, Slice, Tile, Concat, Split, Transpose, Reshape, Flatten,
Squeeze/Unsqueeze, AveragePool/MaxPool/GlobalAveragePool, 各種活性化（Relu/LeakyRelu/Elu/Selu/
Sigmoid/Tanh/HardSwish/HardSigmoid/Softplus 等）, WebGL は **Reduce 10種**（Mean/Sum/Max/Min/L1/L2/...）。

### 無いop（＝デモの制約になる）

- **Resize / Upsample** — ❌。**追加価値が最も高い単一op**。これ1つで深度推定・AnimeGAN・
  多くのセグメンテーション/検出のFPN系が解放される。まず nearest、できれば bilinear。
- **DepthToSpace（PixelShuffle）** — ❌。超解像の sub-pixel conv に必要。実装は軽い
  （Reshape+Transpose+Reshape でベイクも可）。
- **LayerNormalization / GroupNormalization（ネイティブop）** — ❌。ただし **分解で実現可**
  （ReduceMean/Sub/Pow/ReduceMean/Add/Sqrt/Div/Mul/Add）。WebGL に Reduce が揃っているのが効く。
- **Attention / MultiHeadAttention（融合op）** — ❌。ただし **MatMul+Softmax+Reshape+Transpose で分解可**。
- **BatchNormalization（ネイティブop）** — ❌。だが推論時は**前段 Conv に畳み込んで（fold）**消えるため
  実害なし（ResNet50 が現に動いている）。ONNX 書き出し時の定数畳み込み or onnxsim で処理。
- **LSTM / GRU / RNN, Einsum, GridSample** — ❌。

### 効いてくる2つの事実（重要）

1. **`example/detr/` が既に Transformer を動かしている。** `conversion.py` は `nn.Transformer` を
   **opset 10** で書き出す。opset 10 では attention も LayerNorm もネイティブopが無く、
   **プリミティブに分解**されて出力される。つまり「小さな attention モデルはブラウザで動く」ことが
   実証済み（ネイティブ Attention/LayerNorm op を新設する必要はない）。大きいものは重すぎるだけ。
2. **InstanceNorm + ConvTranspose が揃っている** → style transfer / セグメンテーション / VAE といった
   **image-to-image / 生成系 CNN が新規op無しで動く**。

---

## ギャラリー方針と作る順序

各デモは独立した spec → plan → 実装サイクル（このディレクトリに `NN-<name>.md` で spec を置く）。
カメラ・深度・背景除去は **「webcam/画像 → 前処理 → モデル → canvas」パイプラインが共通**なので、
1本目で共通シェル＋入出力ハーネスを作ると2本目以降が安くなる（ボードゲームだけ独立）。

推奨ビルド順:

1. **カメラフィルタ**（style transfer）★1本目・設計中 → `01-camera-filter.md`
2. **ボードゲーム自己対戦AI**（独立・物語性最強）
3. **深度推定 → 擬似3D**（Resize 追加の最初の用途）
4. **背景除去 / 仮想背景**（カメラ系ハーネス再利用）

---

## デモ候補カタログ

実現性タグ: 🟢 = 今すぐ・新規op不要 / 🟡 = 簡単なop1つ追加（多くは Resize） / 🟠 = 分解 or 重め。

### A. 原点（維持）

#### ResNet50 画像分類 — 🟢（実装済み: `example/resnet/`）
- ops: Conv, (BN fold), Relu, MaxPool, GlobalAveragePool, Gemm, Add, Softmax。全部あり。
- 近代化案: webcam リアルタイム版／中身を MobileNetV3・EfficientNet-lite に差し替え「軽くて速い」を訴求。

### B. 既存モデル変換（映像系の "wow"・共通画像ハーネス）

#### カメラフィルタ / fast neural style transfer — 🟢（★1本目）
- モデル: Johnson 系 per-style net（~1.6M params, 256²入力）。Conv+InstanceNorm+Relu+**ConvTranspose**+Tanh+Pad。
- **新規op不要の条件**: アップサンプルを **ConvTranspose** で行う variant を使う/学習する
  （resize-conv 版は Resize が要るので 🟡 化する）。
- 客層: 子供◎（自分が変身）・回転率◎・エンジニア○（実時間GPU推論＋顔がブラウザ外に出ない＝プライバシー）。
- リスク: 高解像度時のFPS、ConvTranspose 由来のチェッカーボード（学習/設定で緩和）。WebDNN 旧版で実績あり。
- 発展: **AnimeGANv2**（アニメ風）は resize-upsample 採用で 🟡（Resize 追加）。"アニメ" の wow は更に上。

#### 背景除去 / 仮想背景（matting）— 🟡
- モデル: **U2-Netp（軽量版 ~4.7MB）** or MODNet-lite。Conv+(BN fold)+Relu+MaxPool+upsample+Sigmoid。
- U2-Net は bilinear Upsample を多用 → **Resize 必要**。アップサンプルを ConvTranspose に置換再学習すれば 🟢 化可。
- 客層: 子供○（「消えた！」）・エンジニア○（実用＋全部クライアント側でプライバシー）。
- リスク: モデルサイズ（フル U2-Net は ~168MB なので小型版必須）、Resize。

#### 単眼深度推定 → 擬似3Dパララックス — 🟡
- モデル: **MiDaS-small（~21MB）** など CNN エンコーダ・デコーダ。エンコーダは Conv/HardSwish 系 ✅、
  デコーダの bilinear アップサンプルに **Resize 必要**。
- 出力（逆深度マップ）を WebGL/three.js でパララックス（dolly-zoom 風）描画。
- 客層: 子供○（眺めて「おおっ」）・エンジニア○。**魔法感は最大**。
- リスク: Resize の品質（nearest だと粗い→bilinear 欲しい）、3D描画レイヤの実装。

#### 超解像 — 🟡
- モデル: **ESPCN（~25K params と極小）** or Real-ESRGAN-lite。Conv + **sub-pixel(DepthToSpace)** + Tanh。
- **DepthToSpace 必要**（実装軽い／Reshape+Transpose でベイクも可）。
- before/after スライダで見せる。子供○・エンジニア○。リスク低。

#### 物体検出アップグレード（YOLO-nano / NanoDet）— 🟡
- Conv+(BN fold)+SiLU/Sigmoid+Concat+MaxPool。FPN/neck の Upsample で **Resize 必要**が多い。
- 後処理（NMS, anchor decode）は JS。DETR の隣に「リアルタイム webcam 検出」を置ける。
- リスク: FPN の Resize、デコード実装の手間。

#### 姿勢推定（pose）— 🟢
- 軽量 heatmap 系（lightweight OpenPose 等）は Conv のみ → 🟢。argmax/decode は JS。
- webcam 骨格オーバーレイ → スクワットカウンタ等のミニゲームに発展可。子供◎。
- （注: MoveNet は一部 op 要確認。Conv のみの実装を選ぶこと。）

### C. 自前で学習（自動生成データ → 面白い物）

#### ボードゲーム自己対戦AI（AlphaZero-lite）— 🟢（独立・物語性◎）
- モデル: 小型 ResNet トランク（Conv+BN fold+Relu+residual Add）+ policy head（→Gemm→Softmax）
  + value head（→Gemm→Tanh）。**全部あり・新規op不要**。
- 学習: PyTorch で **自己対戦（MCTS）→ 学習データを自動生成** → ONNX。データセット不要＝
  ユーザーの「自動生成データで学習」路線に直球。
- ブラウザ: JS で MCTS、各ノード評価で NN 推論。
- ゲーム候補: **Gomoku（9×9 or 15×15）/ Othello（8×8）/ Connect-4**。
- 客層: 子供◎（対戦して本気で負ける）・エンジニア◎（自己対戦学習→ONNX→ブラウザMCTS の一気通貫が最も差別化）。
- リスク: 学習計算コスト、MCTS 実装。回転率は低め（1人が数分占有）。

#### お絵描き認識（Quick, Draw! 風）— 🟢
- 小型 Conv CNN + Softmax。canvas に描く→即認識。データは Google QuickDraw or 合成。
- 子供◎・軽量・即インタラクティブ。リスク低。

#### VAE 生成器 / 潜在空間エクスプローラ — 🟢
- 推論はデコーダのみ: z（JSでサンプル）→ Gemm/**ConvTranspose**/Relu/Sigmoid → 画像。
- スライダで潜在変数 → 生成画像がモーフィング。MNIST/FashionMNIST/顔（小型）。
- 「生成AIがブラウザで動く」。リスク低（顔は小型だと品質限界）。

#### （stretch）nano char-GPT — 🟠
- embedding（**Gather=CPUのみ** ⚠️）+ LayerNorm（分解）+ attention（MatMul+Softmax）+ Gemm + GELU(近似)。
- DETR が分解の前例。tiny 構成（n_layer≈4, n_embd≈128, char-level）なら動く見込みだが **CPU 律速で低速**。
- ユーザー方針「transformer は重すぎ」に配慮し**最小実証枠**。優先度低。

---

## 共通画像ハーネス（カメラ/深度/背景除去/検出で再利用）

1本目で切り出しておくと2本目以降が安い。責務:

- 入力ソース: `<video>`(webcam) / `<img>`(ファイル/ドラッグ&ドロップ) を統一インタフェース化。
- 前処理: リサイズ・正規化（mean/std）・NCHW 変換 → `CPUTensor`。
- 推論: `runner.run([tensor])`（backendOrder で WebGL→WASM→CPU フォールバック）。
- 後処理→描画: 出力テンソル → `<canvas>`（画像化 / オーバーレイ / before-after スライダ）。
- 計測: 推論時間・FPS 表示（デモとして「速さ」を見せる）。

公開APIの最小形（`src/descriptor_runner/index.ts`）:
```js
const runner = await WebDNN.load("model/", { backendOrder: ["webgl", "wasm", "cpu"] });
const input = new WebDNN.CPUTensor([1, 3, H, W], "float32", chw);
const [out] = await runner.run([input]);
// out.data: Float32Array
```

---

## ステータス

- [x] **01 カメラフィルタ** — コード実装完了・ブラウザでパイプライン検証済（model load / 192²ライブ / HUD / 256²キャプチャ）。light model + ライブ192²/キャプチャ256²。**残: GPUで画風を学習→`styles/styles.json`更新**（[example/style_transfer/README.md](../../example/style_transfer/README.md)）。副産物の知見: core修正（`util.ts` の Long→number 変換）と「export は opset11＋ORT最適化が必須」。
- [ ] 02 ボードゲーム自己対戦AI — backlog
- [ ] 03 深度推定 → 擬似3D — backlog（Resize 追加の初回）
- [ ] 04 背景除去 / 仮想背景 — backlog
- [ ] その他（超解像 / 検出 / 姿勢 / お絵描き認識 / VAE / nano-GPT）— アイデアプール

> メモ: 🟡 デモの大半は **Resize（nearest→bilinear）op の追加**で解放される。Resize を一度実装すれば
> 深度・AnimeGAN・背景除去・検出FPN がまとめて前進する。投資対効果が高い共通基盤。
