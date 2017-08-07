import tensorflow as tf

from webdnn.frontend.tensorflow.converter import TensorFlowConverter


@TensorFlowConverter.register_handler("DenseToDenseSetOperation")
def dense_to_dense_set_operation_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("DenseToSparseSetOperation")
def dense_to_sparse_set_operation_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("SetSize")
def set_size_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("SparseToSparseSetOperation")
def sparse_to_sparse_set_operation_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")
