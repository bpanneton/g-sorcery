#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    ebuild.py
    ~~~~~~~~~~~~~
    
    ebuild generation
    
    :copyright: (c) 2013 by Jauhien Piatlicki
    :license: GPL-2, see LICENSE for more details.
"""

from .compatibility import basestring
from .exceptions import DependencyError

class EbuildGenerator(object):
    """
    Ebuild generator.
    """
    def __init__(self, package_db):
        """
        Args:
            package_db: Package database.
        """
        self.package_db = package_db

    def generate(self, package, ebuild_data=None):
        """
        Generate an ebuild for a package.

        Args:
            package: package_db.Package instance.
            ebuild_data: Dictionary with ebuild data.

        Returns:
            Ebuild source as a list of strings.
        """
        #a possible exception should be catched in the caller
        if not ebuild_data:
            ebuild_data = self.package_db.get_package_description(package)
        ebuild_data = self.process_ebuild_data(ebuild_data)
        ebuild = self.get_template(package, ebuild_data)
        ebuild = self.process(ebuild, ebuild_data)
        ebuild = self.postprocess(ebuild, ebuild_data)
        return ebuild

    def process_ebuild_data(self, ebuild_data):
        """
        A hook allowing changing ebuild_data before ebuild generation.

        Args:
            ebuild_data: Dictinary with ebuild data.

        Returns:
            Dictinary with ebuild data.
        """
        return ebuild_data

    def process(self, ebuild, ebuild_data):
        """
        Fill ebuild template with data.

        Args:
            ebuild: Ebuild template.
            ebuild_data: Dictionary with ebuild data.

        Returns:
            Ebuild source as a list of strings.
        """
        result = []
        for line in ebuild:
            error = ""
            try:
                line = line % ebuild_data
            except ValueError as e:
                error = str(e)
            if error:
                error = "substitution failed in line '" + line + "': " + error
                raise DependencyError(error)
            result.append(line)
            
        return result
        
    def get_template(self, package, ebuild_data):
        """
        Generate ebuild template. Should be overriden.

        Args:
            package: package_db.Package instance.
            ebuild_data: Dictionary with ebuild data.

        Returns:
            Ebuild template.
        """
        ebuild = []
        return ebuild
        
    def postprocess(self, ebuild, ebuild_data):
        """
        A hook for changing of a generated ebuild.

        Args:
            ebuild: Ebuild source as a list of strings.
            ebuild_data: Dictionary with ebuild data.

        Returns:
            Ebuild source as a list of strings.
        """
        return ebuild

class EbuildGeneratorFromFile(EbuildGenerator):
    """
    Ebuild generators that takes templates from files.
    """
    def __init__(self, package_db, filename=""):
        super(EbuildGeneratorFromFile, self).__init__(package_db)
        self.filename = filename

    def get_template(self, package, ebuild_data):
        """
        Generate ebuild template.

        Args:
            package: package_db.Package instance.
            ebuild_data: Dictionary with ebuild data.

        Returns:
            Ebuild template.
        """
        name = self.get_template_file(package, ebuild_data)
        with open(name, 'r') as f:
            ebuild = f.read().split('\n')
            if ebuild[-1] == '':
                ebuild = ebuild[:-1]
        return ebuild

    def get_template_file(self, package, ebuild_data):
        """
        Get template filename for a package. Should be overriden.
        
        Args:
            package: package_db.Package instance.
            ebuild_data: Dictionary with ebuild data.

        Returns:
            Template filename.
        """
        return self.filename


class DefaultEbuildGenerator(EbuildGenerator):
    """
    Default ebuild generator.

    Takes a layout dictinary that describes ebuild structure and generates
    an ebuild temlate basing on it.

    Layout has entries for vars and inherited eclasses. Each entry is a list.
    Entries are processed in the following order:
    
    vars_before_inherit
    inherit
    vars_after_inherit
    vars_after_description
    vars_after_keywords

    inherit entry is just a list of eclass names.
    vars* entries are lists of variables in tw0 possible formats:
    1. A string with variable name
    2. A dictinary with entries:
        name: variable name
        value: variable value
        raw: if present, no quotation of value will be done
    Variable names are automatically transformed to the upper-case.
    """
    def __init__(self, package_db, layout):
        super(DefaultEbuildGenerator, self).__init__(package_db)
        self.template = ["# automatically generated by g-sorcery",
                         "# please do not edit this file",
                         ""]

        if hasattr(layout, "eapi"):
            self.template.append("EAPI=%s" % layout.eapi)
        else:
            self.template.append("EAPI=5")
        self.template.append("")

        if hasattr(layout, "vars_before_inherit"):
            self._append_vars_to_template(layout.vars_before_inherit)
            self.template.append("")

        if hasattr(layout, "inherit"):
            self.template.append("inherit " + " ".join(layout.inherit))
            self.template.append("")

        if hasattr(layout, "vars_after_inherit"):
            self._append_vars_to_template(layout.vars_after_inherit)
            self.template.append("")

        self.template.append('DESCRIPTION="%(description)s"')
        self.template.append("")

        if hasattr(layout, "vars_after_description"):
            self._append_vars_to_template(layout.vars_after_description)
            self.template.append("")

        self.template.append('SLOT="0"')
        self.template.append('KEYWORDS="~amd64 ~x86"')
        self.template.append("")

        if hasattr(layout, "vars_after_keywords"):
            self._append_vars_to_template(layout.vars_after_keywords)
            self.template.append("")
        

    def _append_vars_to_template(self, variables):
        """
        Add a list of variables to the end of template.

        Args:
            variables: List of variables.
        """
        for var in variables:
            if isinstance(var, basestring):
                self.template.append(var.upper() + '="%(' + var + ')s"')
            else:
                if "raw" in var:
                    quote = ''
                else:
                    quote = '"'
                if "value" in var:
                    self.template.append(var["name"].upper() \
                                         + '=' + quote + var["value"] + quote)
                else:
                    self.template.append(var["name"].upper() + '=' + quote + '%(' + var["name"] + ')s' + quote)


    def get_template(self, package, ebuild_data):
        """
        Generate ebuild template.

        Args:
            package: package_db.Package instance.
            ebuild_data: Dictionary with ebuild data.

        Returns:
            Ebuild template.
        """
        return self.template
