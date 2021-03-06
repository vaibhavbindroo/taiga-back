# -*- coding: utf-8 -*-
# Copyright (C) 2014-2016 Andrey Antukh <niwi@niwi.nz>
# Copyright (C) 2014-2016 Jesús Espino <jespinog@gmail.com>
# Copyright (C) 2014-2016 David Barragán <bameda@dbarragan.com>
# Copyright (C) 2014-2016 Alejandro Alonso <alejandro.alonso@kaleidos.net>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from django.utils.translation import ugettext as _

from taiga.base.api import serializers

from . import services
from . import fields

import re


class ProjectTagSerializer(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        # Don't pass the extra project arg
        self.project = kwargs.pop("project")

        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)


class CreateTagSerializer(ProjectTagSerializer):
    tag = serializers.CharField()
    color = serializers.CharField(required=False)

    def validate_tag(self, attrs, source):
        tag = attrs.get(source, None)
        if services.tag_exist_for_project_elements(self.project, tag):
            raise serializers.ValidationError(_("The tag exists."))

        return attrs

    def validate_color(self, attrs, source):
        color = attrs.get(source, None)
        if not re.match('^\#([a-fA-F0-9]{6}|[a-fA-F0-9]{3})$', color):
            raise serializers.ValidationError(_("The color is not a valid HEX color."))

        return attrs


class EditTagTagSerializer(ProjectTagSerializer):
    from_tag = serializers.CharField()
    to_tag = serializers.CharField(required=False)
    color = serializers.CharField(required=False)

    def validate_from_tag(self, attrs, source):
        tag = attrs.get(source, None)
        if not services.tag_exist_for_project_elements(self.project, tag):
            raise serializers.ValidationError(_("The tag doesn't exist."))

        return attrs

    def validate_to_tag(self, attrs, source):
        tag = attrs.get(source, None)
        if services.tag_exist_for_project_elements(self.project, tag):
            raise serializers.ValidationError(_("The tag exists yet"))

        return attrs

    def validate_color(self, attrs, source):
        color = attrs.get(source, None)
        if not re.match('^\#([a-fA-F0-9]{6}|[a-fA-F0-9]{3})$', color):
            raise serializers.ValidationError(_("The color is not a valid HEX color."))

        return attrs


class DeleteTagSerializer(ProjectTagSerializer):
    tag = serializers.CharField()

    def validate_tag(self, attrs, source):
        tag = attrs.get(source, None)
        if not services.tag_exist_for_project_elements(self.project, tag):
            raise serializers.ValidationError(_("The tag doesn't exist."))

        return attrs


class MixTagsSerializer(ProjectTagSerializer):
    from_tags = fields.TagsField()
    to_tag = serializers.CharField()

    def validate_from_tags(self, attrs, source):
        tags = attrs.get(source, None)
        for tag in tags:
            if not services.tag_exist_for_project_elements(self.project, tag):
                raise serializers.ValidationError(_("The tag doesn't exist."))

        return attrs

    def validate_to_tag(self, attrs, source):
        tag = attrs.get(source, None)
        if not services.tag_exist_for_project_elements(self.project, tag):
            raise serializers.ValidationError(_("The tag doesn't exist."))

        return attrs
