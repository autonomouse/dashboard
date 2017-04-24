from tastypie.exceptions import Unauthorized
from tastypie.authorization import DjangoAuthorization
from django.contrib.auth.models import User


class WorldReadableDjangoAuthorization(DjangoAuthorization):
    """Allow all authenticated users to read from the API endpoints"""
    def is_staff_check(self, bundle):
        username = bundle.request.user
        user = User.objects.get(username=username)
        if not (user.is_staff or user.is_superuser):
            raise Unauthorized("You are not allowed to access that resource.")

    def read_list(self, object_list, bundle):
        self.is_staff_check(bundle)

        if self.base_checks(bundle.request, object_list.model) is False:
            return []

        # GET-style methods are always allowed.
        return object_list

    def read_detail(self, object_list, bundle):
        self.is_staff_check(bundle)

        if self.base_checks(bundle.request, bundle.obj.__class__) is False:
            raise Unauthorized("You are not allowed to access that resource.")

        # GET-style methods are always allowed.
        return True
