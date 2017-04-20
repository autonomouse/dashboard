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


class CustomModelChoiceField(forms.ModelChoiceField):
    def __init__(self, *args, **kwargs):
        self.field_to_return = kwargs.pop('field_to_return')
        super(CustomModelChoiceField, self).__init__(*args, **kwargs)

    def label_from_instance(self, obj):
        # The following allows to both 'obj.name' and 'obj.relatedobj.name':
        for lvl in self.field_to_return.split('.'):
            obj = getattr(obj, lvl)
        return obj


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
    buildexecutor = CustomModelChoiceField(
        field_to_return='name', queryset=models.BuildExecutor.objects.all())

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
    project = CustomModelChoiceField(
        field_to_return='name', queryset=models.Project.objects.all(),
        required=False)
    vendor = CustomModelChoiceField(
        field_to_return='name', queryset=models.Vendor.objects.all(),
        required=False)
    internalcontact = CustomModelChoiceField(
        field_to_return='name', queryset=models.InternalContact.objects.all(),
        required=False)
    producttype = CustomModelChoiceField(
        field_to_return='name', queryset=models.ProductType.objects.all(),
        required=False)

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
    project = CustomModelChoiceField(
        field_to_return='name', queryset=models.Project.objects.all())

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
    bugtrackerbug = CustomModelChoiceField(
        field_to_return='bug_number',
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
    machine = CustomModelChoiceField(
        field_to_return='hostname', queryset=models.Machine.objects.all())

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


class JujuServiceDeploymentForm(forms.ModelForm):
    pipeline = CustomModelChoiceField(
        field_to_return='uuid', queryset=models.Pipeline.objects.all())
    productundertest = CustomModelChoiceField(
        field_to_return='name', queryset=models.ProductUnderTest.objects.all())
    charm = CustomModelChoiceField(
        field_to_return='name', queryset=models.Charm.objects.all())
    jujuservice = CustomModelChoiceField(
        field_to_return='name', queryset=models.JujuService.objects.all())

    class Meta:
        model = models.JujuServiceDeployment
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(JujuServiceDeploymentForm, self).__init__(*args, **kwargs)
        add_related_field_wrapper(self, 'pipeline')
        add_related_field_wrapper(self, 'productundertest')
        add_related_field_wrapper(self, 'charm')
        add_related_field_wrapper(self, 'jujuservice')


class JujuServiceDeploymentAdmin(admin.ModelAdmin):
    list_display = ['uuid', 'pipeline_uuid', 'productundertest_uuid',
                    'charm_uuid', 'jujuservice_name']

    def pipeline_uuid(self, obj):
        return get_obj_attribute(obj, 'uuid', 'pipeline')

    def productundertest_uuid(self, obj):
        return get_obj_attribute(obj, 'name', 'productundertest')

    def charm_uuid(self, obj):
        return get_obj_attribute(obj, 'name', 'charm')

    def jujuservice_name(self, obj):
        return get_obj_attribute(obj, 'name', 'jujuservice')

    search_fields = ['uuid']
    form = JujuServiceDeploymentForm

admin.site.register(models.JujuServiceDeployment, JujuServiceDeploymentAdmin)


class JenkinsAdmin(admin.ModelAdmin):
    list_display = ['internal_access_url', 'external_access_url']

    search_fields = ['internal_access_url', 'external_access_url']
    ordering = ['internal_access_url', 'external_access_url']

admin.site.register(models.Jenkins, JenkinsAdmin)


class SolutionTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'show', 'colour']
    search_fields = ['name']

admin.site.register(models.SolutionTag, SolutionTagAdmin)


class ReportAdmin(admin.ModelAdmin):
    list_display = ['name', 'uuid']
    search_fields = ['name', 'uuid']


admin.site.register(models.Report, ReportAdmin)


class ReportPeriodAdmin(admin.ModelAdmin):
    list_display = ['name', 'uuid', 'start_date', 'end_date']
    search_fields = ['name', 'uuid']


admin.site.register(models.ReportPeriod, ReportPeriodAdmin)


class ReportInstanceForm(forms.ModelForm):
    report = CustomModelChoiceField(
        field_to_return='name', queryset=models.Report.objects.all())
    reportperiod = CustomModelChoiceField(
        field_to_return='name', queryset=models.ReportPeriod.objects.all())

    class Meta:
        model = models.ReportInstance
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ReportInstanceForm, self).__init__(*args, **kwargs)
        add_related_field_wrapper(self, 'report')
        add_related_field_wrapper(self, 'reportperiod')


class ReportInstanceAdmin(admin.ModelAdmin):
    list_display = ['report_name', 'reportperiod_name', 'uuid']

    def report_name(self, obj):
        return get_obj_attribute(obj, 'name', 'report')

    def reportperiod_name(self, obj):
        return get_obj_attribute(obj, 'name', 'reportperiod')

    search_fields = ['uuid']
    form = ReportInstanceForm


admin.site.register(models.ReportInstance, ReportInstanceAdmin)


class ReleaseForm(forms.ModelForm):
    releasetype = CustomModelChoiceField(
        field_to_return='name', queryset=models.ReleaseType.objects.all(),
        required=True)

    class Meta:
        model = models.Release
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ReleaseForm, self).__init__(*args, **kwargs)
        add_related_field_wrapper(self, 'releasetype')


class ReleaseAdmin(admin.ModelAdmin):
    list_display = ['releasetype_name', 'releasedate',
                    'producttype_name', 'actualrelease', 'show']

    def releasetype_name(self, obj):
        return get_obj_attribute(obj, 'name', 'releasetype')

    def producttype_name(self, obj):
        return get_obj_attribute(
            obj, 'name', 'producttypeversion', 'producttype')

    form = ReleaseForm

admin.site.register(models.Release, ReleaseAdmin)


# Register any remaining models that have not been explicitly registered:
for model in get_models(get_app('oilserver')):
    try:
        admin.site.register(model)
    except AlreadyRegistered:
        pass
