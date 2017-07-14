# How to contribute
We welcome contributions to WebDNN. This document describes the procedures and rules.

Kinds of contributions will be one of the following, but not restricted to:
- Bugfix
- Implementation of a layer
- Implementation of a converter from a deep learning framework
- Improvement of performance
- Documantation

For new layer implementation, at least WebAssembly backend implementation is required. WebGPU backend can only be tested on Mac, so it is not mandatory.

# Testing
If you have added some features, implementing tests corresponding to them is recommended.

`test/webdnn_test` is for tests which can be completed within graph transpiler. `test/runtime` is for tests which generates graph descriptor and compares its behavior on web browsers.

See how to run test commands in `test/README.md`.

# Pull Request
Send pull request from your fork branch to our master branch. The project organizer checks the request and accepts or gives request for revision.

# License
WebDNN is distributed under the MIT License. Every contributor holds the copyright of his/her part.

By contributing to the mil-tokyo/webdnn repository through pull-request, comment,
or otherwise, the contributor releases their content to the license and copyright
terms herein.

## Developer Certificate of Origin 1.1
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
