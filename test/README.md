# Test

As test framework, [nose](http://nose.readthedocs.io/en/latest/) is used in WebDNN. `nosetests` installed by `pip install nose` runs 
the test.

```shell
nosetests
```

`nosetests` traverses all directories and files with suffix `_test` recursively. As default, all test cases in `/test/webdnn_test` will 
be executed.

## Kernel test

Kernel code is test on web browsers. To run test, you need to generate all kernel codes first.

```shell
nosetests ./test/runtime
```

Then, open `/test/kernel_test.html` and press `RUN` button. Result is output at console.

Generating all code requires about 10 minutes. 

- If you want to check only specific layers, you can specify python files to check.

    ```shell
    nosetests ./test/runtime/frontend_test/keras_test/layers_test/core_test/activation_test.py
    ```
  
- To check only specific backend, you can toggle target backends like follows,

    ```shell
    TEST_WEBGPU=1 TEST_WEBASSEMBLY=0 TEST_FALLBACK=0 nosetests ./test/runtime
    ```
