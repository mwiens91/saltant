"""Contains filters to go along with viewsets for the REST API."""

from django_filters import rest_framework as filters
from tasksapi.models import (
    ContainerTaskInstance,
    ContainerTaskType,
    ExecutableTaskInstance,
    ExecutableTaskType,
    TaskQueue,
    TaskWhitelist,
    User,
)

# Common lookups for filter fields
CHAR_FIELD_LOOKUPS = [
    "exact",
    "contains",
    "in",
    "startswith",
    "endswith",
    "regex",
]
BOOLEAN_FIELD_LOOKUPS = ["exact"]
FOREIGN_KEY_FIELD_LOOKUPS = ["exact", "in"]
DATE_FIELD_LOOKUPS = ["exact", "year", "range", "lt", "lte", "gt", "gte"]

# Common sets of fields to use or extend
ABSTRACT_TASK_INSTANCE_FIELDS = {
    "name": CHAR_FIELD_LOOKUPS,
    "state": CHAR_FIELD_LOOKUPS,
    "user__username": CHAR_FIELD_LOOKUPS,
    "task_type": FOREIGN_KEY_FIELD_LOOKUPS,
    "task_queue": FOREIGN_KEY_FIELD_LOOKUPS,
    "datetime_created": DATE_FIELD_LOOKUPS,
    "datetime_finished": DATE_FIELD_LOOKUPS,
}
ABSTRACT_TASK_TYPE_FIELDS = {
    "name": CHAR_FIELD_LOOKUPS,
    "description": CHAR_FIELD_LOOKUPS,
    "user__username": CHAR_FIELD_LOOKUPS,
    "command_to_run": CHAR_FIELD_LOOKUPS,
    "datetime_created": DATE_FIELD_LOOKUPS,
}


class UserFilter(filters.FilterSet):
    """A filterset to support queries for Users."""

    class Meta:
        model = User
        fields = {"username": CHAR_FIELD_LOOKUPS, "email": CHAR_FIELD_LOOKUPS}


class ContainerTaskInstanceFilter(filters.FilterSet):
    """A filterset to support queries for container task instance attributes."""

    class Meta:
        model = ContainerTaskInstance
        fields = ABSTRACT_TASK_INSTANCE_FIELDS


class ContainerTaskTypeFilter(filters.FilterSet):
    """A filterset to support queries for container task type attributes."""

    class Meta:
        model = ContainerTaskType
        container_fields = {
            "container_image": CHAR_FIELD_LOOKUPS,
            "container_type": CHAR_FIELD_LOOKUPS,
        }
        fields = {**ABSTRACT_TASK_TYPE_FIELDS, **container_fields}


class ExecutableTaskInstanceFilter(filters.FilterSet):
    """A filterset to support queries for executable task instance attributes."""

    class Meta:
        model = ExecutableTaskInstance
        fields = ABSTRACT_TASK_INSTANCE_FIELDS


class ExecutableTaskTypeFilter(filters.FilterSet):
    """A filterset to support queries for executable task type attributes."""

    class Meta:
        model = ExecutableTaskType
        fields = ABSTRACT_TASK_TYPE_FIELDS


class TaskQueueFilter(filters.FilterSet):
    """A filterset to support queries for task queue attributes."""

    class Meta:
        model = TaskQueue
        fields = {
            "name": CHAR_FIELD_LOOKUPS,
            "description": CHAR_FIELD_LOOKUPS,
            "user__username": CHAR_FIELD_LOOKUPS,
            "private": BOOLEAN_FIELD_LOOKUPS,
            "runs_executable_tasks": BOOLEAN_FIELD_LOOKUPS,
            "runs_docker_container_tasks": BOOLEAN_FIELD_LOOKUPS,
            "runs_singularity_container_tasks": BOOLEAN_FIELD_LOOKUPS,
            "active": BOOLEAN_FIELD_LOOKUPS,
        }


class TaskWhitelistFilter(filters.FilterSet):
    """A filterset to support queries for task whitelist attributes."""

    class Meta:
        model = TaskWhitelist
        fields = {
            "name": CHAR_FIELD_LOOKUPS,
            "description": CHAR_FIELD_LOOKUPS,
            "user__username": CHAR_FIELD_LOOKUPS,
        }
