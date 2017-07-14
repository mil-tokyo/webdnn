# Test

### GraphBuilder

- Test framework is [nose](http://nose.readthedocs.io/en/latest/)
    `nosetests` installed by `pip install nose` runs the test。

    ```
    nosetests
    ```

- The suffix `_test` must be attached to the file / folder name when adding a test

- Taking coverage

    ```
    nosetests --with-coverage --cover-tests graph_transpiler
    ```
    
    Coverage is not calculated for files which are not imported.

- Kernel code generation test is done via a web browser.

    - Kernel code have to be generated in advance.
    
        ```
        nosetests -w ./test/runtime
        ```

    - Opening `kernel_test.html` and press [RUN] to test the generated kernel code.

    - Generating all code requires about 30 minutes. To check only specific layers, you can specify python files to check.

        ```
        nosetests ./test/runtime/frontend_test/keras_test/layers_test/core_test/activation_test.py
        ```


### DescriptorRunner

- Not implemented
