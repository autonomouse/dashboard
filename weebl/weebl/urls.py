from django.conf.urls import patterns, include, url
from tastypie.api import Api
from oilserver.api import resources
from weebl.__init__ import __api_version__
from django.contrib import admin


v_api = Api(api_name=__api_version__)
v_api.register(resources.EnvironmentResource())
v_api.register(resources.ServiceStatusResource())
v_api.register(resources.JenkinsResource())
v_api.register(resources.BuildExecutorResource())
v_api.register(resources.PipelineResource())
v_api.register(resources.JobTypeResource())
v_api.register(resources.BuildResource())
v_api.register(resources.TargetFileGlobResource())
v_api.register(resources.KnownBugRegexResource())
v_api.register(resources.BugResource())
v_api.register(resources.BugTrackerBugResource())
v_api.register(resources.BugOccurrenceResource())
v_api.register(resources.UbuntuVersionResource())
v_api.register(resources.OpenstackVersionResource())
v_api.register(resources.ProjectResource())
v_api.register(resources.MachineResource())
v_api.register(resources.VendorResource())
v_api.register(resources.ProductUnderTestResource())
v_api.register(resources.InternalContactResource())
v_api.register(resources.MachineConfigurationResource())
v_api.register(resources.JujuServiceResource())
v_api.register(resources.JujuServiceDeploymentResource())
v_api.register(resources.UnitResource())
v_api.register(resources.ReportResource())
v_api.register(resources.ReportPeriodResource())
v_api.register(resources.ReportInstanceResource())
v_api.register(resources.TestFrameworkResource())
v_api.register(resources.TestCaseClassResource())
v_api.register(resources.TestCaseInstanceStatusResource())
v_api.register(resources.TestCaseInstanceResource())
v_api.register(resources.TestCaseResource())
v_api.register(resources.WeeblSettingResource())
v_api.register(resources.CharmResource())
v_api.register(resources.VersionConfigurationResource())
v_api.register(resources.ProductTypeResource())
v_api.register(resources.ConfigurationChoicesResource())
v_api.register(resources.BugReportViewResource())
v_api.register(resources.PipelineReportViewResource())
v_api.register(resources.ServiceReportViewResource())
v_api.register(resources.TestReportViewResource())
v_api.register(resources.ReportSectionResource())
v_api.register(resources.SolutionTagResource())
v_api.register(resources.SolutionResource())

urlpatterns = patterns(
    '',
    url(r'^', include('oilserver.urls')),
    url(r'^api/', include(v_api.urls)),
    url(r'', include('social.apps.django_app.urls', namespace='social')),
    url(r'^admin/', include(admin.site.urls)),
)
