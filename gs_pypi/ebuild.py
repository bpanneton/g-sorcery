#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    ebuild.py
    ~~~~~~~~~
    
    ebuild generation
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

import collections
import os

from g_sorcery.ebuild import DefaultEbuildGenerator

Layout = collections.namedtuple("Layout",
    ["vars_before_inherit", "inherit", "vars_after_description", "vars_after_keywords"])
  

class PypiEbuildWithoutDigestGenerator(DefaultEbuildGenerator):
    def __init__(self, package_db):

        vars_before_inherit = \
          []

        inherit = ["gs-pypi"]
        
        vars_after_description = \
          []

        vars_after_keywords = \
          []

        layout = Layout(vars_before_inherit, inherit, vars_after_description, vars_after_keywords)

        super(PypiEbuildWithoutDigestGenerator, self).__init__(package_db, layout)

class PypiEbuildWithDigestGenerator(DefaultEbuildGenerator):
    def __init__(self, package_db):

        vars_before_inherit = \
          []

        inherit = ["gs-pypi"]
        
        vars_after_description = \
          []

        vars_after_keywords = \
          []

        layout = Layout(vars_before_inherit, inherit, vars_after_description, vars_after_keywords)

        super(PypiEbuildWithDigestGenerator, self).__init__(package_db, layout)
