# WebDNN 移行前ベースライン（2026-06-17 実測）

## 環境

- Node: v26.3.0（homebrew 経由でインストール；PATH に未設定だったため `brew install node` を実行）
- npm: 11.16.0
- Python: 3.9.6（macOS Xcode 付属）
- emscripten (emcc -v): 未インストール
- yarn: 未インストール

## 依存インストール

- `yarn`: 失敗（コマンド未インストール。代替として `npm install` を実行し成功。287 パッケージ追加。非推奨パッケージ警告多数、脆弱性 24 件）
- `python setup.py develop`: 部分的成功 / 失敗あり
  - `--user` フラグ付きで実行。egg-link 作成は成功したが、依存パッケージ numpy のインストールが失敗。
  - 失敗理由: numpy 最新版 (2.5.0rc1) が `setup.py` 形式を持たず `easy_install` が処理できない。
  - webdnn パッケージ本体の egg-link は `/Users/milhidaka/Library/Python/3.9/lib/python/site-packages/webdnn.egg-link` に作成済み。

## ビルド成否

注記：`npm run` は webpack の非ゼロ終了コードをマスクして 0 を返すことがある。各ステップは webpack を直接呼び出した場合の終了コードで評価している。Node v26 と webpack@5.24.4 の OpenSSL 非互換のため、全 webpack ステップは `NODE_OPTIONS=--openssl-legacy-provider` を設定して実行した（設定なしでは `ERR_OSSL_EVP_UNSUPPORTED` で即時クラッシュ）。

| ステップ | 結果 | 備考（失敗理由など） |
|----------|------|----------------------|
| shader:webgpu | OK | `node src/shader/webgpu/compile.js` 正常終了。shaders.ts を更新。 |
| shader:wasm | NG | スクリプトが `python`（非 `python3`）を呼び出すためシェルで失敗。`python3` で実行しても emcc 未インストールのため FileNotFoundError。 |
| makeShaderList | OK | `python3 scripts/make_operator_entries.py` で正常終了（`python` コマンド不在のため npm スクリプト呼び出しは失敗するが、直接実行は成功）。 |
| build (webdnn.js) | NG | webpack exit 1。`./operators/wasm/worker/worker` モジュール未生成（shader:wasm 未実行のため）。TypeScript エラー 3 件。ただし webdnn.js は出力済み（1.17 MiB）。 |
| build:core | NG | webpack exit 1。同上 TypeScript エラー 2 件（worker モジュール不在）。webdnn-core.js は出力済み（768 KiB）。 |
| build:cpu | NG | webpack exit 1。同上 TypeScript エラー 2 件。op-cpu.js は出力済み（590 KiB）。 |
| build:wasm | NG | webpack exit 1。worker モジュール不在により Module not found エラー含む 3 件。op-wasm.js は出力済み（612 KiB）。 |
| build:webgl1-4096 | NG | webpack exit 1。TypeScript エラー 2 件（worker モジュール不在）。op-webgl1-4096.js は出力済み（732 KiB）。 |
| build:webgl1-16384 | NG | webpack exit 1。TypeScript エラー 2 件（worker モジュール不在）。op-webgl1-16384.js は出力済み（732 KiB）。 |
| build:webgl2-4096 | NG | webpack exit 1。TypeScript エラー 2 件（worker モジュール不在）。op-webgl2-4096.js は出力済み（732 KiB）。 |
| build:webgl2-16384 | NG | webpack exit 1。TypeScript エラー 2 件（worker モジュール不在）。op-webgl2-16384.js は出力済み（732 KiB）。 |
| build:webgpu | NG | webpack exit 1。TypeScript エラー 2 件（worker モジュール不在）。op-webgpu.js は出力済み（648 KiB）。 |

### webpack エラーの根本原因

全 webpack ステップで共通して発生するエラー:

```
Module not found: Error: Can't resolve './operators/wasm/worker/worker'
TS2307: Cannot find module './operators/wasm/worker/worker'
```

