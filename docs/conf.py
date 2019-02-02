"""Sphinx conf

Mostly copied and adapted from https://github.com/theislab/scanpy/
"""

import sys
import inspect
import logging
from pathlib import Path
from typing import Optional

from sphinx.application import Sphinx
from sphinx.ext import autosummary

if 'six' in sys.modules:
    print(*sys.path, sep='\n')
    for pypath in list(sys.path):
        if any(p in pypath for p in ['PyCharm', 'pycharm']) and 'helpers' in pypath:
            sys.path.remove(pypath)
    del sys.modules['six']

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))

logger = logging.getLogger(__name__)

import pypairs

# -- Project information -----------------------------------------------------

project = 'PyPairs'
copyright = '2018, R. Fechtner, A. Scialdone'
author = 'R. Fechtner, A. Scialdone'

# The short X.Y version
version = pypairs.__version__.replace('.dirty', '')
# The full version, including alpha/beta/rc tags
release = version


# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.coverage',
    'sphinx.ext.mathjax',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
    'sphinx_autodoc_typehints',
    'sphinx.ext.intersphinx'
]

# Generate the API documentation when building
autosummary_generate = True
# both of the following two lines don't work
# see falexwolf's issue for numpydoc
# autodoc_member_order = 'bysource'
# autodoc_default_flags = ['members']
napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_use_rtype = False
napoleon_custom_sections = [('Params', 'Parameters')]

intersphinx_mapping = dict(
    python=('https://docs.python.org/3', None),
    numpy=('https://docs.scipy.org/doc/numpy/', None),
    pandas=('http://pandas.pydata.org/pandas-docs/stable/', None),
    anndata=('https://anndata.readthedocs.io/en/latest/', None),
    scanpy=('https://scanpy.readthedocs.io/en/stable/', None),
    numba=('https://numba.pydata.org/numba-doc/latest/', None)
)

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
pygments_style = 'sphinx'
todo_include_todos = False

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
html_theme_options = dict(
    navigation_depth=2,
)

html_context = dict(
    display_github=True,      # Integrate GitHub
    github_user='rfechtner',   # Username
    github_repo='pypairs',     # Repo name
    github_version='master',  # Version
    conf_py_path='/docs/',    # Path in the checkout to the docs root
)


# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# The default sidebars (for documents that don't match any pattern) are
# defined by theme itself.  Builtin themes are using these templates by
# default: ``['localtoc.html', 'relations.html', 'sourcelink.html',
# 'searchbox.html']``.
#
# html_sidebars = {}

def setup(app):
    app.add_stylesheet('css/custom.css')



# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'PyPairs-Documentation'


# -- Options for LaTeX output ------------------------------------------------

latex_engine = 'pdflatex'

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'PyPairs.tex', 'PyPairs Documentation',
     author, 'manual'),
]


# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'pypairs', 'PyPairs Documentation',
     author, 1)
]


# -- Options for Texinfo output ----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'pypairs', 'PyPairs Documentation',
     author, 'PyPairs', 'A python scRNA-Seq classifier',
     'Miscellaneous'),
]

# -- Extension configuration -------------------------------------------------

# -- generate_options override ------------------------------------------
# The only thing changed here is that we specify imported_members=True
# in the generate_autosummary_docs call.


def process_generate_options(app: Sphinx):
    genfiles = app.config.autosummary_generate

    if genfiles and not hasattr(genfiles, '__len__'):
        env = app.builder.env
        genfiles = [
            env.doc2path(x, base=None)
            for x in env.found_docs
            if Path(env.doc2path(x)).is_file()
        ]
    if not genfiles:
        return

    ext = app.config.source_suffix
    genfiles = [
        genfile + ('' if genfile.endswith(tuple(ext)) else ext[0])
        for genfile in genfiles
    ]

    suffix = autosummary.get_rst_suffix(app)
    if suffix is None:
        return

    from sphinx.ext.autosummary.generate import generate_autosummary_docs
    generate_autosummary_docs(
        genfiles, builder=app.builder,
        warn=logger.warning, info=logger.info,
        suffix=suffix, base_path=app.srcdir,
        imported_members=True, app=app,
    )


autosummary.process_generate_options = process_generate_options

# -- GitHub URLs for class and method pages ------------------------------------------


def get_obj_module(qualname):
    """Get a module/class/attribute and its original module by qualname"""
    modname = qualname
    classname = None
    attrname = None
    while modname not in sys.modules:
        attrname = classname
        modname, classname = modname.rsplit('.', 1)

    # retrieve object and find original module name
    if classname:
        cls = getattr(sys.modules[modname], classname)
        modname = cls.__module__
        obj = getattr(cls, attrname) if attrname else cls
    else:
        obj = None

    return obj, sys.modules[modname]


