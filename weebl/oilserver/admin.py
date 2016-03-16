from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.db.models import get_models, get_app
from oilserver.models import ProductUnderTest
from django.contrib.admin.sites import AlreadyRegistered
from tastypie.models import ApiKey
from tastypie.admin import ApiKeyInline


class UserModelAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff',
                    'is_superuser']
    inlines = UserAdmin.inlines + [ApiKeyInline]

admin.site.unregister(User)
admin.site.register(User, UserModelAdmin)


class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ['user', 'key']

admin.site.unregister(ApiKey)
admin.site.register(ApiKey, ApiKeyAdmin)


class ProductUnderTestAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_vendor_name', 'get_project_name']

    def get_vendor_name(self, obj):
        try:
            return obj.vendor.name
        except AttributeError:
            return obj.vendor

    def get_project_name(self, obj):
        try:
            return obj.project.name
        except AttributeError:
            return obj.project

    search_fields = ['name']
    ordering = ['name']

admin.site.register(ProductUnderTest, ProductUnderTestAdmin)


# Register any remaining models that have not been explicitly registered:
for model in get_models(get_app('oilserver')):
    try:
        admin.site.register(model)
    except AlreadyRegistered:
        pass
