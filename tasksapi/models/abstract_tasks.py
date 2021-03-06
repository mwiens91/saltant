"""Models to represent abstract task types and instances.

Other task type and task instance models should inherit from these.
"""

import json
from uuid import uuid4
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ValidationError
from django.db import models
from tasksapi.constants import (
    CREATED,
    STATE_CHOICES,
    STATE_MAX_LENGTH,
    EXECUTABLE_TASK,
    DOCKER,
    SINGULARITY,
)
from .task_queues import TaskQueue
from .users import User
from .utils import determine_task_class
from .validators import task_instance_args_are_valid, task_type_args_are_valid


class AbstractTaskType(models.Model):
    """A type of task to create instances with."""

    name = models.CharField(
        max_length=200, unique=True, help_text="The name of the task."
    )
    description = models.TextField(
        blank=True, help_text="A description of the task."
    )
    user = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
        help_text="The author of this task.",
    )

    # The datetime the task type was created. This will be automatically
    # set upon creation of a task type and is *not* editable. See
    # https://docs.djangoproject.com/en/2.0/ref/models/fields/#django.db.models.DateField.auto_now_add
    # for more details.
    datetime_created = models.DateTimeField(auto_now_add=True)

    command_to_run = models.CharField(
        max_length=400,
        help_text=(
            "The command to run to execute the task. For example, "
            '"python /app/myscript.py". Note that shell operators '
            "will *not* be parsed; for example, | and &&. "
            "Arguments will be appended to the end of the command."
        ),
    )

    # Required environment variables
    environment_variables = JSONField(
        blank=True,
        default=list,
        help_text=(
            "A JSON array of environment variables to consume from "
            "the Celery worker's environment. Defaults to []. Note "
            "that all task instances have their job UUID available "
            "in the environment variable JOB_UUID."
        ),
    )

    # Required arguments
    required_arguments = JSONField(
        blank=True,
        default=list,
        help_text="A JSON array of required argument names. Defaults to [].",
    )

    # Default required argument values encoded as a dictionary. This
    # dictionary must be a subset of the required arguments, which is
    # validated when saving task types.
    required_arguments_default_values = JSONField(
        blank=True,
        default=dict,
        help_text=(
            "A JSON dictionary of default values for required "
            "arguments, where the keys are the argument names and "
            "the values are their corresponding default values. "
            "Defaults to {}."
        ),
    )

    class Meta:
        # Don't make an actual database table for this. Note that this
        # gets set to False when the model is inherited.
        abstract = True

        # Ordering
        ordering = ["id"]

    def __str__(self):
        """String representation of a task type."""
        return self.name

    def save(self, *args, **kwargs):  # pylint: disable=arguments-differ
        # Call clean
        self.clean()

        # Call the parent save method
        super().save(*args, **kwargs)

    def clean(self):
        """Validate a task type's required arguments."""
        # Set null JSON values to empty Python data structures
        if self.environment_variables is None:
            self.environment_variables = []

        if self.required_arguments is None:
            self.required_arguments = []

        if self.required_arguments_default_values is None:
            self.required_arguments_default_values = {}

        # If JSON was passed in as a string, try to interpret it as JSON
        if isinstance(self.environment_variables, str):
            try:
                self.environment_variables = json.loads(
                    self.environment_variables
                )
            except json.JSONDecodeError:
                raise ValidationError(
                    "'%s' is not valid JSON!" % self.environment_variables
                )

        if isinstance(self.required_arguments, str):
            try:
                self.required_arguments = json.loads(self.required_arguments)
            except json.JSONDecodeError:
                raise ValidationError(
                    "'%s' is not valid JSON!" % self.required_arguments
                )

        if isinstance(self.required_arguments_default_values, str):
            try:
                self.required_arguments_default_values = json.loads(
                    self.required_arguments_default_values
                )
            except json.JSONDecodeError:
                raise ValidationError(
                    "'%s' is not valid JSON!"
                    % self.required_arguments_default_values
                )

        # Make sure that JSON dicts are dicts and JSON arrays are lists
        if not isinstance(self.environment_variables, list):
            raise ValidationError(
                "'%s' is not a valid JSON array!" % self.environment_variables
            )

        if not isinstance(self.required_arguments, list):
            raise ValidationError(
                "'%s' is not a valid JSON array!" % self.required_arguments
            )

        if not isinstance(self.required_arguments_default_values, dict):
            raise ValidationError(
                "'%s' is not a valid JSON dictionary!"
                % self.required_arguments_default_values
            )

        # Make sure arguments are valid
        is_valid, reason = task_type_args_are_valid(self)

        # Arguments are not valid!
        if not is_valid:
            raise ValidationError(reason)


