# Strategy

GraphDescriptorGeneratorWebGPUの生成ストラテジーについて

## 1. Parameter割り当て

全ノードのParameterをメモリに割り付けて、アドレスを計算しておく

```cpp
Allocator allocator;

MemoryLayout parameter_allocation;
ByteData parameters_buffer;
 
[parameter_allocation, paramters_buffer] = allocator.allocate_parameters(Graph);
```

## 2. Variable割り当て

全Variableをメモリに割り付けて、アドレスを計算しておく。

- inplace化によるVariableの削除はFrontendで行う
- メモリ隣接によるMinor-dimension concatの省略はこの段階で行う

```cpp
Allocator allocator;

MemoryLayout variable_allocation = allocator.allocate_variables(Graph)
```

## 3. Operator生成

Layerを全てOperatorに変換する。WebGPU独自の表現。

## 4. KernelSource生成

OperatorのAttributeMixin実装状況を確認しつつカーネルソースコードを構築
