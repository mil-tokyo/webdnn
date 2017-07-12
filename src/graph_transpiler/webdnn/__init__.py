import pkg_resources

__version__ = pkg_resources.require("webdnn")[0].version

from webdnn import backend
from webdnn import encoder
from webdnn import frontend
from webdnn import graph
from webdnn import optimizer
from webdnn import util
# alias
from webdnn.graph.attribute import Attribute
from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.operator import Operator
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.order import Order
from webdnn.graph.placeholder import Placeholder
from webdnn.graph.shape import Shape
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable
