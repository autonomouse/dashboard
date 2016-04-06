from django import forms
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.db.models import get_models, get_app
from oilserver.models import (
    ProductUnderTest, Bug, BugTrackerBug, Project, KnownBugRegex)
from django.contrib.admin.sites import AlreadyRegistered
from tastypie.models import ApiKey
from tastypie.admin import ApiKeyInline
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper


def add_related_field_wrapper(form, col_name):
    rel_model = form.Meta.model
    rel = rel_model._meta.get_field(col_name).rel
    form.fields[col_name].widget = RelatedFieldWidgetWrapper(
        form.fields[col_name].widget, rel, admin.site, can_add_related=True)


class CustomModelChoiceField_Name(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name


class CustomModelChoiceField_BugNumber(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.bug_number


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
    list_display = ['name', 'vendor_name', 'project_name']

    def vendor_name(self, obj):
        try:
            return obj.vendor.name
        except AttributeError:
            return obj.vendor

    def project_name(self, obj):
        try:
            return obj.project.name
        except AttributeError:
            return obj.project

    search_fields = ['name']
    ordering = ['name']

admin.site.register(ProductUnderTest, ProductUnderTestAdmin)


class BugTrackerBugForm(forms.ModelForm):
    project = CustomModelChoiceField_Name(
        queryset=Project.objects.all())

    class Meta:
        model = BugTrackerBug

    def __init__(self, *args, **kwargs):
        super(BugTrackerBugForm, self).__init__(*args, **kwargs)
        add_related_field_wrapper(self, 'project')


class BugTrackerBugAdmin(admin.ModelAdmin):
    list_display = ['bug_number', 'project_name']

    def project_name(self, obj):
        try:
            return obj.project.name
        except AttributeError:
            return obj.project

    search_fields = ['bug_number']
    ordering = ['bug_number']
    form = BugTrackerBugForm

admin.site.register(BugTrackerBug, BugTrackerBugAdmin)


class BugTrackerBugInline(admin.StackedInline):
    model = BugTrackerBug


class KnownBugRegexInline(admin.StackedInline):
    model = KnownBugRegex
    extra = 1


class BugForm(forms.ModelForm):
    bugtrackerbug = CustomModelChoiceField_BugNumber(
        queryset=BugTrackerBug.objects.all())

    class Meta:
        model = Bug

    def __init__(self, *args, **kwargs):
        super(BugForm, self).__init__(*args, **kwargs)
        add_related_field_wrapper(self, 'bugtrackerbug')


class BugAdmin(admin.ModelAdmin):
    list_display = ['summary', 'bugtrackerbug_number']
    inlines = [KnownBugRegexInline]

    def bugtrackerbug_number(self, obj):
        try:
            return obj.bugtrackerbug.bug_number
        except AttributeError:
            return obj.bugtrackerbug

    search_fields = ['summary']
    ordering = ['summary']
    form = BugForm

admin.site.register(Bug, BugAdmin)


# Register any remaining models that have not been explicitly registered:
for model in get_models(get_app('oilserver')):
    try:
        admin.site.register(model)
    except AlreadyRegistered:
        pass
