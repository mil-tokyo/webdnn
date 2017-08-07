import chainer

from webdnn.frontend.chainer.converter import ChainerConverter


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("Accuracy")
def _convert_accuracy(converter: ChainerConverter, c_op: "chainer.functions.Accuracy"):
    # TODO
    raise NotImplementedError("[ChainerConverter] Accuracy is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("BinaryAccuracy")
def _convert_binary_accuracy(converter: ChainerConverter, c_op: "chainer.functions.BinaryAccuracy"):
    # TODO
    raise NotImplementedError("[ChainerConverter] BinaryAccuracy is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("ClassificationSummary")
def _convert_classification_summary(converter: ChainerConverter, c_op: "chainer.functions.ClassificationSummary"):
    # TODO
    raise NotImplementedError("[ChainerConverter] ClassificationSummary is not supported")


# noinspection PyUnusedLocal,PyUnresolvedReferences
@ChainerConverter.register_handler("R2_score")
def _convert_r2_score(converter: ChainerConverter, c_op: "chainer.functions.evaluation.r2_score.R2_score"):
    # TODO
    raise NotImplementedError("[ChainerConverter] R2_score is not supported")