`worker.ts` は `shader:wasm`（emscripten）によって生成されるはずのファイルで、emcc 未インストールのため生成されない。

## 生成された dist

```
ls -la dist/ の結果（2026-06-17 実測）:

total 13360
drwxr-xr-x@ 23  736 Jun 17 20:25 .
drwxr-xr-x@ 32 1024 Jun 17 20:24 ..
drwxr-xr-x@  6  192 Jun 17 20:24 backend/
drwxr-xr-x@ 10  320 Jun 17 20:24 core/
drwxr-xr-x@  7  224 Jun 17 20:24 image/
-rw-r--r--@  1  461 Jun 17 20:24 image.d.ts
-rw-r--r--@  1  943 Jun 17 20:24 index.d.ts
drwxr-xr-x@  4  128 Jun 17 20:24 interface/
-rw-r--r--@  1 1614 Jun 17 20:24 logging.d.ts
drwxr-xr-x@  4  128 Jun 17 20:24 math/
-rw-r--r--@  1  237 Jun 17 20:24 math.d.ts
-rw-r--r--@  1 590013 Jun 17 20:24 op-cpu.js
-rw-r--r--@  1 612518 Jun 17 20:24 op-wasm.js
-rw-r--r--@  1 732778 Jun 17 20:25 op-webgl1-16384.js
-rw-r--r--@  1 732778 Jun 17 20:24 op-webgl1-4096.js
-rw-r--r--@  1 732778 Jun 17 20:25 op-webgl2-16384.js
-rw-r--r--@  1 732778 Jun 17 20:25 op-webgl2-4096.js
-rw-r--r--@  1 663365 Jun 17 20:25 op-webgpu.js
drwxr-xr-x@ 10  320 Jun 17 20:24 operators/
drwxr-xr-x@  7  224 Jun 17 20:24 separateBuild/
-rw-r--r--@  1  728 Jun 17 20:24 util.d.ts
-rw-r--r--@  1 786645 Jun 17 20:24 webdnn-core.js
-rw-r--r--@  1 1222024 Jun 17 20:24 webdnn.js
```

shasum（JS バンドルのみ）:

```
8e47afaa270bd4a6bd259e29ad1397fa051ab503  dist/op-cpu.js
8a7b4f26e8abc910108417384e0e1e28fb1e9706  dist/op-wasm.js
d9fe920e7b46ee6148e1890e49885d614dadf31b  dist/op-webgl1-16384.js
d9fe920e7b46ee6148e1890e49885d614dadf31b  dist/op-webgl1-4096.js
d9fe920e7b46ee6148e1890e49885d614dadf31b  dist/op-webgl2-16384.js
d9fe920e7b46ee6148e1890e49885d614dadf31b  dist/op-webgl2-4096.js
6d90692626543567d826f3181d0b9873445489d9  dist/op-webgpu.js
b13f8b79af200168c0e94f2e89e6bc09ce6a8d3d  dist/webdnn-core.js
c2fdc3eb47b119b7b6000c746b1fe90b1f42b4e9  dist/webdnn.js
```

注記: webgl1-4096 と webgl1-16384 の SHA が一致しているのは、テクスチャサイズが TypeScript 定数ではなく webpack 定義変数で制御されているためか、ビルド時にそのフラグが実際に差分を生んでいない可能性がある。

## バックエンド別の現状評価

