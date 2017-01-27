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


class DefaultAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    ordering = ['name']


# Register models with default settings:
admin.site.register(models.Project, DefaultAdmin)
admin.site.register(models.Vendor, DefaultAdmin)
admin.site.register(models.BuildExecutor, DefaultAdmin)
admin.site.register(models.Charm, DefaultAdmin)
admin.site.register(models.InternalContact, DefaultAdmin)
admin.site.register(models.JujuService, DefaultAdmin)
admin.site.register(models.ProductType, DefaultAdmin)
admin.site.register(models.Report, DefaultAdmin)


# Register models with custom settings:
def add_related_field_wrapper(form, col_name):
    rel_model = form.Meta.model
    rel = rel_model._meta.get_field(col_name).rel
    form.fields[col_name].widget = RelatedFieldWidgetWrapper(
        form.fields[col_name].widget, rel, admin.site, can_add_related=True)


def get_obj_attribute(obj, field, *args):
    attr = None
    for arg in args:
        try:
            attr = getattr(obj, arg)
            if arg == args[-1]:
                return getattr(attr, field)
        except AttributeError:
            return attr


class CustomModelChoiceFieldName(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name


class CustomModelChoiceFieldBugNumber(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.bug_number


class CustomModelChoiceFieldHostname(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.hostname


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
    buildexecutor = CustomModelChoiceFieldName(
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
        return get_obj_attribute(obj, 'name', 'buildexecutor')

    search_fields = ['uuid']
    ordering = ['completed_at']
    form = PipelineForm

admin.site.register(models.Pipeline, PipelineAdmin)


class BuildAdmin(admin.ModelAdmin):
    list_display = ['build_id', 'pipeline', 'jobtype']
    search_fields = ['build_id']
    ordering = ['build_id']

admin.site.register(models.Build, BuildAdmin)


class ProductUnderTestForm(forms.ModelForm):
    project = CustomModelChoiceFieldName(
        queryset=models.Project.objects.all())
    vendor = CustomModelChoiceFieldName(
        queryset=models.Vendor.objects.all())
    internalcontact = CustomModelChoiceFieldName(
        queryset=models.InternalContact.objects.all())
    producttype = CustomModelChoiceFieldName(
        queryset=models.ProductType.objects.all())

    class Meta:
        model = models.ProductUnderTest
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ProductUnderTestForm, self).__init__(*args, **kwargs)
        add_related_field_wrapper(self, 'vendor')
        add_related_field_wrapper(self, 'project')
        add_related_field_wrapper(self, 'internalcontact')
        add_related_field_wrapper(self, 'producttype')


class ProductUnderTestAdmin(admin.ModelAdmin):
    list_display = ['name', 'vendor_name', 'project_name']

    def vendor_name(self, obj):
        return get_obj_attribute(obj, 'name', 'vendor')

    def project_name(self, obj):
        return get_obj_attribute(obj, 'name', 'project')

    search_fields = ['name']
    ordering = ['name']
    form = ProductUnderTestForm

admin.site.register(models.ProductUnderTest, ProductUnderTestAdmin)


class BugTrackerBugForm(forms.ModelForm):
    project = CustomModelChoiceFieldName(
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
        return get_obj_attribute(obj, 'name', 'project')

    search_fields = ['bug_number']
    ordering = ['bug_number']
    form = BugTrackerBugForm

admin.site.register(models.BugTrackerBug, BugTrackerBugAdmin)


class BugTrackerBugInline(admin.StackedInline):
    model = models.BugTrackerBug


class KnownBugRegexAdmin(admin.ModelAdmin):
    list_display = ['regex']
    search_fields = ['regex']
    ordering = ['created_at']

admin.site.register(models.KnownBugRegex, KnownBugRegexAdmin)


class KnownBugRegexInline(admin.StackedInline):
    model = models.KnownBugRegex
    extra = 0


class BugForm(forms.ModelForm):
    bugtrackerbug = CustomModelChoiceFieldBugNumber(
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
        return get_obj_attribute(obj, 'bug_number', 'bugtrackerbug')

    def project_name(self, obj):
        return get_obj_attribute(obj, 'name', 'bugtrackerbug', 'project')

    search_fields = ['summary', 'uuid']
    ordering = ['summary']
    form = BugForm

admin.site.register(models.Bug, BugAdmin)


class MachineAdmin(admin.ModelAdmin):
    list_display = ['hostname']
    search_fields = ['hostname']
    ordering = ['hostname']

admin.site.register(models.Machine, MachineAdmin)


class MachineConfigurationForm(forms.ModelForm):
    machine = CustomModelChoiceFieldHostname(
        queryset=models.Machine.objects.all())

    class Meta:
        model = models.MachineConfiguration
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(MachineConfigurationForm, self).__init__(*args, **kwargs)
        add_related_field_wrapper(self, 'machine')


class MachineConfigurationAdmin(admin.ModelAdmin):
    list_display = ['uuid', 'machine_name']

    def machine_name(self, obj):
        try:
            return obj.machine.hostname
        except AttributeError:
            return obj.machine

    search_fields = ['uuid']
    ordering = ['uuid']
    form = MachineConfigurationForm

admin.site.register(models.MachineConfiguration, MachineConfigurationAdmin)


class TestFrameworkForm(forms.ModelForm):

    class Meta:
        model = models.TestFramework
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(TestFrameworkForm, self).__init__(*args, **kwargs)

class TestFrameworkAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'name', 'version']

    search_fields = ['name', 'version']
    ordering = ['name', 'version']
    form = TestFrameworkForm

admin.site.register(models.TestFramework, TestFrameworkAdmin)


# Register any remaining models that have not been explicitly registered:
for model in get_models(get_app('oilserver')):
    try:
        admin.site.register(model)
    except AlreadyRegistered:
        pass
