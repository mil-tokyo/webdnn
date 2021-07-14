import Long from "long";
import { onnx } from "onnx-proto";
import { DataArrayTypes } from "../../interface/core/constants";
import { clipLong } from "../../util";

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
    case onnx.TensorProto.DataType.INT64: {
      data = new Int32Array(numel);
      const view = new DataView(buf, bodyByteOffset, numel * 8);
      for (let idx = 0; idx < numel; idx++) {
        data[idx] = clipLong(
          new Long(
            view.getUint32(idx * 8, true),
            view.getUint32(idx * 8 + 4, true)
          )
        );
      }
      return data;
    }
    default:
      throw new Error("Unsupported DataType");
  }
  // Buf may not be aligned
  const dataUint8View = new Uint8Array(data.buffer),
    srcUint8View = new Uint8Array(buf, bodyByteOffset, data.byteLength);
  dataUint8View.set(srcUint8View);
  return data;
}