- **CPU**: テストランナー配信 HTTP 200 確認（`http://localhost:8080/test/model_test/runner/standard.html`）。op-cpu.js は生成済み。ただし worker モジュール不在による TypeScript エラー付きビルド。実ブラウザ実行テストは後続フェーズで実施。
- **WASM**: emscripten（emcc）未インストールのため `shader:wasm` が失敗し、`operators/wasm/worker/worker.ts` が生成されない。このファイルは全ビルドの TypeScript エラーの根本原因にもなっている。op-wasm.js は出力されているが WASM worker なしでは実際には動作しない。emcc インストール（またはモダン化フェーズでの wasm-pack 等への移行）が必要。
- **WebGL**: ビルドは TypeScript エラー付きで出力済み（exit 1 だがファイル生成される）。webgl1-4096/16384 および webgl2-4096/16384 の各バンドルは同サイズ・同 SHA であり、テクスチャサイズ定数が実際にバンドル差分を生んでいない疑いがある（要確認）。現状のツールチェーン（Node v26 + webpack@5.24.4）では `NODE_OPTIONS=--openssl-legacy-provider` なしでは起動すら不可。
- **WebGPU**: `shader:webgpu`（compile.js）は正常終了し shaders.ts を更新。op-webgpu.js も生成済み。ただし `@webgpu/glslang@0.0.15` はブラウザ向け旧 GLSL+SPIR-V 変換パイプラインであり、現行ブラウザの WebGPU API（WGSL ネイティブ）では動作しない。詳細は P3 で対応予定。

## 既知の技術的負債（移行前時点）

1. **Node バージョン非互換**: webpack@5.24.4 は Node v17 以降の OpenSSL 変更と非互換。`NODE_OPTIONS=--openssl-legacy-provider` が必須。
2. **`python` vs `python3`**: シェルスクリプトが `python` を直接呼び出すが macOS では `python3` のみ存在。
3. **emcc 依存**: WASM バックエンドは emscripten に強く依存しており、未インストール環境では全ビルドに TypeScript エラーが波及する。
4. **yarn.lock / package-lock.json 二重管理**: リポジトリに yarn.lock が存在するが実際の install は npm で実施。lock ファイルの整合性が取れていない。
5. **`@webgpu/glslang` 廃止**: devDependency として残っているが現行 WebGPU 仕様（WGSL）では使用不可。

---

## Phase 1 移行後（2026-06-17）

ツールチェーン刷新を完了。以下の状態に到達:

- **パッケージマネージャ**: npm（`package-lock.json`）。`yarn.lock` 廃止。
- **Node**: `.nvmrc`=26 / `engines.node>=20`。
- **TypeScript**: 5.9.3。`tsconfig.json` は `module: esnext` / `moduleResolution: bundler` / `noEmit`（型チェック専用）。
- **Lint/Format**: ESLint 9 flat config（`eslint.config.js`）+ Prettier 3 単体。コードベース全体を Prettier 3 で一度正規化済み（`.prettierignore` 追加）。
- **ビルド**: webpack（9 config）→ Vite（`scripts/build.mjs`）。`dist` に 9 バンドル（`webdnn.js`/`webdnn-core.js`/`op-*.js`）+ `dist/types/*.d.ts` を生成。WebGL の 4 バリアントは 1 回ビルド→複製。
- **生成物スタブ**: `scripts/ensure-generated-stubs.mjs` が emscripten/シェーダ未導入でも `worker.ts`/`shaders.ts` のスタブを補い、typecheck/build を再現可能にする。

検証結果（全て緑）:
- `npm run typecheck` = 0
- `npm run lint` = 0
- `npm run format:check` = 0
- `npm run build:all` = 0（`makeShaderList` + Vite + dts。emscripten 不要）
- ローカルサーバ配信: `standard.html` 200 / `dist/webdnn.js` 200

P1 で確定した積み残し（後続フェーズへ）:
- `shader:wasm`（emscripten）と `shader:webgpu`（現状 GLSL→SPIR-V）は `build:all` から除外。前者は **P4**（emscripten 導入）、後者は **P3**（WGSL 化）で再統合する。
- WebGPU バックエンドの旧 API 4 箇所は `@ts-expect-error` + `TODO(P3)` で切り分け済み。**P3** で除去。
- `python3` をハードコード（`makeShaderList`/`shader:wasm`）。**P5** の uv 移行で `uv run` ベースへ。
- `@webgpu/glslang` は依存に残存。**P3** で除去。
- クリーンインストール CI では esbuild の postinstall 承認が必要（**P2** で考慮）。

