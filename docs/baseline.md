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
