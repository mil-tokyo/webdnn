import tensorflow as tf

from webdnn.frontend.tensorflow.converter import TensorFlowConverter


@TensorFlowConverter.register_handler("PyFunc")
def py_func_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("PyFuncStateless")
def py_func_stateless_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")
