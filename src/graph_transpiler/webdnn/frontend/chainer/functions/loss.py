import chainer

from webdnn.frontend.chainer.converter import ChainerConverter


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("AbsoluteError")
def _convert_absolute_error(converter: ChainerConverter, c_op: "chainer.functions.AbsoluteError"):
    # TODO
    raise NotImplementedError("[ChainerConverter] AbsoluteError is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("Contrastive")
def _convert_contrastive(converter: ChainerConverter, c_op: "chainer.functions.Contrastive"):
    # TODO
    raise NotImplementedError("[ChainerConverter] Contrastive is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("CrossCovariance")
def _convert_cross_covariance(converter: ChainerConverter, c_op: "chainer.functions.CrossCovariance"):
    # TODO
    raise NotImplementedError("[ChainerConverter] CrossCovariance is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("ConnectionistTemporalClassification")
def _convert_connectionist_temporal_classification(converter: ChainerConverter,
                                                   c_op: "chainer.functions.ConnectionistTemporalClassification"):
    # TODO
    raise NotImplementedError("[ChainerConverter] ConnectionistTemporalClassification is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("DeCov")
def _convert_decov(converter: ChainerConverter, c_op: "chainer.functions.DeCov"):
    # TODO
    raise NotImplementedError("[ChainerConverter] DeCov is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("Hinge")
def _convert_hinge(converter: ChainerConverter, c_op: "chainer.functions.Hinge"):
    # TODO
    raise NotImplementedError("[ChainerConverter] Hinge is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("HuberLoss")
def _convert_huber_loss(converter: ChainerConverter, c_op: "chainer.functions.HuberLoss"):
    # TODO
    raise NotImplementedError("[ChainerConverter] HuberLoss is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("MeanAbsoluteError")
def _convert_mean_absolute_error(converter: ChainerConverter, c_op: "chainer.functions.MeanAbsoluteError"):
    # TODO
    raise NotImplementedError("[ChainerConverter] MeanAbsoluteError is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("MeanSquaredError")
def _convert_mean_squared_error(converter: ChainerConverter, c_op: "chainer.functions.MeanSquaredError"):
    # TODO
    raise NotImplementedError("[ChainerConverter] MeanSquaredError is not supported")


# noinspection PyUnusedLocal,PyUnresolvedReferences
@ChainerConverter.register_handler("NegativeSamplingFunction")
def _convert_negative_sampling_function(converter: ChainerConverter,
                                        c_op: "chainer.functions.loss.negative_sampling.NegativeSamplingFunction"):
    # TODO
    raise NotImplementedError("[ChainerConverter] NegativeSamplingFunction is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("SigmoidCrossEntropy")
def _convert_sigmoid_cross_entropy(converter: ChainerConverter, c_op: "chainer.functions.SigmoidCrossEntropy"):
    # TODO
    raise NotImplementedError("[ChainerConverter] SigmoidCrossEntropy is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("SoftmaxCrossEntropy")
def _convert_softmax_cross_entropy(converter: ChainerConverter, c_op: "chainer.functions.SoftmaxCrossEntropy"):
    # TODO
    raise NotImplementedError("[ChainerConverter] SoftmaxCrossEntropy is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("SquaredError")
def _convert_squared_error(converter: ChainerConverter, c_op: "chainer.functions.SquaredError"):
    # TODO
    raise NotImplementedError("[ChainerConverter] SquaredError is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("Triplet")
def _convert_triplet(converter: ChainerConverter, c_op: "chainer.functions.Triplet"):
    # TODO
    raise NotImplementedError("[ChainerConverter] Triplet is not supported")
