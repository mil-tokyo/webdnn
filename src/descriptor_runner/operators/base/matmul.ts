import { OperatorImpl } from "../operatorImpl";
import { calcStrides } from "../operatorUtil";

// version 13
export abstract class MatMul extends OperatorImpl {
  protected calcShape(
    dimsA: ReadonlyArray<number>,
    dimsB: ReadonlyArray<number>
  ) {
    /*
    matmulの出力shape、入力stride計算
    matmul((a,b,m,k), (a,b,k,n)) => (a,b,m,n)

    a, bの部分は2個に限らず0~無限個の次元がつけられる。
    2行列で各次元のサイズは一致が必要。
    broadcastingあり。次元数が少ない側には先頭にサイズ1の次元が付与。
    そのうえでサイズ1とそれ以外のサイズがある場合にそれ以外のサイズに合わせbroadcast

    一方の入力が１次元の場合の特例。
    (k), (a,b,k,n) => (a,b,n)
    (k)を(a,b,1,k)にbroadcastしたうえで計算して、(a,b,1,n)を得て、1の軸を消して(a,b,n)

    (a,b,m,k), (k) => (a,b,m)
    (k)を(a,b,k,1)にbroadcastしたうえで計算して、(a,b,m,1)を得て、１の軸を消して(a,b,m)

    両方１次元だと、単純な内積で(1,1)を得て１の軸２つが消え、０次元のスカラー値。
    */

    // 出力の次元数（1次元の場合の特例適用前）
    const totalNDims = Math.max(dimsA.length, dimsB.length, 2);

    const expandedDimsA = dimsA.slice();
    if (expandedDimsA.length === 0) {
      throw new Error();
    } else if (expandedDimsA.length === 1) {
      expandedDimsA.unshift(1);
    }
    while (expandedDimsA.length < totalNDims) {
      expandedDimsA.unshift(1);
    }
    const expandedDimsB = dimsB.slice();
    if (expandedDimsB.length === 0) {
      throw new Error();
    } else if (expandedDimsB.length === 1) {
      expandedDimsB.push(1);
    }
    while (expandedDimsB.length < totalNDims) {
      expandedDimsB.unshift(1);
    }

    const resultDims = [
      expandedDimsA[expandedDimsA.length - 2],
      expandedDimsB[expandedDimsB.length - 1],
    ];
    const innerProductLength = expandedDimsA[expandedDimsA.length - 1];
    if (innerProductLength !== expandedDimsB[expandedDimsB.length - 2]) {
      throw new Error();
    }
    const stridesA = calcStrides(expandedDimsA);
    const stridesB = calcStrides(expandedDimsB);
    for (let i = expandedDimsA.length - 3; i >= 0; i--) {
      const resultDim = Math.max(expandedDimsA[i], expandedDimsB[i]);
      // broadcastされた次元はstrideは0 (出力サイズ1の次元でも0にしてOK)
      if (expandedDimsA[i] === 1) {
        stridesA[i] = 0;
      }
      if (expandedDimsB[i] === 1) {
        stridesB[i] = 0;
      }
      resultDims.unshift(resultDim);
    }

    const resultStrides = calcStrides(resultDims);
    const resultLength = resultStrides[0] * resultDims[0];
    const resultDimsAfterSqueeze = resultDims.slice();
    if (dimsA.length === 1) {
      resultDimsAfterSqueeze.splice(resultDimsAfterSqueeze.length - 2, 1);
    }
    if (dimsB.length === 1) {
      resultDimsAfterSqueeze.splice(resultDimsAfterSqueeze.length - 1, 1);
    }

    return {
      resultLength,
      resultDims,
      resultStrides,
      resultDimsAfterSqueeze,
      stridesA,
      stridesB,
      innerProductLength,
    };
  }
}
