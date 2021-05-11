(function () {
  // To potentially support IE11, not using ES6 syntax (const)
  var buffers = {};
  onmessage = function (event) {
    switch (event.data.type) {
      case "alloc":
        var result = Module._webdnn_malloc(event.data.byteLength);
        if (result === 0) {
          postMessage({ type: "error", message: "Memory alloc failed" });
        } else {
          buffers[event.data.bufferId] = {
            byteLength: event.data.byteLength,
            ptr: result,
          };
        }
        break;
      case "destroy":
        var buffer = buffers[event.data.bufferId];
        if (buffer) {
          Module._webdnn_free(buffer.ptr);
          delete buffers[event.data.bufferId];
        } else {
          postMessage({
            type: "error",
            message: "Destroying non-existing buffer",
          });
        }
        break;
      case "write":
        var buffer = buffers[event.data.bufferId];
        if (buffer) {
          var dataBufView = new Uint8Array(
            Module.HEAPU8.buffer,
            buffer.ptr,
            buffer.byteLength
          );
          dataBufView.set(event.data.data);
        } else {
          postMessage({
            type: "error",
            message: "Writing non-existing buffer",
          });
        }
        break;
      case "read":
        var buffer = buffers[event.data.bufferId];
        if (buffer) {
          var dataBufView = new Uint8Array(
            Module.HEAPU8.buffer,
            buffer.ptr,
            buffer.byteLength
          );
          var result = new Uint8Array(buffer.byteLength);
          result.set(dataBufView);
          postMessage({ type: "read", data: result });
        } else {
          postMessage({
            type: "error",
            message: "Reading non-existing buffer",
          });
        }
        break;
      case "runKernel":
        var kernelFunction = Module["_" + event.data.name];
        if (kernelFunction) {
          var args = [];
          var ok = true;
          for (var i = 0; i < event.data.args.length; i++) {
            var arg = event.data.args[i];
            if (arg.type === "tensor") {
              var buffer = buffers[arg.bufferId];
              if (!buffer) {
                ok = false;
                postMessage({
                  type: "error",
                  message: "Tensor argument of kernel call does not exist",
                });
              }
              args.push(buffer.ptr);
            } else {
              args.push(arg.value);
            }
          }
          if (ok) {
            kernelFunction.apply(null, args);
          }
        } else {
          postMessage({ type: "error", message: "Kernel not found" });
        }
        break;
    }
  };

  Module.onRuntimeInitialized = function () {
    postMessage({ type: "initializeComplete" });
  };

  var bstr = atob("WASM_WORKER_WASM_BINARY_BASE64");
  var ary = new Uint8Array(bstr.length);
  for (var i = 0; i < bstr.length; i++) {
    ary[i] = bstr.charCodeAt(i);
  }
  Module.wasmBinary = ary;
})();
