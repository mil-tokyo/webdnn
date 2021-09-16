// auto-generated by scripts/make_operator_entries.py
import { OperatorEntry } from "../../interface/core/operator";

import { getOpEntries as getOpEntriesoperatorsstandardbinary7 } from "./operators/standard/binary7";
import { getOpEntries as getOpEntriesoperatorsstandarddynamicunary } from "./operators/standard/dynamicunary";
import { getOpEntries as getOpEntriesoperatorsstandardgemm } from "./operators/standard/gemm";
import { getOpEntries as getOpEntriesoperatorsstandardunary } from "./operators/standard/unary";

export function getOpEntries(): OperatorEntry[] {
  const entries: OperatorEntry[] = [];
  entries.push(...getOpEntriesoperatorsstandardbinary7());
  entries.push(...getOpEntriesoperatorsstandarddynamicunary());
  entries.push(...getOpEntriesoperatorsstandardgemm());
  entries.push(...getOpEntriesoperatorsstandardunary());
  return entries;
}
