# emscripten のセットアップ（WASM バックエンドのビルド用）

WASM バックエンドの C++ カーネル（`src/shader/wasm/src/**/*.cpp`）は emscripten でビルドする。
emscripten は容量が大きいため、**システムグローバルに 1 度だけ導入**する
（ワークツリー単位では入れない／CI では使わない）。

## いつ必要か

通常の開発・CI では不要。`scripts/ensure-generated-stubs.mjs` が
`src/descriptor_runner/operators/wasm/worker/worker.ts` のスタブを供給するため、
typecheck・lint・ビルド・CPU/WebGPU/WebGL のテストは emscripten なしで通る。

**WASM バックエンドを実際に動かす**には、emscripten を導入して `worker.ts` を
実バイナリ埋め込み版に生成する必要がある。

## 推奨バージョン

- emscripten **3.1.x 以降**（本プロジェクトは `-O3` と `ALLOW_MEMORY_GROWTH=1` を使用）。

## 導入手順（emsdk）

```bash
git clone https://github.com/emscripten-core/emsdk.git ~/emsdk
cd ~/emsdk
./emsdk install latest
./emsdk activate latest
emcc -v   # 確認のみ（下記のとおり、ビルド時に都度 source する必要はない）
```

**`source emsdk_env.sh` を毎回手動で行う必要はない。** ビルドスクリプトが内部で
`emsdk_env.sh` を source するため、非対話シェル（`npm run` / CI / ツール駆動）でも動く。

emsdk を `~/emsdk` 以外に置いた場合は環境変数 `EMSDK` でその場所を指定する:

```bash
export EMSDK=/path/to/emsdk   # 既定は ~/emsdk
```

## ビルド

```bash
cd <repo>
npm run shader:wasm   # scripts/build-wasm.sh が emsdk_env.sh を source → eigen 取得 → emcc ビルド → worker.ts 生成
```

成功すると `src/descriptor_runner/operators/wasm/worker/worker.ts` がスタブから
実バイナリ埋め込み版に置き換わる（このファイルは gitignore 対象、ディスク上に残る）。
以後 `npm run build` / `build:all` はこの実 `worker.ts` を取り込むため、**`build:all` を
書き換える必要はない**（emscripten 未導入の環境では `scripts/ensure-generated-stubs.mjs` が
スタブを供給し、ビルド自体は通る＝WASM はオプトイン）。

## 検証

`npm run shader:wasm` 実行後（= 実 `worker.ts` 生成済み）に:

```bash
npm run build && npm run fixtures
npx playwright test test/e2e/wasm.spec.ts   # WASM バックエンドを自動検証
```

`test/e2e/wasm.spec.ts` は実 `worker.ts` が在る時のみ実行され、スタブの場合は skip する
（CPU フォールバックでの偽 PASS を避けるため）。ブラウザ目視（`docs/testing.md` 第 3 層）で
backend に `wasm` を選んで全ケース `ALL OK` を確認してもよい。

## emcc バージョンと既知の注意

- emscripten **3.1.x〜6.x** で動作確認（emcc 6.0.0 で E2E PASS）。
- emcc 6.x は `HEAPU8` を既定で `Module` に公開しないため、`compile.py` の emcc 呼び出しに
  `-s EXPORTED_RUNTIME_METHODS=HEAPU8` を付与している（worker の `pre.js` が `Module.HEAPU8` を使う）。
