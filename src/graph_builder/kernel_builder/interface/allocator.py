from graph_builder.util import json


class WorkspaceLayout(json.SerializableMixin):
    def _to_serializable_(self):
        raise NotImplementedError


class AllocatorWebGPU:
    layout: WorkspaceLayout

    def allocate_params(self, weights) -> WorkspaceLayout:
        raise NotImplementedError

    def allocate_variables(self, weights) -> WorkspaceLayout:
        raise NotImplementedError