---

## Phase 3 移行後（2026-06-17）

WebGPU バックエンドを現行規格（WGSL + 現行 API）へ全面移行し、**実 GPU で動作を実証**した。

- 12 個の GLSL シェーダ → **WGSL** へ書き換え（`src/shader/webgpu/shadersources/standard/*.wgsl`）。
- `compile.js` を WGSL 文字列埋め込み生成器に刷新（`webgpuShaders: Record<string,string>`）。
- `webgpuContextImpl.ts` の旧 API を現行化（`computeStage`→`compute`、`dispatch`→`dispatchWorkgroups`、
  `endPass`→`end`、シェーダ Uint32Array→WGSL string）。P1 の `@ts-expect-error` 4 箇所を除去。
- `@webgpu/glslang` を依存から除去。`shader:webgpu` を `build:all` に復帰。
- 検証フィクスチャに gemm/conv を追加。
- **発見した重要バグ**: WGSL では `meta` が予約語のため全シェーダがコンパイル失敗していた
  → 変数名を `metaBuf` に統一して解消。
- 検証: 開発機（Apple Silicon / Chromium / Metal）で WebGPU E2E が PASS。relu/add/gemm/conv が
  WebGPU 実行で onnxruntime と数値一致。CPU 経路も回帰なし。

積み残し（後続）:
- WebGL バックエンドの現行化は **P4**。WebGPU の他ブラウザ（Safari/Firefox）実機確認は人手。
- `shader:wasm`（emscripten）は引き続き `build:all` 除外（**P4**）。

---

## Phase 4 移行後（2026-06-17）

依存更新と残りバックエンドの検証を実施。

- **onnx-proto → protobufjs**: メンテ終了の `onnx-proto` を除去し、公式 `onnx.proto`(v1.17.0) から
  protobufjs で生成・ベンダリングした `src/descriptor_runner/onnx/onnx.{js,d.ts}` へ置換（37 import 貼替）。
  API 互換（`ModelProto.decode`/`TensorProto.DataType`/`IAttributeProto` 等）でコード変更は import のみ。
  再生成は `npm run gen:onnx`。`protobufjs` は直接依存に昇格。
- **WebGL**: コンテキスト実装は現行（webgl2 優先＋webgl1 フォールバック、float ext）。E2E 追加で
  現行 Chromium 上の動作を実証（`test/e2e/webgl.spec.ts` PASS）。コード変更なし（YAGNI）。
- **WASM/emscripten**: 導入手順を [emscripten-setup.md](../emscripten-setup.md) に整備、`compile.py` に
  要件コメント追記。emcc は本環境に未導入のため **実 WASM ビルドは人手 TODO**（`worker.ts` はスタブ、
  `shader:wasm` は `build:all` 除外のまま）。

検証（全て緑）: `typecheck`/`lint`/`format:check`/`build:all`/`test:unit` =0、E2E は **CPU + WebGPU + WebGL の 3 経路 PASS**。

人手 TODO: emscripten 導入 → `shader:wasm` 実行 → `worker.ts` 正規生成 → `build:all` に復帰 → WASM 検証。
他ブラウザ（Safari/Firefox）実機での WebGPU/WebGL 確認。

---

## Phase 5 移行後（2026-06-18）

最終フェーズ。ドキュメントと配布構成を刷新後の状態へ整合（自動実装可能な刷新は P0–P5 で完了）。

