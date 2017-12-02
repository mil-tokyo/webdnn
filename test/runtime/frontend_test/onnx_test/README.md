# onnx_test

Unittests for ONNXConverter

Because ONNX is not DNN execution framework but DNN model declaration format, it cannot to compute expected result by ONNX itself.
Therefore, we compute the result by numpy and use ONNX just for model definition.

