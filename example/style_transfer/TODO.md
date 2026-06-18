# Camera Filter デモ — 残作業 TODO（GPUマシン引き継ぎ用）

別マシン（GPU有）でここから続ける人向けの作業チェックリスト。
背景・設計は [README.md](README.md) / [spec](../../docs/demos/01-camera-filter.md) /
[実装計画＋Phase 0実測](../../docs/demos/01-camera-filter-plan.md)。

## 現在地（2026-06-18 時点）
- ブランチ **`demo/style-transfer`**（master 未マージ）。コード実装＋ブラウザでパイプライン検証済、typecheck / 30 unit tests 緑。
- できていないのは **画風モデルの学習**（GPU必須）と、それを使った **実ブラウザでの最終確認**。
- Phase 0 で WebDNN 本体のバグ2件を修正済（`fix(core)` の `util.ts` Long変換、export の opset11+ORT最適化）。

---

## 0. このマシンでの環境セットアップ
- [ ] ブランチ取得: `git fetch && git switch demo/style-transfer`
- [ ] Node 依存＋ビルド: `npm install` → **`npm run build:all`**
      ⚠️ **必須**: core修正(`util.ts`)は src にあるが、`dist/webdnn.js` は gitignore。各マシンで build しないと
      **古い dist で Conv が誤って "buffer exceeds limit" を投げる**。
- [ ] Python(uv): `uv pip install torch torchvision onnx onnxruntime pillow numpy`
      （GPUマシンは CUDA 版 torch を入れる。`onnxsim` は使わない＝この環境で segfault したため、
      export は onnxruntime の optimizer を使用）
- [ ] 動作確認（任意）: `npm run server` → `http://localhost:8080/example/style_transfer/`
      空 manifest なら「学習済みstyleがありません」が出れば OK。

## 1. 【必須】画風モデルの学習（メイン作業）
1 モデル = 1 画風。fully-convolutional なので 256² で学習すれば 192²/256² 両方で動く。
推奨 5〜6 画風（例: 浮世絵 / ゴッホ / ムンク / モザイク / 点描）。

- [ ] 学習データ COCO train2014 取得（README の手順、`~/data/coco/train/train2014/*.jpg`）
- 各画風について:
  - [ ] 学習（light既定, RTX4070 で ~1-2h/style）
        ```bash
        cd example/style_transfer/train
        uv run python train_style.py --dataset ~/data/coco/train \
          --style-image /path/to/<art>.jpg --out ../styles/<id>/transformer.pth
        ```
  - [ ] ONNX 化（★学習と同じ light フラグ。opset11+ORT最適化は自動）
        ```bash
        uv run python export_to_onnx.py --weights ../styles/<id>/transformer.pth \
          --out ../styles/<id> --base 16 --num-res 3 --end-k 3
        ```
  - [ ] サムネ `styles/<id>/thumb.jpg`（128px程度）
  - [ ] `styles/styles.json` にエントリ追加:
        `{ "id": "<id>", "name": "<表示名>", "dir": "styles/<id>/", "thumb": "styles/<id>/thumb.jpg" }`

## 2. 【必須】実ブラウザでの最終確認
プレビューは rAF が絞られ「連続アニメ」「実際の画風（未学習=黒）」は確認できなかった。実タブで:
- [ ] Chrome / Safari / Firefox / Edge で `example/style_transfer/` を開き、**実際に画風変換された映像**が出る／ライブが滑らか（192²で~12fps目安）
- [ ] 高画質キャプチャ（256²・PNG保存）が綺麗に出る
- [ ] webカメラ（localhost か https でのみ getUserMedia 許可）
- [ ] before/after トグル
- [ ] 4バックエンド `?backend=webgl|wasm|cpu`（CPUは低速だが動く）。数値突合するなら各 `styles/<id>/expected.bin` と比較。

## 3. 【任意】プラン記載の追加タスク（低優先）
- [ ] `train/convert_zoo.py` 作成 — ONNX Model Zoo の fast-style を変換＋アップサンプルop検査
      （Resize/Upsample を含むなら WebDNN 未対応 → 見送り or 別計画で Resize op 追加）。詳細は plan §Task 5.2。
- [ ] 画風を増やす
- [ ] heavy 構成を試す場合は学習・export とも `--base 32 --num-res 5 --end-k 9`
      （ディテール↑だがライブは 128²/6fps が上限。perf 表は plan / README 参照）

## 4. 完了したらマージ
- [ ] 実機で動作 OK を確認 → master へマージ（ユーザー指示で）。
      `dist/` は gitignore なので各環境で `npm run build:all` する前提。

---

## ハマりどころメモ
- **dist 再ビルド必須**（上記 0）。古い dist だと Conv 誤エラー。
- **export = opset 11 + ORT BASIC 最適化が必須**（`export_to_onnx.py` が自動。torch legacy exporter の
  `Identity/Cast/Concat` 等の動的pad足場を畳み込み、WebDNN対応op だけにする）。
- **モデルは入力サイズ可変** → 1 モデルでライブ192²＋キャプチャ256²（再export不要）。
- **学習と export の `base/num-res/end-k` は一致必須**（state_dict 整合）。light=既定(16/3/3)。
- 前処理は `[0,255]` スケール・正規化なし（fast-style の流儀。`infer.js` 実装済）。
