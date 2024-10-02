# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('../../'))

import datetime
import codecs
import os.path

def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()

def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")

def get_short_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__short_version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")

# -- Project information -----------------------------------------------------

company = f"Teledyne LeCroy Xena"
year = datetime.datetime.today().year
month = datetime.datetime.today().month
project = f"Xena OpenAutomation Core"
copyright = f"{year}, {company}"
author = company
title = f"Xena OpenAutomation Core Documentation"
output_basename = f"xoa_core_doc"

# The full version, including alpha/beta/rc tags.
release = get_version("../../xoa_core/__init__.py")

# The short X.Y version.
version = get_short_version("../../xoa_core/__init__.py")


# -- General configuration -----------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'sphinx.ext.coverage',
    'sphinx.ext.viewcode',
    'sphinx.ext.todo',
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.extlinks',
    "sphinx_inline_tabs",
    'sphinx_copybutton',
    "sphinx_remove_toctrees",
    'sphinx_rtd_theme',
]
add_module_names = False
autodoc_default_options = {
    'member-order': 'bysource',
    'private-members': False,
    'undoc-members': False,
    'show-inheritance': True
}
autodoc_typehints = 'signature'
autodoc_typehints_format = 'short'
autodoc_inherit_docstrings = True
todo_include_todos = True
autosectionlabel_prefix_document = True

# The suffix(es) of source filenames.
# source_suffix = ['.rst', '.md']
source_suffix = '.rst'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# These patterns also affect html_static_path and html_extra_path
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The master toctree document.
master_doc = 'index'

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# -- Options for HTML output -----------------------------------------------------

# The theme to use for HTML and HTML Help pages.
html_theme = 'sphinx_rtd_theme'

# Output file base name for HTML help builder.
htmlhelp_basename = output_basename

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
html_title = title

# The path to the HTML logo image in the static path, or URL to the logo, or ''.
# html_logo = './_static/xoa_logo.png'

html_favicon = './_static/xoa_favicon_16.png'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Theme config for Furo
# html_show_copyright = True
# html_show_sphinx = False
# html_theme_options = {
#     "light_logo": "xoa_logo_light.png",
#     "dark_logo": "xoa_logo_dark.png",
#     "source_repository": "https://github.com/xenanetworks/open-automation-core",
#     "light_css_variables": {
#         "color-brand-primary": "#295341",
#         "color-brand-content": "#295341",
#     },
#     "navigation_with_keys": True,
# }
# If true, the index is generated twice: once as a single page with all the entries, 
# and once as one page per starting letter. Default is False.
# html_split_index = True

# Theme config for sphinx_rtd_theme
html_show_sphinx =  False
html_show_sourcelink = False
html_logo = './_static/tlc_w1.png'
html_context = {
    "display_github": False
}
html_theme_options = {
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    'vcs_pageview_mode': 'view',
    'style_nav_header_background': '#0076c0',
    'navigation_depth': 2,
}

# -- Options for Texinfo output -----------------------------------------------------

# This config value contains the locations and names of other projects that should be linked to in this documentation.
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}

intersphinx_disabled_domains = ['std']

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, output_basename, title, author, output_basename, title, 'Miscellaneous'),
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']


# -- Options for LaTeX output -----------------------------------------------------

latex_elements = {
# The paper size ('letterpaper' or 'a4paper').
'papersize': 'a4paper',

# The font size ('10pt', '11pt' or '12pt').
'pointsize': '12pt',

# Additional stuff for the LaTeX preamble.
#'preamble': r'',

# Latex figure (float) alignment
#'figure_align': 'htbp',

#'printindex': r'\def\twocolumn[#1]{#1}\printindex',
'makeindex': r'\usepackage[columns=1]{idxlayout}\makeindex',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [(master_doc, f"{output_basename}.tex", title, author, 'manual'),
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
latex_logo = './_static/tlc_pdf.png'

# -- Options for manual page output -----------------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, output_basename, title, [author], 1)
]


# -- Options for EPUB output -----------------------------------------------------
epub_title = title + ' ' + release
epub_author = author
epub_publisher = 'https://xenanetworks.com'
epub_copyright = copyright
epub_show_urls = 'footnote'
epub_basename = output_basename