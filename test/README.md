# Test

### GraphBuilder

- テストフレームワークとして[nose](http://nose.readthedocs.io/en/latest/)を使用
    `pip install nose` でインストールされる `nosetests` コマンドでテストを実行可能。

    ```
    nosetests
    ```

- テスト追加の際はフォルダ・ファイル名の末尾に `_test` をつけること

- カバレッジも取れる

    ```
    nosetests --with-coverage --cover-tests graph_builder
    ```
    
    ただしカバレッジはそもそもimportしていないファイルについて計算されないので注意

- カーネルコード生成のテストは、ウェブブラウザで行う。

    - 予め、テスト用のカーネルコードを生成する必要がある
    
        ```
        nosetests nosetests -w ./test/kernels
        ```

    - `kernel_test.html` を開いて[RUN]を押すと生成されたカーネルコードがテストされる。


### DescriptorRunner

- 未定
