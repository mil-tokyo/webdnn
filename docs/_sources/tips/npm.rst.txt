Installing JavaScript package with npm
======================================

If you are building your webpage with `broserify <http://browserify.org/>`_ 
or `webpack <https://webpack.js.org/>`_, you can install JavaScript part of WebDNN with npm (node package manager).
By using these build system, the code of WebDNN is automatically concatenated with your own code to improve page load performance.

1. Install webdnn package in your project

.. code-block:: shell

    npm install webdnn --save

It will install ``webdnn`` package in the ``node_modules`` directory.

2. Load the package from your JavaScript code

.. code-block:: javascript

    var webdnn = require('webdnn');

    var runner = await webdnn.load('graph_descriptor');//do some stuff

You can use the package by using ``require('webdnn')``.

Complete working example is here: `https://github.com/milhidaka/webdnn-exercise/tree/master/webpack <https://github.com/milhidaka/webdnn-exercise/tree/master/webpack>`_

=====
Notes
=====

* The npm package only contains code to run on web browsers. To convert your DNN model, you have to install python package separately.
* TypeScript type definition file is included (as it is implemented with TypeScript).