class AbstractTaskInstance(models.Model):
    """A running instance of a task type.

    Make sure you define a foreign key to the appropriate task type when
    you subclass this!
    """

    name = models.CharField(
        max_length=200,
        blank=True,
        help_text="An optional non-unique name for the task instance.",
    )
    uuid = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        verbose_name="UUID",
        help_text="The UUID for the running job.",
    )
    state = models.CharField(
        max_length=STATE_MAX_LENGTH, choices=STATE_CHOICES, default=CREATED
    )
    user = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
        help_text="The author of this instance.",
    )
    task_queue = models.ForeignKey(
        TaskQueue,
        on_delete=models.CASCADE,
        help_text="The queue this instance runs on.",
    )
    datetime_created = models.DateTimeField(
        auto_now_add=True, help_text="When the job was created."
    )
    datetime_finished = models.DateTimeField(
        null=True, editable=False, help_text="When the job finished."
    )

    # Arguments encoded as a dictionary. The arguments pass in must
    # contain all of the required arguments of the task type for which
    # there don't exist default arguments.
    arguments = JSONField(
        blank=True,
        default=dict,
        help_text=(
            "A JSON dictionary of arguments, where the keys are the "
            "argument names and the values are their corresponding "
            "values. A task instance must specify values for all "
            "values of a task type's required arguments for which "
            "no default value exists. Defaults to {}."
        ),
    )

    class Meta:
        """Model metadata."""

        # Don't make an actual database table for this. Note that this
        # gets set to False when the model is inherited.
        abstract = True

        # Order with respect to most recently created
        ordering = ["-datetime_created"]

    def __str__(self):
        """String representation of a task instance."""
        return str(self.uuid)

    def save(self, *args, **kwargs):  # pylint: disable=arguments-differ
        """Perform additonal validation."""
        # Call clean
        self.clean(fill_in_missing_args=True)

        # Call the parent save method
        super().save(*args, **kwargs)

    def clean(
        self, fill_in_missing_args=False
    ):  # pylint: disable=arguments-differ
        """Validate an instance's arguments."""
        # Set null JSON values to empty Python data structures
        if self.arguments is None:
            self.arguments = {}

        # If JSON was passed in as a string, try to interpret it as JSON
        if isinstance(self.arguments, str):
            try:
                self.arguments = json.loads(self.arguments)
            except json.JSONDecodeError:
                raise ValidationError("%s is not valid JSON!" % self.arguments)

        # Make sure the arguments JSON passed in is a dictionary
        if not isinstance(self.arguments, dict):
            raise ValidationError(
                "'%s' is not a valid JSON dictionary!" % self.arguments
            )

        # Make sure the queue is active
        if not self.task_queue.active:
            raise ValidationError(
                "Queue %s is not active" % self.task_queue.name
            )

        # Make sure the user is authorized to use the queue they're
        # posting to
        if self.task_queue.private and self.user != self.task_queue.user:
            raise ValidationError(
                "%s is not authorized to use the queue %s"
                % (self.user, self.task_queue.name)
            )

        # Determine task class for queue validation
        this_task_class = determine_task_class(self)

        # Make sure this task type is on one of the queue's whitelists
        if this_task_class == EXECUTABLE_TASK:
            if not self.task_queue.whitelists.filter(
                whitelisted_executable_task_types=self.task_type
            ):
                raise ValidationError(
                    "Queue %s has not whitelisted task type %s"
                    % (self.task_queue.name, self.task_type.name)
                )
        else:
            if not self.task_queue.whitelists.filter(
                whitelisted_container_task_types=self.task_type
            ):
                raise ValidationError(
                    "Queue %s has not whitelisted task type %s"
                    % (self.task_queue.name, self.task_type.name)
                )

        # Make sure the queue accepts the type of task they're posting
        # to
        if this_task_class == EXECUTABLE_TASK:
            if not self.task_queue.runs_executable_tasks:
                raise ValidationError(
                    "Queue %s does not accept executable tasks"
                    % self.task_queue.name
                )
        else:
            if (
                self.task_type.container_type == DOCKER
                and not self.task_queue.runs_docker_container_tasks
            ):
                raise ValidationError(
                    "Queue %s does not accept Docker container tasks"
                    % self.task_queue.name
                )
            elif (
                self.task_type.container_type == SINGULARITY
                and not self.task_queue.runs_singularity_container_tasks
            ):
                raise ValidationError(
                    "Queue %s does not accept Singularity container tasks"
                    % self.task_queue.name
                )

        # Make sure arguments are valid
        is_valid, reason = task_instance_args_are_valid(
            instance=self, fill_missing_args=fill_in_missing_args
        )

        # Arguments are not valid!
        if not is_valid:
            raise ValidationError(reason)
