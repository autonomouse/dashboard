from django import forms
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.db.models import get_models, get_app
from oilserver import models
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


class PipelineForm(forms.ModelForm):
    buildexecutor = CustomModelChoiceField_Name(
        queryset=models.BuildExecutor.objects.all())

    class Meta:
        model = models.Pipeline
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(PipelineForm, self).__init__(*args, **kwargs)
        add_related_field_wrapper(self, 'buildexecutor')


class PipelineAdmin(admin.ModelAdmin):
    list_display = ['uuid', 'completed_at', 'buildexecutor_name']

    def buildexecutor_name(self, obj):
        try:
            return obj.buildexecutor.name
        except AttributeError:
            return obj.buildexecutor

    search_fields = ['uuid']
    ordering = ['completed_at']
    form = PipelineForm

admin.site.register(models.Pipeline, PipelineAdmin)


class BuildAdmin(admin.ModelAdmin):
    list_display = ['build_id', 'pipeline', 'jobtype']
    search_fields = ['build_id']
    ordering = ['build_id']

admin.site.register(models.Build, BuildAdmin)


class KnownBugRegexAdmin(admin.ModelAdmin):
    list_display = ['regex']

    search_fields = ['regex']
    ordering = ['created_at']

admin.site.register(models.KnownBugRegex, KnownBugRegexAdmin)


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

admin.site.register(models.ProductUnderTest, ProductUnderTestAdmin)


class BugTrackerBugForm(forms.ModelForm):
    project = CustomModelChoiceField_Name(
        queryset=models.Project.objects.all())

    class Meta:
        model = models.BugTrackerBug
        fields = '__all__'

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

admin.site.register(models.BugTrackerBug, BugTrackerBugAdmin)


class BugTrackerBugInline(admin.StackedInline):
    model = models.BugTrackerBug


class KnownBugRegexInline(admin.StackedInline):
    model = models.KnownBugRegex
    extra = 1


class BugForm(forms.ModelForm):
    bugtrackerbug = CustomModelChoiceField_BugNumber(
        queryset=models.BugTrackerBug.objects.all())

    class Meta:
        model = models.Bug
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(BugForm, self).__init__(*args, **kwargs)
        add_related_field_wrapper(self, 'bugtrackerbug')


class BugAdmin(admin.ModelAdmin):
    list_display = ['summary', 'bugtrackerbug_number', 'project_name']
    inlines = [KnownBugRegexInline]

    def bugtrackerbug_number(self, obj):
        try:
            return obj.bugtrackerbug.bug_number
        except AttributeError:
            return obj.bugtrackerbug

    def project_name(self, obj):
        try:
            return obj.bugtrackerbug.project.name
        except AttributeError:
            return obj.bugtrackerbug.project

    search_fields = ['summary']
    ordering = ['summary']
    form = BugForm

admin.site.register(models.Bug, BugAdmin)


class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    ordering = ['name']

admin.site.register(models.Project, ProjectAdmin)


# Register any remaining models that have not been explicitly registered:
for model in get_models(get_app('oilserver')):
    try:
        admin.site.register(model)
    except AlreadyRegistered:
        pass
