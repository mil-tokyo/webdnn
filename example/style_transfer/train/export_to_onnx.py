import argparse
import os
import numpy as np
import torch
from model import TransformerNet
from webdnn.tensor_export import serialize_tensors


def export(weights, out_dir, size=256):
    os.makedirs(out_dir, exist_ok=True)
    model = TransformerNet().eval()
    if weights and os.path.exists(weights):
        model.load_state_dict(torch.load(weights, map_location="cpu"))
    dummy = torch.rand(1, 3, size, size) * 255.0  # 入力は[0,255]スケール
    with torch.no_grad():
        ref = model(dummy).numpy()
    onnx_path = os.path.join(out_dir, "model.onnx")
    with torch.no_grad():
        torch.onnx.export(
            model, (dummy,), onnx_path, input_names=["input"],
            output_names=["output"], opset_version=11,  # Pad は WebDNN pad11(opsetMin=11)。10だとPad未解決で読込失敗
            dynamo=False,  # torch 2.12+ defaults to dynamo=True (requires onnxscript); legacy exporter supports opset 11
        )
    # ブラウザ4バックエンド突合用の期待値（resnet例と同じ仕組み）
    serialize_tensors(os.path.join(out_dir, "expected.bin"),
                      {"input": dummy.numpy(), "output": ref})
    # 自動検証: onnxruntime と torch の一致
    import onnxruntime as ort
    sess = ort.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])
    ort_out = sess.run(None, {"input": dummy.numpy()})[0]
    diff = float(np.abs(ort_out - ref).max())
    print(f"max|torch-onnxruntime| = {diff:.4e}")
    assert diff < 1e-3, f"ONNX export mismatch: {diff}"
    print(f"OK: {onnx_path}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--weights", default="")
    p.add_argument("--out", required=True)
    p.add_argument("--size", type=int, default=256)
    a = p.parse_args()
    export(a.weights, a.out, a.size)
