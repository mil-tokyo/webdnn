#!/usr/bin/env bash

# Build "./dist/webdnn.js", "./dist/webdnn.es5.js", and "./dist/webdnn.d.ts".

abs_dirname() {
  local cwd="$(pwd)"
  local path="$1"

  while [ -n "$path" ]; do
    cd "${path%/*}"
    local name="${path##*/}"
    path="$(readlink "$name" || true)"
  done

  pwd -P
  cd "$cwd"
}

script_dir="$(dirname "$0")"
npm_bin_dir=$(npm bin)


# latest ES
${npm_bin_dir}/tsc -p ${script_dir}/../src/descriptor_runner/tsconfig.json
${npm_bin_dir}/webpack --config ${script_dir}/../src/descriptor_runner/webpack.config.js

# ES5
${npm_bin_dir}/tsc -p ${script_dir}/../src/descriptor_runner/tsconfig.es5.json
${npm_bin_dir}/webpack --config ${script_dir}/../src/descriptor_runner/webpack.config.es5.js

# type declaration file
${npm_bin_dir}/dts-generator \
    --prefix webdnn --name webdnn --main webdnn/webdnn \
    --project ${script_dir}/../src/descriptor_runner \
    --out ${script_dir}/../dist/webdnn.d.ts
