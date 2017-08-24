How to Contribute
=================

We welcome contributions to WebDNN. This document describes the procedures and rules.

Kinds of contributions will be one of the following, but not restricted to:

- New bug reporting
- New feature proposal
- Bug fix
- Implementation of a layer
- Implementation of a converter from a deep learning framework
- Improvement of performance
- Documantation

For new layer implementation, at least **WebAssembly** backend implementation is required.
**WebGPU** backend can only be tested on Mac, so it is not mandatory.

Open New Issue
--------------

Feel free to create open new issue, for example:

- New bug report
- Ask question
- Feature proposal/request

If you found a bug, please report with execution environment information such as python interpreter version, DNN framework version,
browser version, OS version, GPU version, and so on.

Send Pull Request
-----------------

Please send pull request from your fork branch to our :code:`master` branch. The project organizer checks the request and accepts or gives
request for revision.

Testing
-------

If you have added some features, implementing tests corresponding to them is recommended. WebDNN uses
`nose <http://nose.readthedocs.io/en/latest/>`_ test framework. All tests of WebDNN is in :code:`/test`.
There are many examples. Please check them.


Compile-Time Test
^^^^^^^^^^^^^^^^^

:code:`/test/webdnn_test` directory contains compile-time graph transpiler tests. All tests is done only in python code.

You can run compile-time test like follows:

.. code-block:: shell

    $ nosetests

:code:`nosetests` command traverse directories whose name contains `"test"` recursively, therefore you simply hit above command.
If you want to create new tests, please create directory and files based on this suffix rule.

Runtime Test
^^^^^^^^^^^^

:code:`/test/runtime` directory contains runtime graph transpiler test. Test code is compiled by transpiler and run on web browsers.

To run runtime test, you need to generate test codes first. All test codes are generated under :code:`/build/test` directory.

.. code-block:: shell

    # generate test codes
    $ nosetests test/runtime

Then, access :code:`/test/test_kernel.html` and click **RUN** button. Result are output in debug console.

Generating all test codes requires more than 10 minutes. Instead of that, you can specify target test files like follows:

.. code-block:: shell

    # generate test code only for AveragePooling2D
    $ nosetests test/runtime/operators_test/average_pooling_2d_test.py

Also you can specify target backends. For example, follow command generates test code of only webgpu backend.

.. code-block:: shell

    # generate test code only for WebGPU backend
    $ TEST_WEBGPU=1 TEST_WEBASSEMBLY=0, TEST_WEBGL=0, TEST_FALLBACK=0 nosetests test/runtime

License
-------

WebDNN is distributed under the MIT License. Every contributor holds the copyright of his/her part.

By contributing to the mil-tokyo/webdnn repository through pull-request, comment, or otherwise, the contributor releases their content to
the license and copyright terms herein.

.. code-block:: text

    Developer Certificate of Origin 1.1

    Developer Certificate of Origin
    Version 1.1

    Copyright (C) 2004, 2006 The Linux Foundation and its contributors.
    1 Letterman Drive
    Suite D4700
    San Francisco, CA, 94129

    Everyone is permitted to copy and distribute verbatim copies of this
    license document, but changing it is not allowed.


    Developer's Certificate of Origin 1.1

    By making a contribution to this project, I certify that:

    (a) The contribution was created in whole or in part by me and I
        have the right to submit it under the open source license
        indicated in the file; or

    (b) The contribution is based upon previous work that, to the best
        of my knowledge, is covered under an appropriate open source
        license and I have the right under that license to submit that
        work with modifications, whether created in whole or in part
        by me, under the same open source license (unless I am
        permitted to submit under a different license), as indicated
        in the file; or

    (c) The contribution was provided directly to me by some other
        person who certified (a), (b) or (c) and I have not modified
        it.

    (d) I understand and agree that this project and the contribution
        are public and that a record of the contribution (including all
        personal information I submit with it, including my sign-off) is
        maintained indefinitely and may be redistributed consistent with
        this project or the open source license(s) involved.
