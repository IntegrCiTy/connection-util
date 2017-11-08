import pkg_resources  # part of setuptools
try:
    __version__ = pkg_resources.require("connection-util")[0].version
except :
    pass
