from graph_builder.frontend.graph import Graph, LayerAttributes
from graph_builder.util import flags


class GraphOptimizer:
    def __init__(self, graph: Graph):
        self.graph = graph

    def optimize(self):
        while True:
            variable_to_node = self._get_variable_to_node()
            for variable, prod_cons in variable_to_node.items():
                # ある変数からみて生成側と消費側がくっつくかどうか判定
                prod = prod_cons['producer']
                cons_list = prod_cons['consumers']
                cons_first = cons_list[0] if len(cons_list) > 0 else None
                if prod is not None \
                    and flags.optimize.CONCAT_ELEMENTWISE_OPERATION \
                    and LayerAttributes.PostElementwise in prod.layer.attributes \
                    and len(cons_list) == 1 \
                    and LayerAttributes.Elementwise in cons_first.layer.attributes:
                    # linearのうしろにreluをくっつける
                    prod.layer.append_child_to_tail(cons_first.layer)
                    # linearの出力がreluの出力になる
                    prod.tops[0] = cons_first.tops[0]
                    # 後続レイヤーが持たないattributeを消す(これでいいのか？)
                    prod.layer.attributes &= cons_first.layer.attributes
                    # reluのノードは消える (同時に、linear-relu間の変数もなくなる)
                    self.graph.nodes.remove(cons_first)
                    break  # グラフが変わったのでvariable_to_nodeをつくりなおす
                if prod is not None \
                    and flags.optimize.CONCAT_CHANNELWISE_OPERATION \
                    and LayerAttributes.PostChannelwise in prod.layer.attributes \
                    and len(cons_list) == 1 \
                    and LayerAttributes.Channelwise in cons_first.layer.attributes:
                    # linearのうしろにbiasをくっつける
                    prod.layer.append_child_to_tail(cons_first.layer)
                    # linearの出力がbiasの出力になる
                    prod.tops[0] = cons_first.tops[0]
                    # 後続レイヤーが持たないattributeを消す(これでいいのか？)
                    prod.layer.attributes &= cons_first.layer.attributes
                    # biasのノードは消える (同時に、linear-bias間の変数もなくなる)
                    self.graph.nodes.remove(cons_first)
                    break  # グラフが変わったのでvariable_to_nodeをつくりなおす
            else:
                # グラフが変化しなかった
                break

    def _get_variable_to_node(self):
        """
        変数からみた、作成者および消費者ノード情報の作成
        """
        variable_to_node = {}
        for node in self.graph.nodes:
            for bottom in node.bottoms:
                if bottom.name not in variable_to_node:
                    variable_to_node[bottom.name] = {'producer': None, 'consumers': []}
                variable_to_node[bottom.name]['consumers'].append(node)

            for top in node.tops:
                if top.name not in variable_to_node:
                    variable_to_node[top.name] = {'producer': None, 'consumers': []}
                variable_to_node[top.name]['producer'] = node
        return variable_to_node
