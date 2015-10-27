#!/usr/bin/python
# -*- coding: utf-8  -*-
"""A generic bot to do data ingestion (batch uploading) to Commons."""
#
# (C) Pywikibot team, 2013
#
# Distributed under the terms of the MIT license.
#
__version__ = '$Id: 72e22f58054addf8408746ea45bf58c48b68a35f $'
#

import posixpath
import hashlib
import base64
import sys
import io

import pywikibot
# TODO: nosetests3 fails on 'import <other_script>', which is used by many
# of our scripts, but only data_ingestion is directly imported (not via pwb).
# https://github.com/nose-devs/nose/issues/839

if sys.version_info[0] > 2:
    from urllib.parse import urlparse
    from urllib.request import urlopen
else:
    from urlparse import urlparse
    from urllib import urlopen


class MediaObject(object):

    """
    Represents a Photo (or other file), with metadata, to upload to Commons.

    The constructor takes two parameters: URL (string) and metadata (dict with
    str:str key:value pairs) that can be referred to from the title & template
    generation.


    """

    def __init__(self, URL, metadata):
        """Constructor."""
        self.URL = URL
        self.metadata = metadata
        self.metadata["_url"] = URL
        self.metadata["_filename"] = filename = posixpath.split(
            urlparse(URL)[2])[1]
        self.metadata["_ext"] = ext = filename.split(".")[-1]
        if ext == filename:
            self.metadata["_ext"] = ext = None
        self.contents = None

    def downloadPhoto(self):
        """
        Download the photo and store it in a io.BytesIO object.

        TODO: Add exception handling
        """
        if not self.contents:
            imageFile = urlopen(self.URL).read()
            self.contents = io.BytesIO(imageFile)
        return self.contents

    def findDuplicateImages(self,
                            site=pywikibot.Site(u'commons', u'commons')):
        """
        Find duplicates of the photo.

        Calculates the SHA1 hash and asks the MediaWiki api
        for a list of duplicates.

        TODO: Add exception handling, fix site thing
        """
        hashObject = hashlib.sha1()
        hashObject.update(self.downloadPhoto().getvalue())
        return list(
            page.title(withNamespace=False) for page in
            site.allimages(sha1=base64.b16encode(hashObject.digest())))

    def getTitle(self, fmt):
        """
        Populate format string with %(name)s entries using metadata.

        @param fmt: format string
        @type fmt: unicode
        @return: formatted string
        @rtype: unicode
        """
        return fmt % self.metadata

    def getDescription(self, template, extraparams={}):
        """Generate a description for a file."""
        params = {}
        params.update(self.metadata)
        params.update(extraparams)
        description = u'{{%s\n' % template
        for key in sorted(params.keys()):
            value = params[key]
            if not key.startswith("_"):
                description = description + (
                    u'|%s=%s' % (key, self._safeTemplateValue(value))) + "\n"
        description = description + u'}}'

        return description

    def _safeTemplateValue(self, value):
        return value.replace("|", "{{!}}")
