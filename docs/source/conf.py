from recommonmark.parser import CommonMarkParser
from recommonmark.transform import AutoStructify

import webdnn

extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.doctest',
              'sphinx.ext.intersphinx',
              'sphinx.ext.coverage',
              'sphinx.ext.mathjax',
              'sphinx.ext.viewcode',
              'sphinx.ext.githubpages',
              'sphinx.ext.napoleon']

master_doc = 'index'

project = 'MIL WebDNN'
copyright = '2017, MIL'
author = 'MIL'

version = ".".join(webdnn.__version__.split(".")[:2])
release = webdnn.__version__

language = None

exclude_patterns = ["api_reference/descriptor_runner"]

pygments_style = 'sphinx'

# todo_include_todos = False

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
intersphinx_mapping = {"https://docs.python.org/3.6": None}

napoleon_include_special_with_doc = True
source_parsers = {
    '.md': CommonMarkParser,
}
source_suffix = ['.rst', '.md']


def setup(app):
    app.add_config_value('recommonmark_config', {
        'enable_eval_rst': True,
        'enable_auto_doc_ref': True,
    }, True)
    app.add_transform(AutoStructify)
