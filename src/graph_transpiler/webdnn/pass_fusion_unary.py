from typing import Dict, Iterable, List, Optional
import onnx

from webdnn.optimization_pass import OptimizationPass, OptimizationPassResult
from webdnn.util import make_random_identifier
from webdnn.operator_shader import OperatorShader

UNARY_OPERATORS = ["Ceil", "Exp", "Floor", "Relu", "Sigmoid", "Sqrt", "Tanh"]

class PassFusionUnary(OptimizationPass):
    def optimize(self, model: onnx.ModelProto) -> Optional[OptimizationPassResult]:
        target_nodes_list = self._find_target_nodes(model)
        all_custom_shaders = {}
        for target_nodes in target_nodes_list:
            custom_shaders = self._fuse_combi(model, target_nodes)
            all_custom_shaders.update(custom_shaders)
        result = None
        if len(all_custom_shaders) > 0:
            result = self._construct_result()
            result.operator_shaders = all_custom_shaders
        return result
    
    def _construct_result(self):
        raise NotImplementedError
    
    def _find_target_nodes(self, model: onnx.ModelProto) -> List[List[onnx.NodeProto]]:
        graph = model.graph
        unary_nodes = []
        unary_input_names = set()
        unary_output_names = set()
        for node in graph.node:
            if node.op_type in UNARY_OPERATORS:
                unary_nodes.append(node)
                unary_input_names.add(node.input[0])
                unary_output_names.add(node.output[0])
        # この変数を出力とするoperatorと入力とするoperatorを連結可能
        unary_to_unary_vars = unary_input_names & unary_output_names
        merge_combis = []
        for v in unary_to_unary_vars:
            prev_node = self._find_node_which_output(v, graph.node)
            next_nodes = self._find_nodes_which_consume_input(v, graph.node)
            if len(next_nodes) > 1:
                continue
            merge_combis.append([prev_node, next_nodes[0]])
        # 3つ以上の連結を探す
        while True:
            changed = False
            for combi in merge_combis:
                head = combi[0]
                joinable = None
                for combi2 in merge_combis:
                    if combi2[-1] == head:
                        joinable = combi2
                        break
                if joinable is not None:
                    merge_combis.remove(combi)
                    merge_combis.remove(joinable)
                    new_combi = joinable + combi[1:]
                    merge_combis.append(new_combi)
                    changed = True
                    break
            if not changed:
                break
        return merge_combis

    def _find_nodes_which_consume_input(self, name: str, nodes: Iterable[onnx.NodeProto]) -> List[onnx.NodeProto]:
        return [node for node in nodes if name in node.input]
    
    def _find_node_which_output(self, name: str, nodes: Iterable[onnx.NodeProto]) -> Optional[onnx.NodeProto]:
        rets = [node for node in nodes if name in node.output]
        assert len(rets) <= 1
        if len(rets) == 1:
            return rets[0]
        return None

    def _fuse_combi(self, model: onnx.ModelProto, nodes: List[onnx.NodeProto]) -> Dict[str, OperatorShader]:
        # replace nodes into custom node
        custom_node_type = make_random_identifier()
        input_name = nodes[0].input[0]
        output_name = nodes[-1].output[0]
        shader = self._make_shader(custom_node_type, nodes)
        custom_node = onnx.helper.make_node(op_type=custom_node_type, inputs=[input_name], outputs=[output_name], name=custom_node_type)
        self._remove_insert_node(model, nodes, custom_node)
        return {custom_node_type: shader}

    def _remove_insert_node(self, model: onnx.ModelProto, remove_nodes: List[onnx.NodeProto], insert_node: onnx.NodeProto):
        graph = model.graph
        insert_pos = 0
        for i in range(len(graph.node)):
            if graph.node[i] == remove_nodes[0]:
                insert_pos = i
                break
        else:
            raise ValueError
        for node in remove_nodes:
            graph.node.remove(node)
        graph.node.insert(insert_pos, insert_node)

    def _make_shader(self, custom_op_type: str, nodes: List[onnx.NodeProto]) -> OperatorShader:
        raise NotImplementedError
