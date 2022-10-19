import { onnx } from "onnx-proto";
import { CPUTensor } from "..";
import { WebDNNCPUContext } from "../interface/backend/cpu/cpuContext";
import { DataArrayTypes, DataType } from "../interface/core/constants";
import { TensorLoader } from "../interface/core/tensorLoader";
import { arrayProd, arraySum } from "../util";
import { decodeTensorEightbit } from "./tensorDecoder/decodeTensorEightbit";
import { decodeTensorRaw } from "./tensorDecoder/decodeTensorRaw";

const signatureFile = 843990103, // "WDN2"
  signatureTensor = 1397638484, // "TENS"
  signautreClose = 1397705795; // "CLOS"

export class TensorLoaderImpl implements TensorLoader {
  paths: string[];

  constructor(path: string[] | string, public cpuContext: WebDNNCPUContext) {
    if (typeof path === "string") {
      this.paths = [path];
    } else {
      this.paths = path;
    }
  }

  async loadAll(
    progressCallback?: (loadedBytes: number) => unknown
  ): Promise<Map<string, CPUTensor>> {
    const fileArray = await this.fetchAllFile(progressCallback),
      view = new DataView(
        fileArray.buffer,
        fileArray.byteOffset,
        fileArray.byteLength
      );
    if (signatureFile !== view.getUint32(0, true)) {
      throw new Error("Unexpected file signature");
    }
    let offset = 4;
    const tensors = new Map<string, CPUTensor>();
    let close = false;
    while (!close) {
      const chunkInfo = this.extractChunk(fileArray.buffer, offset);
      switch (chunkInfo.signature) {
        case signatureTensor:
          {
            const { name, tensor } = this.parseTensorChunk(
              fileArray.buffer,
              chunkInfo.bodyByteOffset,
              chunkInfo.bodyByteLength
            );
            tensors.set(name, tensor);
          }
          break;
        case signautreClose:
          close = true;
          break;
      }
      offset = chunkInfo.nextByteOffset;
    }
    return tensors;
  }

  private async fetchAllFile(
    progressCallback?: (loadedBytes: number) => unknown
  ): Promise<Uint8Array> {
    const abs: ArrayBuffer[] = [];
    let loadedBytes = 0;
    progressCallback?.(loadedBytes);
    for (const path of this.paths) {
      const f = await fetch(path),
        ab = await f.arrayBuffer();
      abs.push(ab);
      loadedBytes += ab.byteLength;
      progressCallback?.(loadedBytes);
    }
    const totalLength = arraySum(abs.map((ab) => ab.byteLength)),
      concatArray = new Uint8Array(totalLength);
    let ofs = 0;
    for (const ab of abs) {
      const src = new Uint8Array(ab);
      concatArray.set(src, ofs);
      ofs += src.byteLength;
    }

    return concatArray;
  }

  private extractChunk(
    buf: ArrayBuffer,
    byteOffset: number
  ): {
    signature: number;
    nextByteOffset: number;
    bodyByteOffset: number;
    bodyByteLength: number;
  } {
    const view = new DataView(buf, byteOffset);
    if (view.byteLength < 8) {
      throw new Error("Unexpected EOF");
    }
    const signature = view.getUint32(0, true),
      bodyByteLength = view.getUint32(4, true),
      bodyByteOffset = byteOffset + 8;
    if (view.byteLength < 8 + bodyByteLength) {
      throw new Error("Unexpected EOF");
    }
    const nextByteOffset = bodyByteOffset + bodyByteLength;
    return { signature, bodyByteLength, bodyByteOffset, nextByteOffset };
  }

  private parseTensorChunk(
    buf: ArrayBuffer,
    bodyByteOffset: number,
    bodyByteLength: number
  ): { name: string; tensor: CPUTensor } {
    const view = new DataView(buf, bodyByteOffset, bodyByteLength);

    let ofs = 0;
    const compressionAlgorithm = view.getUint8(ofs);
    ofs += 1;
    const bodyCompressedLength = view.getUint32(ofs, true);
    ofs += 4;
    const dataType = view.getUint8(ofs);
    ofs += 1;
    const ndim = view.getUint8(ofs);
    ofs += 1;
    const dims: number[] = [];
    for (let i = 0; i < ndim; i++) {
      dims.push(view.getUint32(ofs, true));
      ofs += 4;
    }
    const numel = arrayProd(dims),
      nameLength = view.getUint32(ofs, true);
    ofs += 4;
    const name = this.parseString(buf, bodyByteOffset + ofs, nameLength);
    ofs += nameLength;
    const extraLength = view.getUint32(ofs, true);
    ofs += 4;
    // Skip extra data
    ofs += extraLength;

    const data = this.parseTensorBody(
      buf,
      compressionAlgorithm,
      bodyByteOffset + ofs,
      bodyCompressedLength,
      dataType,
      numel
    );
    let dataTypeString: DataType;
    switch (dataType) {
      case onnx.TensorProto.DataType.FLOAT:
        dataTypeString = "float32";
        break;
      case onnx.TensorProto.DataType.INT32:
        dataTypeString = "int32";
        break;
      default:
        throw new Error("Unsupported DataType");
    }
    const tensor = this.cpuContext.emptyTensor(dims, dataTypeString, data);
    return { name, tensor };
  }

  private parseString(
    buf: ArrayBuffer,
    byteOffset: number,
    byteLength: number
  ): string {
    const view = new Uint8Array(buf, byteOffset, byteLength);
    // TODO: support UTF-8
    return String.fromCharCode(...Array.from(view));
  }

  private parseTensorBody(
    buf: ArrayBuffer,
    compressionAlgorithm: number,
    bodyByteOffset: number,
    bodyCompressedLength: number,
    dataType: number,
    numel: number
  ): DataArrayTypes {
    switch (compressionAlgorithm) {
      case 0:
        return decodeTensorRaw(
          buf,
          bodyByteOffset,
          bodyCompressedLength,
          dataType,
          numel
        );
      case 1:
        return decodeTensorEightbit(
          buf,
          bodyByteOffset,
          bodyCompressedLength,
          dataType,
          numel
        );
      default:
        throw new Error("Unexpected compression algorithm");
    }
  }
}
