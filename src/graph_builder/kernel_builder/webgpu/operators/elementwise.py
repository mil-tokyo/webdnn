class KBElementwiseOperator:
    """
    Elementwiseかつウェイト不要の処理が他のレイヤーに後続する際のカーネル関数生成
    """

    def __init__(self, func_name, sources, serial_generator):
        self.func_name = func_name
        self.sources = sources
        self.post_init_source = """
        """  # 初期化不要
        self.meta_buffer = b""
        self.serial_generator = serial_generator

    def wrap_expression(self, expression):
        return "{0}({1})".format(self.func_name, expression)

