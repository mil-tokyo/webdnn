import argparse
import os
import numpy as np
import torch
from model import TransformerNet
from webdnn.tensor_export import serialize_tensors


def export(weights, out_dir, size=256, base=32, num_res=5, end_k=9):
    os.makedirs(out_dir, exist_ok=True)
    model = TransformerNet(base=base, num_res=num_res, end_k=end_k).eval()
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
    import onnxruntime as ort
    # torch の legacy exporter は ReflectionPad の動的padding機構として Identity/Cast/Concat/
    # Slice/ConstantOfShape 等を大量に出す（WebDNN は Identity 等を未実装で読込失敗する）。
    # ORT BASIC で定数畳み込みし、WebDNN対応op だけに圧縮する。
    tmp = onnx_path + ".opt"
    so = ort.SessionOptions()
    so.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_BASIC
    so.optimized_model_filepath = tmp
    ort.InferenceSession(onnx_path, so, providers=["CPUExecutionProvider"])
    os.replace(tmp, onnx_path)
    # ブラウザ4バックエンド突合用の期待値（resnet例と同じ仕組み）
    serialize_tensors(os.path.join(out_dir, "expected.bin"),
                      {"input": dummy.numpy(), "output": ref})
    # 自動検証1: 最適化後 ONNX と torch の一致
    sess = ort.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])
    ort_out = sess.run(None, {"input": dummy.numpy()})[0]
    diff = float(np.abs(ort_out - ref).max())
    print(f"max|torch-onnxruntime(optimized)| = {diff:.4e}")
    assert diff < 1e-3, f"ONNX export mismatch: {diff}"
    # 自動検証2: WebDNN非対応op が残っていないか（将来モデル変更時の番兵）
    import onnx
    allowed = {"Conv", "ConvTranspose", "InstanceNormalization", "Relu", "Add", "Pad"}
    used = sorted({n.op_type for n in onnx.load(onnx_path).graph.node})
    extra = set(used) - allowed
    assert not extra, f"WebDNN未対応の可能性があるop が残存: {extra}"
    print(f"OK: {onnx_path}  ops={used}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--weights", default="")
    p.add_argument("--out", required=True)
    p.add_argument("--size", type=int, default=256)
    p.add_argument("--base", type=int, default=32)
    p.add_argument("--num-res", type=int, default=5)
    p.add_argument("--end-k", type=int, default=9)
    a = p.parse_args()
    export(a.weights, a.out, a.size, a.base, a.num_res, a.end_k)
