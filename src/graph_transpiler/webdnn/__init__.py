import pkg_resources

try:
    __version__ = pkg_resources.require("webdnn")[0].version
except Exception:
    __version__ = '1.x.x.git'
    pass

from webdnn import backend
from webdnn import encoder
from webdnn import frontend
from webdnn import graph
from webdnn import optimizer
from webdnn import util
