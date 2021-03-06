"""Contains view(sets) related to tasks."""

from celery.result import AsyncResult
from django.core.exceptions import ObjectDoesNotExist
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, serializers, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_202_ACCEPTED,
    HTTP_400_BAD_REQUEST,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from tasksapi.filters import (
    ContainerTaskInstanceFilter,
    ContainerTaskTypeFilter,
    ExecutableTaskInstanceFilter,
    ExecutableTaskTypeFilter,
    TaskQueueFilter,
    TaskWhitelistFilter,
    UserFilter,
)
from tasksapi.models import (
    ContainerTaskInstance,
    ContainerTaskType,
    ExecutableTaskInstance,
    ExecutableTaskType,
    TaskQueue,
    TaskWhitelist,
    User,
)
from tasksapi.paginators import SmallResultsSetPagination
from tasksapi.permissions import IsAdminOrOwnerThenWriteElseReadOnly
from tasksapi.serializers import (
    ContainerTaskInstanceSerializer,
    ContainerTaskTypeSerializer,
    ExecutableTaskInstanceSerializer,
    ExecutableTaskTypeSerializer,
    TaskInstanceStateUpdateRequestSerializer,
    TaskInstanceStateUpdateResponseSerializer,
    TaskQueueSerializer,
    TaskWhitelistSerializer,
    UserSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    """A viewset for users."""

    queryset = User.objects.all().order_by("username")
    serializer_class = UserSerializer
    lookup_field = "username"
    http_method_names = ["get"]
    filter_class = UserFilter


class UserInjectedModelViewSet(viewsets.ModelViewSet):
    """Subclass this for a ModelViewSet with an injected user attribute.

    Injected means that the user as determined by the request's
    authentication header will be sent to the viewset's serializer (cf.
    specified explicitly in the request body) for instance creation
    requests.
    """

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ContainerTaskInstanceViewSet(UserInjectedModelViewSet):
    """A viewset for container task instances."""

    queryset = ContainerTaskInstance.objects.all()
    serializer_class = ContainerTaskInstanceSerializer
    pagination_class = SmallResultsSetPagination
    lookup_field = "uuid"
    http_method_names = ["get", "post"]
    filter_class = ContainerTaskInstanceFilter

    @swagger_auto_schema(
        method="post",
        request_body=serializers.Serializer,
        responses={HTTP_201_CREATED: ContainerTaskInstanceSerializer},
    )
    @action(methods=["post"], detail=True)
    def clone(self, request, uuid):
        """Clone a job with the same arguments, task type, and task queue."""
        # Get the instance to be cloned
        instance_to_clone = ContainerTaskInstance.objects.get(uuid=uuid)

        # Build the new instance
        cloned_instance = ContainerTaskInstance.objects.create(
            name=instance_to_clone.name,
            user=request.user,
            task_type=instance_to_clone.task_type,
            task_queue=instance_to_clone.task_queue,
            arguments=instance_to_clone.arguments,
        )

        # Serialize the new instance and return it in the response
        serialized_instance = ContainerTaskInstanceSerializer(cloned_instance)

        return Response(serialized_instance.data, status=HTTP_201_CREATED)

    @swagger_auto_schema(
        method="post",
        request_body=serializers.Serializer,
        responses={HTTP_202_ACCEPTED: ContainerTaskInstanceSerializer},
    )
    @action(methods=["post"], detail=True)
    def terminate(self, request, uuid):
        """Send a terminate signal to a job."""
        # Terminate the job
        AsyncResult(uuid).revoke(terminate=True)

        # Post the object back as the response
        this_instance = ContainerTaskInstance.objects.get(uuid=uuid)
        serialized_instance = ContainerTaskInstanceSerializer(this_instance)
        return Response(serialized_instance.data, status=HTTP_202_ACCEPTED)


@permission_classes((IsAdminOrOwnerThenWriteElseReadOnly,))
class ContainerTaskTypeViewSet(UserInjectedModelViewSet):
    """A viewset for container task types."""

    queryset = ContainerTaskType.objects.all()
    serializer_class = ContainerTaskTypeSerializer
    http_method_names = ["get", "post", "put"]
    filter_class = ContainerTaskTypeFilter


class ExecutableTaskInstanceViewSet(UserInjectedModelViewSet):
    """A viewset for executable task instances."""

    queryset = ExecutableTaskInstance.objects.all()
    serializer_class = ExecutableTaskInstanceSerializer
    pagination_class = SmallResultsSetPagination
    lookup_field = "uuid"
    http_method_names = ["get", "post"]
    filter_class = ExecutableTaskInstanceFilter

    @swagger_auto_schema(
        method="post",
        request_body=serializers.Serializer,
        responses={HTTP_201_CREATED: ExecutableTaskInstanceSerializer},
    )
    @action(methods=["post"], detail=True)
    def clone(self, request, uuid):
        """Clone a job with the same arguments, task type, and task queue."""
        # Get the instance to be cloned
        instance_to_clone = ExecutableTaskInstance.objects.get(uuid=uuid)

        # Build the new instance
        cloned_instance = ExecutableTaskInstance.objects.create(
            name=instance_to_clone.name,
            user=request.user,
            task_type=instance_to_clone.task_type,
            task_queue=instance_to_clone.task_queue,
            arguments=instance_to_clone.arguments,
        )

        # Serialize the new instance and return it in the response
        serialized_instance = ExecutableTaskInstanceSerializer(cloned_instance)

        return Response(serialized_instance.data, status=HTTP_201_CREATED)

    @swagger_auto_schema(
        method="post",
        request_body=serializers.Serializer,
        responses={HTTP_202_ACCEPTED: ExecutableTaskInstanceSerializer},
    )
    @action(methods=["post"], detail=True)
    def terminate(self, request, uuid):
        """Send a terminate signal to a job."""
        # Terminate the job
        AsyncResult(uuid).revoke(terminate=True)

        # Post the object back as the response
        this_instance = ExecutableTaskInstance.objects.get(uuid=uuid)
        serialized_instance = ExecutableTaskInstanceSerializer(this_instance)
        return Response(serialized_instance.data, status=HTTP_202_ACCEPTED)


@permission_classes((IsAdminOrOwnerThenWriteElseReadOnly,))
class ExecutableTaskTypeViewSet(UserInjectedModelViewSet):
    """A viewset for executable task types."""

    queryset = ExecutableTaskType.objects.all()
    serializer_class = ExecutableTaskTypeSerializer
    http_method_names = ["get", "post", "put"]
    filter_class = ExecutableTaskTypeFilter


@permission_classes((IsAdminOrOwnerThenWriteElseReadOnly,))
class TaskQueueViewSet(UserInjectedModelViewSet):
    """A viewset for task queues."""

    queryset = TaskQueue.objects.all()
    serializer_class = TaskQueueSerializer
    http_method_names = ["get", "post", "patch", "put"]
    filter_class = TaskQueueFilter


@permission_classes((IsAdminOrOwnerThenWriteElseReadOnly,))
class TaskWhitelistViewSet(UserInjectedModelViewSet):
    """A viewset for task queues."""

    queryset = TaskWhitelist.objects.all()
    serializer_class = TaskWhitelistSerializer
    http_method_names = ["get", "post", "patch", "put"]
    filter_class = TaskWhitelistFilter


class TokenObtainPairPermissiveView(TokenObtainPairView):
    """Always make sure that users can obtain JWT tokens."""

    # Inherit the more useful docstring (shown in the API reference)
    # from the parent
    __doc__ = TokenObtainPairView.__doc__

    permission_classes = (permissions.AllowAny,)

    @swagger_auto_schema(security=[])
    def post(self, request, *args, **kwargs):
        # Make sure drg-yasg knows this doesn't require auth headers.
        return super().post(request, *args, **kwargs)


class TokenRefreshPermissiveView(TokenRefreshView):
    """Always make sure that users can obtain JWT tokens."""

    # Inherit the more useful docstring (shown in the API reference)
    # from the parent
    __doc__ = TokenRefreshView.__doc__

    permission_classes = (permissions.AllowAny,)

    @swagger_auto_schema(security=[])
    def post(self, request, *args, **kwargs):
        # Make sure drg-yasg knows this doesn't require auth headers.
        return super().post(request, *args, **kwargs)


@swagger_auto_schema(
    method="patch",
    request_body=TaskInstanceStateUpdateRequestSerializer,
    responses={HTTP_200_OK: TaskInstanceStateUpdateResponseSerializer},
)
@api_view(["PATCH"])
def update_task_instance_status(request, uuid):
    """Updates the status for task instances of any class of task."""
    # Find the instance we need to update
    state = request.data["state"]

    try:
        # Try finding a container task instance first
        instance = ContainerTaskInstance.objects.get(uuid=uuid)
        instance.state = state
        instance.save()

        serialized_instance = TaskInstanceStateUpdateResponseSerializer(
            instance
        )

        return Response(serialized_instance.data, status=HTTP_200_OK)
    except ObjectDoesNotExist:
        # Not a container task instance
        pass

    # Now try finding an executable task instance
    try:
        instance = ExecutableTaskInstance.objects.get(uuid=uuid)
        instance.state = state
        instance.save()

        serialized_instance = TaskInstanceStateUpdateResponseSerializer(
            instance
        )

        return Response(serialized_instance.data, status=HTTP_200_OK)
    except ObjectDoesNotExist:
        # Not a container task instance
        pass

    # Bad request :(
    return Response(
        "No task instance with UUID {} found".format(uuid),
        status=HTTP_400_BAD_REQUEST,
    )
