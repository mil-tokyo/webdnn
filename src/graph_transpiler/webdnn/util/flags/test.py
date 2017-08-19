import os

TEST_WEBGPU = os.environ.get("TEST_WEBGPU", "1") == "1"
TEST_WEBGL = os.environ.get("TEST_WEBGL", "1") == "1"
TEST_WEBASSEMBLY = os.environ.get("TEST_WEBASSEMBLY", "1") == "1"
TEST_FALLBACK = os.environ.get("TEST_FALLBACK", "1") == "1"
