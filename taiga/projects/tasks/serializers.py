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

from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from taiga.base.api import serializers
from taiga.base.fields import PgArrayField
from taiga.base.neighbors import NeighborsSerializerMixin

from taiga.projects.milestones.validators import SprintExistsValidator
from taiga.projects.mixins.serializers import OwnerExtraInfoMixin
from taiga.projects.mixins.serializers import AssigedToExtraInfoMixin
from taiga.projects.mixins.serializers import StatusExtraInfoMixin
from taiga.projects.notifications.mixins import EditableWatchedResourceModelSerializer
from taiga.projects.notifications.mixins import ListWatchedResourceModelSerializer
from taiga.projects.notifications.validators import WatchersValidator
from taiga.projects.serializers import BasicTaskStatusSerializerSerializer
from taiga.mdrender.service import render as mdrender
from taiga.projects.tagging.fields import TagsAndTagsColorsField
from taiga.projects.tasks.validators import TaskExistsValidator
from taiga.projects.validators import ProjectExistsValidator
from taiga.projects.votes.mixins.serializers import VoteResourceSerializerMixin
from taiga.projects.votes.mixins.serializers import ListVoteResourceSerializerMixin

from taiga.users.serializers import UserBasicInfoSerializer
from taiga.users.services import get_photo_or_gravatar_url
from taiga.users.services import get_big_photo_or_gravatar_url

from . import models

import serpy

class TaskSerializer(WatchersValidator, VoteResourceSerializerMixin, EditableWatchedResourceModelSerializer,
                     serializers.ModelSerializer):
    tags = TagsAndTagsColorsField(default=[], required=False)
    external_reference = PgArrayField(required=False)
    comment = serializers.SerializerMethodField("get_comment")
    milestone_slug = serializers.SerializerMethodField("get_milestone_slug")
    blocked_note_html = serializers.SerializerMethodField("get_blocked_note_html")
    description_html = serializers.SerializerMethodField("get_description_html")
    is_closed = serializers.SerializerMethodField("get_is_closed")
    status_extra_info = BasicTaskStatusSerializerSerializer(source="status", required=False, read_only=True)
    assigned_to_extra_info = UserBasicInfoSerializer(source="assigned_to", required=False, read_only=True)
    owner_extra_info = UserBasicInfoSerializer(source="owner", required=False, read_only=True)

    class Meta:
        model = models.Task
        read_only_fields = ('id', 'ref', 'created_date', 'modified_date', 'owner')

    def get_comment(self, obj):
        return ""

    def get_milestone_slug(self, obj):
        if obj.milestone:
            return obj.milestone.slug
        else:
            return None

    def get_blocked_note_html(self, obj):
        return mdrender(obj.project, obj.blocked_note)

    def get_description_html(self, obj):
        return mdrender(obj.project, obj.description)

    def get_is_closed(self, obj):
        return obj.status is not None and obj.status.is_closed


class TaskListSerializer(ListVoteResourceSerializerMixin, ListWatchedResourceModelSerializer,
                         OwnerExtraInfoMixin, AssigedToExtraInfoMixin, StatusExtraInfoMixin,
                         serializers.LightSerializer):
    id = serpy.Field()
    user_story = serpy.Field(attr="user_story_id")
    ref = serpy.Field()
    project = serpy.Field(attr="project_id")
    milestone = serpy.Field(attr="milestone_id")
    milestone_slug = serpy.MethodField("get_milestone_slug")
    created_date = serpy.Field()
    modified_date = serpy.Field()
    finished_date = serpy.Field()
    subject = serpy.Field()
    us_order = serpy.Field()
    taskboard_order = serpy.Field()
    is_iocaine = serpy.Field()
    external_reference = serpy.Field()
    version = serpy.Field()
    watchers = serpy.Field()
    is_blocked = serpy.Field()
    blocked_note = serpy.Field()
    tags = serpy.Field()
    is_closed = serpy.MethodField()

    def get_milestone_slug(self, obj):
        return obj.milestone.slug if obj.milestone else None

    def get_is_closed(self, obj):
        return obj.status is not None and obj.status.is_closed


class TaskNeighborsSerializer(NeighborsSerializerMixin, TaskSerializer):
    def serialize_neighbor(self, neighbor):
        if neighbor:
            return NeighborTaskSerializer(neighbor).data
        return None


class NeighborTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Task
        fields = ("id", "ref", "subject")
        depth = 0


class TasksBulkSerializer(ProjectExistsValidator, SprintExistsValidator,
                          TaskExistsValidator, serializers.Serializer):
    project_id = serializers.IntegerField()
    sprint_id = serializers.IntegerField()
    status_id = serializers.IntegerField(required=False)
    us_id = serializers.IntegerField(required=False)
    bulk_tasks = serializers.CharField()


## Order bulk serializers

class _TaskOrderBulkSerializer(TaskExistsValidator, serializers.Serializer):
    task_id = serializers.IntegerField()
    order = serializers.IntegerField()


class UpdateTasksOrderBulkSerializer(ProjectExistsValidator, serializers.Serializer):
    project_id = serializers.IntegerField()
    bulk_tasks = _TaskOrderBulkSerializer(many=True)
