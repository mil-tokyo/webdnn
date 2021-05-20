import { onnx } from "onnx-proto";
import { DataArrayTypes } from "../../interface/core/constants";

export function decodeTensorRaw(
  buf: ArrayBuffer,
  bodyByteOffset: number,
  bodyCompressedLength: number,
  dataType: number,
  numel: number
): DataArrayTypes {
  let data: DataArrayTypes;
  switch (dataType) {
    case onnx.TensorProto.DataType.FLOAT:
      data = new Float32Array(numel);
      break;
    case onnx.TensorProto.DataType.INT32:
      data = new Int32Array(numel);
      break;
    default:
      throw new Error("Unsupported DataType");
  }
  // Buf may not be aligned
  const dataUint8View = new Uint8Array(data.buffer),
    srcUint8View = new Uint8Array(buf, bodyByteOffset, data.byteLength);
  dataUint8View.set(srcUint8View);
  return data;
}