def get_linenos(obj):
    """Get an object’s line numbers"""
    try:
        lines, start = inspect.getsourcelines(obj)
    except TypeError:
        return None, None
    else:
        return start, start + len(lines) - 1


project_dir = Path(__file__).parent.parent  # project/docs/conf.py/../.. → project/
github_url1 = 'https://github.com/{github_user}/{github_repo}/tree/{github_version}'.format_map(html_context)
github_url2 = 'https://github.com/theislab/anndata/tree/master'


def modurl(qualname: str) -> str:
    """Get the full GitHub URL for some object’s qualname."""
    obj, module = get_obj_module(qualname)
    github_url = github_url1
    try:
        path = Path(module.__file__).relative_to(project_dir)
    except ValueError:
        # trying to document something from another package
        github_url = github_url2
        path = '/'.join(module.__file__.split('/')[-2:])
    start, end = get_linenos(obj)
    fragment = '#L{}-L{}'.format(start, end) if start and end else ''
    return '{}/{}{}'.format(github_url, path, fragment)


def api_image(qualname: str) -> Optional[str]:
    # I’d like to make this a contextfilter, but the jinja context doesn’t contain the path,
    # so no chance to not hardcode “api/” here.
    path = Path(__file__).parent / '{}.png'.format(qualname)
    print(path, path.is_file())
    return '.. image:: {}\n   :width: 200\n   :align: right'.format(path.name) if path.is_file() else ''


# html_context doesn’t apply to autosummary templates ☹
# and there’s no way to insert filters into those templates
# so we have to modify the default filters
from jinja2.defaults import DEFAULT_FILTERS

DEFAULT_FILTERS.update(modurl=modurl, api_image=api_image)

# -- Override some classnames in autodoc --------------------------------------------
# This makes sure that automatically documented links actually
# end up being links instead of pointing nowhere.


import sphinx_autodoc_typehints

qualname_overrides = {
    'anndata.base.AnnData': 'anndata.AnnData',
}

fa_orig = sphinx_autodoc_typehints.format_annotation
def format_annotation(annotation):
    if inspect.isclass(annotation):
        full_name = '{}'.format(annotation.__qualname__)
        override = qualname_overrides.get(full_name)
        if override is not None:
            return ':py:class:`~{}`'.format(qualname_overrides[full_name])
    return fa_orig(annotation)
sphinx_autodoc_typehints.format_annotation = format_annotation

# -- Prettier Param docs --------------------------------------------
# Our PrettyTypedField is the same as the default PyTypedField,
# except that the items (e.g. function parameters) get rendered as
# definition list instead of paragraphs with some formatting.

from typing import Dict, List, Tuple

from docutils import nodes
from sphinx import addnodes
from sphinx.domains.python import PyTypedField, PyObject
from sphinx.environment import BuildEnvironment


class PrettyTypedField(PyTypedField):
    list_type = nodes.definition_list

    def make_field(
        self,
        types: Dict[str, List[nodes.Node]],
        domain: str,
        items: Tuple[str, List[nodes.inline]],
        env: BuildEnvironment = None
    ) -> nodes.field:
        def makerefs(rolename, name, node):
            return self.make_xrefs(rolename, domain, name, node, env=env)

        def handle_item(fieldarg: str, content: List[nodes.inline]) -> nodes.definition_list_item:
            head = nodes.term()
            head += makerefs(self.rolename, fieldarg, addnodes.literal_strong)
            fieldtype = types.pop(fieldarg, None)
            if fieldtype is not None:
                head += nodes.Text(' : ')
                if len(fieldtype) == 1 and isinstance(fieldtype[0], nodes.Text):
                    text_node, = fieldtype  # type: nodes.Text
                    head += makerefs(self.typerolename, text_node.astext(), addnodes.literal_emphasis)
                else:
                    head += fieldtype

            body_content = nodes.paragraph('', '', *content)
            body = nodes.definition('', body_content)

            return nodes.definition_list_item('', head, body)

        fieldname = nodes.field_name('', self.label)
        if len(items) == 1 and self.can_collapse:
            fieldarg, content = items[0]
            bodynode = handle_item(fieldarg, content)
        else:
            bodynode = self.list_type()
            for fieldarg, content in items:
                bodynode += handle_item(fieldarg, content)
        fieldbody = nodes.field_body('', bodynode)
        return nodes.field('', fieldname, fieldbody)


# replace matching field types with ours
PyObject.doc_field_types = [
    PrettyTypedField(
        ft.name,
        names=ft.names,
        typenames=ft.typenames,
        label=ft.label,
        rolename=ft.rolename,
        typerolename=ft.typerolename,
        can_collapse=ft.can_collapse,
    ) if isinstance(ft, PyTypedField) else ft
    for ft in PyObject.doc_field_types
]