- **ドキュメント**: `README.md` / `README.ja.md` を全面書き換え（yarn・node 14・python 3.6・
  emscripten 2.0・「WebGPU は Chrome Canary」「WSL」「iOS13」等の旧記述を一掃）。npm / Vite / uv /
  WGSL ツールチェーンと現行ブラウザ（WebGPU=WGSL on modern Chrome/Edge/Safari/Firefox、WebGL2+fallback、
  WASM=emscripten 必要）に更新。`make_models.py`(torch) 言及を `npm run fixtures` に置換。
  `CONTRIBUTING.md` を現行開発フロー（npm install / 各ゲート / build:all / E2E + fixtures +
  playwright install / shader:webgpu / gen:onnx / emscripten）に更新。`docs/architecture.md` を新規作成
  （descriptor_runner core/backend/operators/onnx/interface・shader 生成・Vite ビルド・graph_transpiler・
  3 層テスト・ensure-generated-stubs の層別概要）。
- **Python uv 移行**: `setup.py` を削除し、root `pyproject.toml`（PEP 621 / setuptools / package
  discovery `src/graph_transpiler` / `dependencies=["numpy"]` / requires-python>=3.10 / version 2.0.0 /
  package-data `*.js`）へ移行。`uv sync` で `.venv` + `uv.lock` 生成、`import webdnn` OK。`.venv/` を
  gitignore に追加、`uv.lock` をコミット。
- **npm 配布構成整合**: `main` を実出力 `dist/webdnn.js` へ修正（旧 `dist/index.js` は不在）、
  `types: dist/types/index.d.ts` と `exports` マップ（`.`→{types,default}、`./webdnn-core`、`./dist/*`）を追加。
  `prepublishOnly` を `build:all` に変更（フレッシュクローンで makeShaderList(opEntries)+shader:webgpu(WGSL)
  を含めてビルドできるよう解消）。`files: ["dist"]` 維持。`npm pack --dry-run` は dist のみ 155 files
  （src/test 非包含）。

検証（全て緑、クリーン状態から再現確認）: `typecheck`/`lint`/`format:check`/`test:unit`(20 passed)/
`build:all` =0、E2E は **CPU + WebGPU + WebGL の 3 経路 PASS**、`npm pack` は dist のみ、`uv sync`+import OK。

人手 TODO（P0–P5 完了後に残るもの）: emscripten 導入と WASM 実ビルド/検証、Safari/Firefox 実機での
WebGPU/WebGL 確認、`npm publish` / PyPI 公開。`modernization` ブランチは未だ `master` 未マージ
（取り込み判断は人手）。

---

## WASM バックエンド有効化・検証（2026-06-18）

ユーザーが emscripten（emsdk, emcc 6.0.0）をシステムグローバル導入。残課題と対応:

- **非対話シェルで emcc が見えない問題**（emsdk は `source emsdk_env.sh` が前提）→
  `scripts/build-wasm.sh` を新設。ビルド時に `${EMSDK:-$HOME/emsdk}/emsdk_env.sh` を内部 source し、
  `npm run shader:wasm`（= `bash scripts/build-wasm.sh`）が手動 source なしで通る。CI/他環境にも移植可能。
- **emcc 6.x 互換**: `Module.HEAPU8` が既定で公開されず worker の `pre.js` が失敗 →
  `compile.py` の emcc 呼び出しに `-s EXPORTED_RUNTIME_METHODS=HEAPU8` を追加。
- 実 `worker.ts`（emcc 出力、約 67KB）生成 → `op-wasm.js` に埋め込み →
  `test/e2e/wasm.spec.ts` で **WASM E2E PASS**（relu/add/sigmoid/gemm は wasm、conv は cpu フォールバック）。
  spec は実 worker が在る時のみ実行（スタブ時は skip し偽 PASS を回避）。
- `build:all` は emscripten 非依存のまま（WASM はオプトイン、未導入環境はスタブで graceful degradation）。
- eslint は wasm worker 出力ディレクトリ全体（`workerRaw.js` 等の emcc 出力含む）を ignore。

**結果: 4 バックエンド（CPU / WebGPU / WebGL / WASM）すべてが実ブラウザ E2E PASS。**
残る人手 TODO: Safari/Firefox 実機確認、publish。
