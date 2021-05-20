// auto-generated by scripts/make_operator_entries.py
import { OperatorEntry } from "../../interface/core/operator";

import { getOpEntries as getOpEntriesoperatorsstandardaveragepool } from './operators/standard/averagepool';
import { getOpEntries as getOpEntriesoperatorsstandardbinary7 } from './operators/standard/binary7';
import { getOpEntries as getOpEntriesoperatorsstandardcast } from './operators/standard/cast';
import { getOpEntries as getOpEntriesoperatorsstandardconcat } from './operators/standard/concat';
import { getOpEntries as getOpEntriesoperatorsstandardconstant } from './operators/standard/constant';
import { getOpEntries as getOpEntriesoperatorsstandardconv } from './operators/standard/conv';
import { getOpEntries as getOpEntriesoperatorsstandardflatten } from './operators/standard/flatten';
import { getOpEntries as getOpEntriesoperatorsstandardgather } from './operators/standard/gather';
import { getOpEntries as getOpEntriesoperatorsstandardgemm } from './operators/standard/gemm';
import { getOpEntries as getOpEntriesoperatorsstandardglobalaveragepool } from './operators/standard/globalaveragepool';
import { getOpEntries as getOpEntriesoperatorsstandardmatmul } from './operators/standard/matmul';
import { getOpEntries as getOpEntriesoperatorsstandardmaxpool } from './operators/standard/maxpool';
import { getOpEntries as getOpEntriesoperatorsstandardreducemean } from './operators/standard/reducemean';
import { getOpEntries as getOpEntriesoperatorsstandardreshape5 } from './operators/standard/reshape5';
import { getOpEntries as getOpEntriesoperatorsstandardshape } from './operators/standard/shape';
import { getOpEntries as getOpEntriesoperatorsstandardslice } from './operators/standard/slice';
import { getOpEntries as getOpEntriesoperatorsstandardsoftmax } from './operators/standard/softmax';
import { getOpEntries as getOpEntriesoperatorsstandardsplit } from './operators/standard/split';
import { getOpEntries as getOpEntriesoperatorsstandardtranspose } from './operators/standard/transpose';
import { getOpEntries as getOpEntriesoperatorsstandardunary } from './operators/standard/unary';
import { getOpEntries as getOpEntriesoperatorsstandardunsqueeze } from './operators/standard/unsqueeze';

export function getOpEntries(): OperatorEntry[] {
  const entries: OperatorEntry[] = [];
  entries.push(...getOpEntriesoperatorsstandardaveragepool());
  entries.push(...getOpEntriesoperatorsstandardbinary7());
  entries.push(...getOpEntriesoperatorsstandardcast());
  entries.push(...getOpEntriesoperatorsstandardconcat());
  entries.push(...getOpEntriesoperatorsstandardconstant());
  entries.push(...getOpEntriesoperatorsstandardconv());
  entries.push(...getOpEntriesoperatorsstandardflatten());
  entries.push(...getOpEntriesoperatorsstandardgather());
  entries.push(...getOpEntriesoperatorsstandardgemm());
  entries.push(...getOpEntriesoperatorsstandardglobalaveragepool());
  entries.push(...getOpEntriesoperatorsstandardmatmul());
  entries.push(...getOpEntriesoperatorsstandardmaxpool());
  entries.push(...getOpEntriesoperatorsstandardreducemean());
  entries.push(...getOpEntriesoperatorsstandardreshape5());
  entries.push(...getOpEntriesoperatorsstandardshape());
  entries.push(...getOpEntriesoperatorsstandardslice());
  entries.push(...getOpEntriesoperatorsstandardsoftmax());
  entries.push(...getOpEntriesoperatorsstandardsplit());
  entries.push(...getOpEntriesoperatorsstandardtranspose());
  entries.push(...getOpEntriesoperatorsstandardunary());
  entries.push(...getOpEntriesoperatorsstandardunsqueeze());
  return entries;
}