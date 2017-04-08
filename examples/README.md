# examples

- sgemm_test.html

	sgemmカーネルの実装が正しいことをnaive実装と比較して検証

- sgemm_performance.html

	sgemmの実行速度(FLOPS)の測定

- convolution2d_performance.html

	convolutionの実行速度(所要時間)の測定

- jit_performance_poc1.html

	JITの効果の確認。Convolution2D+ReLUを別々のカーネルとして実行する場合と単一のカーネルとして実行する場合で所要時間の比較。

- jit_performance_poc2.html

	JITの効果の確認。BatchNormalize+ReLuを別々のカーネルとして実行する場合と単一のカーネルとして実行する場合で所要時間の比較。
