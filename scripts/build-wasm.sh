#!/usr/bin/env bash
# Build the WASM worker via emscripten.
#
# emsdk only adds `emcc` to PATH after `source emsdk_env.sh`, which a
# non-interactive shell (CI, `npm run`, tool-driven shells) does NOT do.
# So we source it here. The emsdk location is taken from $EMSDK, defaulting
# to ~/emsdk. See docs/emscripten-setup.md.
set -euo pipefail

EMSDK_DIR="${EMSDK:-$HOME/emsdk}"

if ! command -v emcc >/dev/null 2>&1; then
  if [ -f "$EMSDK_DIR/emsdk_env.sh" ]; then
    # shellcheck disable=SC1090,SC1091
    source "$EMSDK_DIR/emsdk_env.sh" >/dev/null 2>&1 || true
  fi
fi

if ! command -v emcc >/dev/null 2>&1; then
  echo "error: emcc not found." >&2
  echo "Install emscripten and set EMSDK to your emsdk directory (default: ~/emsdk)." >&2
  echo "See docs/emscripten-setup.md" >&2
  exit 1
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec python3 "$REPO_ROOT/src/shader/wasm/compile.py"
