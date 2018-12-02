"""Views for task instances."""

from celery.result import AsyncResult
from datetime import date, timedelta
import json
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from tasksapi.constants import CONTAINER_TASK, EXECUTABLE_TASK
from tasksapi.models import ContainerTaskInstance, ExecutableTaskInstance
from .mixins import (
    SetContainerTaskClassCookieMixin,
    SetExecutableTaskClassCookieMixin,
)
from .stats_utils import get_job_state_data


class BaseTaskInstanceList(
    SetContainerTaskClassCookieMixin, LoginRequiredMixin, ListView
):
    """A base view for listing task instances."""

    context_object_name = "taskinstance_list"
    task_class = "define me"

    def get_context_data(self, **kwargs):
        """Get some stats for the task instances."""
        context = super().get_context_data(**kwargs)

        # Get data for Chart.js
        today = date.today()
        last_week_date = date.today() - timedelta(days=7)
        chart_data = get_job_state_data(
            task_class=self.task_class,
            start_date=last_week_date,
            end_date=today,
        )

        # Add the Charts.js stuff to our context
        context["labels"] = json.dumps(chart_data["labels"])
        context["datasets"] = json.dumps(chart_data["datasets"])

        return context


class BaseTaskInstanceTerminate(LoginRequiredMixin, DetailView):
    """A base view for terminating task instances."""

    pk_url_kwarg = "uuid"
    context_object_name = "taskinstance"
    template_name = "frontend/base_taskinstance_terminate.html"

    def post(self, request, *args, **kwargs):
        # This will hang unless you have a Celery hooked up and running
        AsyncResult(self.get_object().uuid).revoke(terminate=True)
        return HttpResponseRedirect(self.get_success_url())


class ContainerTaskInstanceList(BaseTaskInstanceList):
    """A view for listing container task instances."""

    model = ContainerTaskInstance
    task_class = CONTAINER_TASK
    template_name = "frontend/containertaskinstance_list.html"


class ContainerTaskInstanceDetail(LoginRequiredMixin, DetailView):
    """A view for a specific container task instance."""

    model = ContainerTaskInstance
    pk_url_kwarg = "uuid"
    context_object_name = "taskinstance"
    template_name = "frontend/containertaskinstance_detail.html"


class ContainerTaskInstanceRename(LoginRequiredMixin, UpdateView):
    """A view for renaming a container task instance."""

    model = ContainerTaskInstance
    pk_url_kwarg = "uuid"
    fields = ("name",)
    template_name = "frontend/base_taskinstance_rename.html"

    def get_success_url(self):
        """Redirect to detail page."""
        return reverse_lazy(
            "containertaskinstance-detail", kwargs={"uuid": self.object.uuid}
        )


class ContainerTaskInstanceStateUpdate(LoginRequiredMixin, UpdateView):
    """A view for overriding container task instance state."""

    model = ContainerTaskInstance
    pk_url_kwarg = "uuid"
    fields = ("state",)
    template_name = "frontend/base_taskinstance_stateupdate.html"

    def get_success_url(self):
        """Redirect to detail page."""
        return reverse_lazy(
            "containertaskinstance-detail", kwargs={"uuid": self.object.uuid}
        )


class ContainerTaskInstanceTerminate(BaseTaskInstanceTerminate):
    """A view for terminating container task instances."""

    model = ContainerTaskInstance

    def get_success_url(self):
        """Redirect to detail page."""
        return reverse_lazy(
            "containertaskinstance-detail",
            kwargs={"uuid": self.get_object().uuid},
        )


class ContainerTaskInstanceDelete(LoginRequiredMixin, DeleteView):
    """A view for deleting a container task instance."""

    model = ContainerTaskInstance
    pk_url_kwarg = "uuid"
    context_object_name = "taskinstance"
    template_name = "frontend/base_taskinstance_delete.html"
    success_url = reverse_lazy("containertaskinstance-list")


class ExecutableTaskInstanceList(BaseTaskInstanceList):
    """A view for listing executable task instance."""

    model = ExecutableTaskInstance
    task_class = EXECUTABLE_TASK
    template_name = "frontend/executabletaskinstance_list.html"


class ExecutableTaskInstanceCreate(LoginRequiredMixin, CreateView):
    """A view for creating an executable task instance."""

    model = ExecutableTaskInstance
    fields = "__all__"
    template_name = "frontend/base_taskinstance_create.html"

    def get_success_url(self):
        """Redirect to queue detail page."""
        return reverse_lazy(
            "executabletaskinstance-detail", kwargs={"uuid": self.object.uuid}
        )


class ExecutableTaskInstanceDetail(LoginRequiredMixin, DetailView):
    """A view for a specific executable task instance."""

    model = ExecutableTaskInstance
    pk_url_kwarg = "uuid"
    context_object_name = "taskinstance"
    template_name = "frontend/executabletaskinstance_detail.html"


class ExecutableTaskInstanceRename(LoginRequiredMixin, UpdateView):
    """A view for renaming an executable task instance."""

    model = ExecutableTaskInstance
    pk_url_kwarg = "uuid"
    fields = ("name",)
    template_name = "frontend/base_taskinstance_rename.html"

    def get_success_url(self):
        """Redirect to detail page."""
        return reverse_lazy(
            "executabletaskinstance-detail", kwargs={"uuid": self.object.uuid}
        )


class ExecutableTaskInstanceStateUpdate(LoginRequiredMixin, UpdateView):
    """A view for overriding executable task instance state."""

    model = ExecutableTaskInstance
    pk_url_kwarg = "uuid"
    fields = ("state",)
    template_name = "frontend/base_taskinstance_stateupdate.html"

    def get_success_url(self):
        """Redirect to detail page."""
        return reverse_lazy(
            "executabletaskinstance-detail", kwargs={"uuid": self.object.uuid}
        )


class ExecutableTaskInstanceTerminate(BaseTaskInstanceTerminate):
    """A view for terminating executable task instances."""

    model = ExecutableTaskInstance

    def get_success_url(self):
        """Redirect to detail page."""
        return reverse_lazy(
            "executabletaskinstance-detail",
            kwargs={"uuid": self.get_object().uuid},
        )


class ExecutableTaskInstanceDelete(LoginRequiredMixin, DeleteView):
    """A view for deleting an executable task instance."""

    model = ExecutableTaskInstance
    pk_url_kwarg = "uuid"
    context_object_name = "taskinstance"
    template_name = "frontend/base_taskinstance_delete.html"
    success_url = reverse_lazy("executabletaskinstance-list")
