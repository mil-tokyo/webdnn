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
source ~/emsdk/emsdk_env.sh   # シェルごとに有効化（~/.zshrc 等へ追記推奨）
emcc -v                        # 導入確認
```

## ビルド

```bash
cd <repo>
npm run shader:wasm   # eigen を取得し emcc でビルド、worker.ts を生成
```

成功すると `src/descriptor_runner/operators/wasm/worker/worker.ts` がスタブから
実バイナリ埋め込み版に置き換わる（このファイルは gitignore 対象）。

その後、WASM を通常ビルドに含めるには `package.json` の `build:all` に `shader:wasm` を戻す:

```json
"build:all": "npm run shader:webgpu && npm run shader:wasm && npm run makeShaderList && npm run build",
```

（現状の `build:all` は emscripten 非依存で完結させるため `shader:wasm` を除外している。
emscripten を導入したら上記のように戻す。）

## 検証

emcc 導入後、ブラウザ目視ランナー（`docs/testing.md` 第 3 層）で backend に `wasm` を選び、
全ケース `ALL OK` を確認する。Playwright で自動化する場合は `test/e2e/` に
`webgpu.spec.ts` と同型の `wasm.spec.ts` を追加できる（WASM は GPU 不要なため CI でも
動かせる可能性があるが、emscripten ビルド成果物が必要）。
