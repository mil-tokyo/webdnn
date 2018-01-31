#!/usr/bin/env bash

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

${npm_bin_dir}/typedoc \
    --disableOutputCheck \
    --ignoreCompilerErrors \
    --out ${script_dir}/../docs/build/html/api_reference/descriptor-runner \
    --mode modules \
    --target es2017 \
    --lib 'lib.es2017.d.ts,lib.dom.d.ts' \
    --excludePrivate \
    --readme ${script_dir}/../src/descriptor_runner/index.md \
    --theme ${script_dir}/../docs/template/typedoc \
    ${script_dir}/../src/descriptor_runner/webdnn.ts
