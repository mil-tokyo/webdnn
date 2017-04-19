from enum import Enum, auto


class Attribute:
    pass


class VariableAttributes(Enum):
    """
    変数の属性
    メモリ割り付けの際に利用
    """

    Input = auto()  # DNNへの入力
    Output = auto()  # DNNへの出力
    Constant = auto()
