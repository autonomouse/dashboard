# pylint: disable=C0103
# (ignore invalid naming convention)
import operator
from collections import namedtuple
from functools import reduce
from tastypie import fields
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.authentication import ApiKeyAuthentication
from tastypie.http import HttpBadRequest, HttpCreated, HttpApplicationError
from django.conf.urls import url
from django.conf import settings
from django.http import HttpResponse
from django.db.models import Q, Count
from django.db.models.aggregates import Count as AggCount
from oilserver import models, utils
from django.contrib.sites.models import Site
from oilserver.api.authorization import WorldReadableDjangoAuthorization
from django.forms.models import model_to_dict

# default to not populating reverse relations ('use_in') for speed and 'maximum
# recursion depth' exceeded wormhole
# (see http://django-tastypie.readthedocs.io/en/latest/fields.html#use-in)
ReverseOneField = utils.override_defaults(
    fields.ToOneField,
    {'readonly': True, 'null': True, 'use_in': lambda _: False})
ReverseManyField = utils.override_defaults(
    fields.ToManyField,
    {'readonly': True, 'null': True, 'use_in': lambda _: False})
ForeignKey = utils.override_defaults(
    fields.ForeignKey,
    {'null': True, 'full': True, 'full_list': False})
ToManyField = utils.override_defaults(fields.ToManyField, {'null': True})
ToOneField = utils.override_defaults(fields.ToOneField, {'null': True})


class CommonMeta(object):
    excludes = ['id', 'created_at', 'updated_at']
    list_allowed_methods = ['get', 'post', 'delete']  # all items
    detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
    include_resource_uri = False
    authentication = ApiKeyAuthentication()
    authorization = WorldReadableDjangoAuthorization()
    always_return_data = True
    detail_uri_name = 'uuid'


class CommonResource(ModelResource):
    """The parent resource of the other resource objects.

    Provides common methods and overrides for tastypie's default methods.
    """

    def alter_list_data_to_serialize(self, request, data):
        if request.GET.get('meta_only'):
            return {'meta': data['meta']}
        return data

    def get_bundle_detail_data(self, bundle):
        # FIXME: There is apparently a bug in tastypie's ModelResource
        # where PUT doesn't work if this method returns non null. If
        # this isn't used, a new object is created instead of updating
        # the existing one.
        return None

    def build_filters(self, filters=None, ignore_bad_filters=True):
        def build_Q_from_query(query_dict):
            return Q(**super(CommonResource, self).build_filters(query_dict))

        if filters is None:  # if you don't pass any filters at all
            filters = {}

        custom_filters = {}
        for filter_, value in dict(filters).items():
            if '|' in filter_:
                custom_queries = [build_Q_from_query({query: ','.join(value)})
                                  for query in filter_.split('|')]
                custom_filters[filter_] = reduce(operator.or_, custom_queries)
                del filters[filter_]
        orm_filters = super(CommonResource, self).build_filters(
            filters, ignore_bad_filters)
        orm_filters.update(custom_filters)
        return orm_filters

    def apply_filters(self, request, applicable_filters):
        querysets = []
        for filter_, value in dict(applicable_filters).items():
            if '|' in filter_:
                querysets.append(value)
                del applicable_filters[filter_]
        return self.get_object_list(request).filter(
            *querysets, **applicable_filters).distinct()


class EnvironmentResource(CommonResource):
    """API Resource for 'Environment' model. """

    class Meta(CommonMeta):
        queryset = models.Environment.objects.all()
        filtering = {
            'uuid': ('exact',),
            'name': ('exact', 'in',)}


class WeeblSettingResource(CommonResource):
    """API Resource for 'WeeblSetting' model. """

    class Meta(CommonMeta):
        current_site = Site.objects.get_current().id
        queryset = models.WeeblSetting.objects.filter(pk=current_site)
        list_allowed_methods = ['get']  # all items
        detail_allowed_methods = []  # individual
        fields = ['default_environment']


class ServiceStatusResource(CommonResource):
    """API Resource for 'ServiceStatus' model. """

    class Meta(CommonMeta):
        queryset = models.ServiceStatus.objects.all()
        list_allowed_methods = ['get']  # all items
        detail_allowed_methods = ['get']  # individual
        filtering = {'name': ('exact',), }
        detail_uri_name = 'name'


class JenkinsResource(CommonResource):
    """API Resource for 'Jenkins' model. """

    environment = ForeignKey(EnvironmentResource, 'environment')
    servicestatus = ForeignKey(ServiceStatusResource, 'servicestatus')

    class Meta(CommonMeta):
        queryset = models.Jenkins.objects.all()
        filtering = {
            'environment': ALL_WITH_RELATIONS,
            'uuid': ('exact',),
        }

    def hydrate(self, bundle):
        # Update timestamp (also prevents user submitting timestamp data):
        # FIXME: No need for this field now that we have updated_at from
        # the base model.
        bundle.data['servicestatus_updated_at'] = utils.time_now()
        return super(JenkinsResource, self).hydrate(bundle)


class BuildExecutorResource(CommonResource):
    """API Resource for 'BuildExecutor' model."""

    jenkins = ForeignKey(JenkinsResource, 'jenkins')

    class Meta(CommonMeta):
        queryset = models.BuildExecutor.objects.all()
        fields = ['name', 'uuid', 'jenkins']
        filtering = {'jenkins': ALL_WITH_RELATIONS,
                     'name': ALL,
                     'uuid': ALL, }


class UbuntuVersionResource(CommonResource):
    """API Resource for 'UbuntuVersion' model. """

    class Meta(CommonMeta):
        queryset = models.UbuntuVersion.objects.all()
        filtering = {'name': ALL, }
        detail_uri_name = 'name'


class ProjectResource(CommonResource):
    """API Resource for 'Project' model. """

    class Meta(CommonMeta):
        queryset = models.Project.objects.all()
        filtering = {
            'uuid': ('exact',),
            'name': ('exact',), }


class VendorResource(CommonResource):
    """API Resource for 'Vendor' model. """

    productundertests = ReverseManyField(
        'oilserver.api.resources.ProductUnderTestResource',
        'productundertests')

    class Meta(CommonMeta):
        queryset = models.Vendor.objects.all()
        filtering = {
            'uuid': ('exact',),
            'name': ('exact',),
            'productundertests': ALL_WITH_RELATIONS, }


class InternalContactResource(CommonResource):
    """API Resource for 'InternalContact' model. """

    class Meta(CommonMeta):
        queryset = models.InternalContact.objects.all()
        filtering = {
            'uuid': ('exact',),
            'name': ALL, }


class MachineResource(CommonResource):
    """API Resource for 'Machine' model. """

    machineconfigurations = ReverseManyField(
        'oilserver.api.resources.MachineConfigurationResource',
        'machineconfigurations')

    class Meta(CommonMeta):
        queryset = models.Machine.objects.all()
        filtering = {
            'machineconfigurations': ALL_WITH_RELATIONS,
            'hostname': ('exact', 'in',),
            'uuid': ('exact',), }


class ReportResource(CommonResource):
    """API Resource for 'Report' model.

    Use the reverse relation for report ui (just a link to resource, not full).
    """

    productundertests = ReverseManyField(
        'oilserver.api.resources.ProductUnderTestResource',
        'productundertests', use_in='all')

    class Meta(CommonMeta):
        queryset = models.Report.objects.all()
        filtering = {
            'uuid': ('exact',),
            'name': ('exact',), }


class ProductTypeResource(CommonResource):
    """API Resource for 'ProductType' model. """

    productundertests = ReverseManyField(
        'oilserver.api.resources.ProductUnderTestResource',
        'productundertests')
    testcaseclasses = ReverseManyField(
        'oilserver.api.resources.TestCaseClassResource',
        'testcaseclasses')

    class Meta(CommonMeta):
        queryset = models.ProductType.objects.all().order_by('name')
        filtering = {
            'toplevel': ('exact',),
            'uuid': ('exact',),
            'name': ('exact', 'in',),
            'productundertests': ALL_WITH_RELATIONS, }


class ProductUnderTestResource(CommonResource):
    """API Resource for 'ProductUnderTest' model. """

    vendor = ForeignKey(VendorResource, 'vendor', full_list=True)
    project = ForeignKey(ProjectResource, 'project', full_list=True)
    internalcontact = ForeignKey(
        InternalContactResource, 'internalcontact', full_list=True)
    producttype = ForeignKey(
        ProductTypeResource, 'producttype', full_list=True)
    project = ForeignKey(ProjectResource, 'project', full_list=True)
    reports = ToManyField(ReportResource, 'reports')
    machineconfigurations = ReverseManyField(
        'oilserver.api.resources.MachineConfigurationResource',
        'machineconfigurations')
    jujuservicedeployments = ReverseManyField(
        'oilserver.api.resources.JujuServiceDeploymentResource',
        'jujuservicedeployments')

    class Meta(CommonMeta):
        queryset = models.ProductUnderTest.objects.select_related(
            'vendor', 'project', 'internalcontact', 'producttype').all()
        filtering = {
            'project': ('exact',),
            'internalcontact': ('exact',),
            'vendor': ALL_WITH_RELATIONS,
            'reports': ALL_WITH_RELATIONS,
            'machineconfigurations': ALL_WITH_RELATIONS,
            'jujuservicedeployments': ALL_WITH_RELATIONS,
            'uuid': ('exact',),
            'name': ('exact', 'in',),
            'producttype': ALL_WITH_RELATIONS,
            'project': ALL_WITH_RELATIONS, }


class OpenstackVersionResource(CommonResource):
    """API Resource for 'OpenstackVersion' model. """

    class Meta(CommonMeta):
        queryset = models.OpenstackVersion.objects.all()
        filtering = {'name': ALL, }
        detail_uri_name = 'name'


class VersionConfigurationResource(CommonResource):
    """API Resource for 'VersionConfiguration' model.

    Include a full list of foreign keys for reports (showing versions).
    """

    ubuntuversion = ForeignKey(
        UbuntuVersionResource, 'ubuntuversion', full_list=True)
    openstackversion = ForeignKey(
        OpenstackVersionResource, 'openstackversion', full_list=True)
    pipelines = ReverseManyField(
        'oilserver.api.resources.PipelineResource', 'pipelines')

    class Meta(CommonMeta):
        queryset = models.VersionConfiguration.objects.select_related(
            'ubuntuversion', 'openstackversion').all()
        filtering = {'uuid': ALL,
                     'pipelines': ALL_WITH_RELATIONS,
                     'ubuntuversion': ALL_WITH_RELATIONS,
                     'openstackversion': ALL_WITH_RELATIONS, }


class SolutionTagResource(CommonResource):
    """API Resource for 'SolutionTag' model."""

    class Meta(CommonMeta):
        queryset = models.SolutionTag.objects.all()
        filtering = {'name': ('exact'),
                     'colour': ('exact'), }
        detail_uri_name = 'name'


class SolutionResource(CommonResource):
    """API Resource for 'Solution' model. """

    solutiontag = ToOneField(
        SolutionTagResource, 'solutiontag', full=True)

    class Meta(CommonMeta):
        queryset = models.Solution.objects.all()
        filtering = {'cdo_checksum': ('exact'),
                     'solutiontag': ALL_WITH_RELATIONS, }
        detail_uri_name = 'cdo_checksum'

class PipelineResource(CommonResource):
    """API Resource for 'Pipeline' model.

    Only show foreign keys on detail to speed up listing.
    """

    buildexecutor = ForeignKey(
        BuildExecutorResource, 'buildexecutor', use_in='detail')
    solution = ForeignKey(SolutionResource, 'solution', full_list=True)
    versionconfiguration = ForeignKey(
        VersionConfigurationResource, 'versionconfiguration', use_in='detail')
    configurationchoices = ToOneField(
        'oilserver.api.resources.ConfigurationChoicesResource',
        'configurationchoices',
        readonly=True, full=True, use_in='detail')
    # FIXME: Shouldn't this be configurationchoice?
    builds = ReverseManyField(
        'oilserver.api.resources.BuildResource', 'builds')
    jujuservicedeployments = ReverseManyField(
        'oilserver.api.resources.JujuServiceDeploymentResource',
        'jujuservicedeployments')

    class Meta(CommonMeta):
        queryset = models.Pipeline.objects.all().order_by('-completed_at')
        filtering = {'uuid': ALL,
                     'builds': ALL_WITH_RELATIONS,
                     'completed_at': ALL,
                     'solution': ALL_WITH_RELATIONS,
                     'versionconfiguration': ALL_WITH_RELATIONS,
                     'configurationchoices': ALL_WITH_RELATIONS,
                     'jujuservicedeployments': ALL_WITH_RELATIONS,
                     'buildexecutor': ALL_WITH_RELATIONS, }

    def build_filters(self, filters=None, ignore_bad_filters=True):
        if filters is None:
            filters = {}

        orm_filters = super(PipelineResource, self).build_filters(filters)
        custom = {}
        if 'failed_jobtype' in filters:
            custom['failed_jobtype'] = filters.getlist('failed_jobtype')
        if 'successful_jobtype' in filters:
            custom['successful_jobtype'] =\
                filters.getlist('successful_jobtype')
        orm_filters['custom'] = custom

        return orm_filters

    def apply_filters(self, request, applicable_filters):
        if 'custom' in applicable_filters:
            custom = applicable_filters.pop('custom')
        else:
            custom = None

        semi_filtered = super(PipelineResource, self).apply_filters(
            request, applicable_filters)

        if custom:
            if 'failed_jobtype' in custom:
                failed_q = Q(
                    builds__jobtype__name__in=custom['failed_jobtype'],
                    builds__testcaseinstances__testcase__name__in=custom[
                        'failed_jobtype'],
                    builds__testcaseinstances__testcaseinstancestatus__name='failure')  # noqa: E501
                semi_filtered = semi_filtered.filter(failed_q)
            if 'successful_jobtype' in custom:
                success_q = Q(
                    builds__jobtype__name__in=custom['successful_jobtype'],
                    builds__testcaseinstances__testcase__name__in=custom[
                        'successful_jobtype'],
                    builds__testcaseinstances__testcaseinstancestatus__name='success')  # noqa: E501
                semi_filtered = semi_filtered.filter(success_q)

        return semi_filtered

    def prepend_urls(self):
        return [url(r"^(?P<resource_name>%s)/(?P<uuid>[-\w]+)/bundleimage/$" %
                (self._meta.resource_name),
                self.wrap_view('post_bundleimage'), name="post_bundleimage"),
                url(r"^(?P<resource_name>%s)/(?P<uuid>[-\w]+)/bundleimage$" %
                (self._meta.resource_name),
                self.wrap_view('get_bundleimage'), name="get_bundleimage"), ]

    def post_bundleimage(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        format = request.META.get('CONTENT_TYPE', 'application/json')
        if format.startswith('multipart'):
            try:
                uuid = kwargs['uuid']
                bundle_image = request.FILES['bundleimage']
                with open("{}/img/bundles/{}.svg".format(
                          settings.STATIC_ROOT, uuid), 'wb+') as save_file:
                    for chunk in bundle_image.chunks():
                        save_file.write(chunk)
                return self.create_response(
                    request, 'Bundle image stored', response_class=HttpCreated)
            except Exception as e:
                return self.create_response(
                    request, str(e), response_class=HttpApplicationError)
        else:
            return self.create_response(
                request, 'Malformed request', response_class=HttpBadRequest)

    def get_bundleimage(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        try:
            uuid = kwargs['uuid']
            with open("{}/img/bundles/{}.svg".format(
                      settings.STATIC_ROOT, uuid), 'rb') as image_file:
                response = HttpResponse(
                    image_file.read(), content_type="image/svg")
            return response
        except Exception as e:
            return self.create_response(
                request, str(e), response_class=HttpApplicationError)

    def get_list(self, request, **kwargs):
        """
        This method hijacks the usual get_list and forces it to instead return
        the number of pipelines run binned by time period if
        'timeinterval_grouping' is present in the request. The time
        period can be day, month or year and is defined by what is given as the
        value for timeinterval_grouping.
        """
        interval = request.GET.get('timeinterval_grouping')
        if interval not in ['hour', 'day', 'month', 'year']:
            return super(PipelineResource, self).get_list(request, **kwargs)

        # Get sorted_objects, as usual
        base_bundle = self.build_bundle(request=request)
        objects = self.obj_get_list(
            bundle=base_bundle, **self.remove_api_resource_names(kwargs))
        sorted_objects = self.apply_sorting(objects, options=request.GET)

        # Group data into bins of a time period (defined by interval)
        stmnt = "date_trunc('%s', oilserver_pipeline.completed_at)" % interval
        timeframe = sorted_objects.filter(completed_at__isnull=False).extra({
            interval: stmnt})
        period = timeframe.values(interval).order_by(interval)
        trend_data = list(period.annotate(count=Count("id")))

        # Return binned data instead of usual objects list
        paginator = self._meta.paginator_class(
            request.GET, trend_data, resource_uri=self.get_resource_uri(),
            limit=self._meta.limit, max_limit=self._meta.max_limit,
            collection_name=self._meta.collection_name)
        to_be_serialized = paginator.page()
        to_be_serialized = self.alter_list_data_to_serialize(
            request, to_be_serialized)
        return self.create_response(request, to_be_serialized)


class ConfigurationChoicesResource(CommonResource):
    """API Resource for 'ConfigurationChoices' model. """

    pipeline = ToOneField(PipelineResource, 'pipeline', readonly=True)
    runs = fields.IntegerField('runs', readonly=True, null=True)
    config = fields.DictField('config', readonly=True, null=True)

    class Meta(CommonMeta):
        queryset = models.ConfigurationChoices.objects.all()
        excludes = ['id']
        max_limit = None
        list_allowed_methods = ['get']  # all items
        detail_allowed_methods = []  # individual
        filtering = {'pipeline': ALL_WITH_RELATIONS,
                     'ubuntuversion': ALL_WITH_RELATIONS,
                     'openstackversion': ALL_WITH_RELATIONS,
                     'compute': ('exact', 'in'),
                     'imagestorage': ('exact', 'in'),
                     'sdn': ('exact', 'in'),
                     'blockstorage': ('exact', 'in'),
                     'database': ('exact', 'in'), }

    def obj_get_list(self, bundle, **kwargs):
        """Override getting the object list -- the occurs after all filtering
        takes place, so we can count appropriately, because order of filter and
        count operations matter."""
        returns = super(ConfigurationChoicesResource, self).obj_get_list(
            bundle, **kwargs)
        if 'count_runs' in bundle.request.GET.keys():
            # get a count of pipelines where the following keys are unique
            # together
            columns = ['ubuntuversion', 'openstackversion', 'compute',
                       'imagestorage', 'sdn', 'blockstorage', 'database']
            if 'exclude_versions' in bundle.request.GET.keys():
                columns.remove('ubuntuversion')
                columns.remove('openstackversion')
            objects = returns.values(*columns).annotate(
                runs=Count('pipeline_id'))
            # have to do namedtuples here since tastypie uses attrs not a dict
            return [namedtuple('Dict', object_.keys())(**object_)
                    for object_ in objects.all()]
        else:
            return returns

    def dehydrate(self, bundle):
        """Depending on whether or not we want to get count_runs include
        or exclude it from the entries -- and if we are counting do not show
        erroneous pipeline value."""
        bundle = super(ConfigurationChoicesResource, self).dehydrate(bundle)
        runs = bundle.data['runs']
        del bundle.data['runs']
        del bundle.data['config']
        if 'count_runs' in bundle.request.GET.keys():
            del bundle.data['pipeline']
            bundle.data = {'config': bundle.data, 'runs': runs}
        return bundle


class MachineConfigurationResource(CommonResource):
    """API Resource for 'Machine' model. """

    machine = ForeignKey(MachineResource, 'machine')
    productundertests = ToManyField(
        ProductUnderTestResource, 'productundertests')
    units = ReverseManyField(
        'oilserver.api.resources.UnitResource', 'units')

    class Meta(CommonMeta):
        queryset = models.MachineConfiguration.objects.all()
        filtering = {
            'machine': ALL_WITH_RELATIONS,
            'name': ('exact',),
            'uuid': ('exact',),
            'productundertests': ALL_WITH_RELATIONS,
            'units': ALL_WITH_RELATIONS, }


class CharmResource(CommonResource):
    """API Resource for 'Charm' model. """

    class Meta(CommonMeta):
        queryset = models.Charm.objects.all()
        filtering = {
            'uuid': ('exact',),
            'name': ('exact',),
            'charm_source_url': ('exact',), }


class JujuServiceResource(CommonResource):
    """API Resource for 'JujuService' model. """

    jujuservicedeployments = ReverseManyField(
        'oilserver.api.resources.JujuServiceDeploymentResource',
        'jujuservicedeployments')

    class Meta(CommonMeta):
        queryset = models.JujuService.objects.all()
        filtering = {
            'uuid': ('exact',),
            'name': ('exact',),
            'jujuservicedeployments': ALL_WITH_RELATIONS, }


class JobTypeResource(CommonResource):
    """API Resource for 'JobType' model. """

    class Meta(CommonMeta):
        queryset = models.JobType.objects.all()
        list_allowed_methods = ['get']  # all items
        detail_allowed_methods = ['get']  # individual
        filtering = {'name': ALL, }
        detail_uri_name = 'name'


class BuildResource(CommonResource):
    """API Resource for 'Pipeline' model. """

    pipeline = ForeignKey(PipelineResource, 'pipeline')
    jobtype = ForeignKey(JobTypeResource, 'jobtype')
    testcaseinstances = ReverseManyField(
        'oilserver.api.resources.TestCaseInstanceResource',
        'testcaseinstances')
    jenkins_build_url = fields.CharField('jenkins_build_url', null=True,
                                         readonly=True)

    class Meta(CommonMeta):
        queryset = models.Build.objects.all()
        filtering = {'uuid': ALL,
                     'build_id': ALL,
                     'build_started_at': ALL,
                     'jobtype': ALL_WITH_RELATIONS,
                     'pipeline': ALL_WITH_RELATIONS,
                     'testcaseinstances': ALL_WITH_RELATIONS, }
        ordering = ['build_started_at']

    def dehydrate(self, bundle):
        bundle = super(BuildResource, self).dehydrate(bundle)
        bundle.data['jenkins_build_url'] = bundle.obj.jenkins_build_url
        return bundle


class JujuServiceDeploymentResource(CommonResource):
    """API Resource for 'JujuServiceDeployment' model. """

    pipeline = ForeignKey(
        PipelineResource, 'pipeline', null=False, full_list=True)
    jujuservice = ForeignKey(
        JujuServiceResource, 'jujuservice', full_list=True)
    charm = ForeignKey(CharmResource, 'charm')
    productundertest = ForeignKey(
        ProductUnderTestResource, 'productundertest')
    units = ReverseManyField(
        'oilserver.api.resources.UnitResource', 'units')

    class Meta(CommonMeta):
        queryset = models.JujuServiceDeployment.objects.all()
        filtering = {
            'uuid': ('exact',),
            'success': ALL,
            'jujuservice': ALL_WITH_RELATIONS,
            'charm': ALL_WITH_RELATIONS,
            'pipeline': ALL_WITH_RELATIONS,
            'productundertest': ALL_WITH_RELATIONS,
            'units': ALL_WITH_RELATIONS, }


class UnitResource(CommonResource):
    """API Resource for 'Unit' model. """

    machineconfiguration = ForeignKey(
        MachineConfigurationResource, 'machineconfiguration')
    jujuservicedeployment = ForeignKey(
        JujuServiceDeploymentResource, 'jujuservicedeployment')

    class Meta(CommonMeta):
        queryset = models.Unit.objects.all()
        filtering = {
            'uuid': ('exact',),
            'number': ('exact',),
            'machineconfiguration': ALL_WITH_RELATIONS,
            'jujuservicedeployment': ALL_WITH_RELATIONS, }


class TestFrameworkResource(CommonResource):
    """API Resource for 'TestFramework' model. """

    class Meta(CommonMeta):
        queryset = models.TestFramework.objects.all()
        filtering = {'name': ('exact'),
                     'version': ('exact'),
                     'uuid': ('exact'), }


class ReportSectionResource(CommonResource):
    """API Resource for 'ReportSection' model."""

    testcaseclasses = ReverseManyField(
        'oilserver.api.resources.TestCaseClassResource',
        'testcaseclasses')

    class Meta(CommonMeta):
        queryset = models.ReportSection.objects.all()
        filtering = {
            'name': ('exact'),
            'functionalgroup': ('exact'),
        }


class TestCaseClassResource(CommonResource):
    """API Resource for 'TestCaseClass' model. """

    testframework = ForeignKey(
        TestFrameworkResource, 'testframework')
    producttypes = ToManyField(
        ProductTypeResource, 'producttypes')
    reportsection = ForeignKey(
        ReportSectionResource, 'reportsection')

    class Meta(CommonMeta):
        queryset = models.TestCaseClass.objects.all()
        filtering = {
            'name': ('exact'),
            'uuid': ('exact'),
            'testframework': ALL_WITH_RELATIONS,
        }


class TestCaseInstanceStatusResource(CommonResource):
    """API Resource for 'TestCaseInstanceStatus' model. """

    testcaseinstances = ReverseManyField(
        'oilserver.api.resources.TestCaseInstanceResource',
        'testcaseinstances')

    class Meta(CommonMeta):
        queryset = models.TestCaseInstanceStatus.objects.all()
        filtering = {
            'name': ('exact', 'in'),
        }
        detail_uri_name = 'name'


class TestCaseResource(CommonResource):
    """API Resource for 'TestCase' model. """

    testcaseclass = ForeignKey(
        TestCaseClassResource, 'testcaseclass')

    class Meta(CommonMeta):
        queryset = models.TestCase.objects.all()
        filtering = {
            'name': ('exact'),
            'uuid': ('exact'),
            'testcaseclass': ALL_WITH_RELATIONS,
        }


class TestCaseInstanceResource(CommonResource):
    """API Resource for 'TestCaseInstance' model.

    Include a full list of foreign keys for individualTestRun page.
    """

    build = ForeignKey(BuildResource, 'build', full_list=True)
    testcase = ForeignKey(TestCaseResource, 'testcase', full_list=True)
    testcaseinstancestatus = ForeignKey(
        TestCaseInstanceStatusResource, 'testcaseinstancestatus',
        full_list=True)
    bugoccurrences = ReverseManyField(
        'oilserver.api.resources.BugOccurrenceResource',
        'bugoccurrences')

    class Meta(CommonMeta):
        queryset = models.TestCaseInstance.objects.select_related(
            'build', 'testcase', 'testcaseinstancestatus').all()
        filtering = {
            'uuid': ('exact'),
            'build': ALL_WITH_RELATIONS,
            'testcaseinstancestatus': ALL_WITH_RELATIONS,
            'testcase': ALL_WITH_RELATIONS,
            'bugoccurrences': ALL_WITH_RELATIONS,
        }


class TargetFileGlobResource(CommonResource):
    """API Resource for 'TargetFileGlob' model. """

    jobtypes = ToManyField(
        'oilserver.api.resources.JobTypeResource', 'jobtypes', full=True)
    knownbugregexes = ReverseManyField(
        'oilserver.api.resources.KnownBugRegexResource', 'knownbugregexes')

    class Meta(CommonMeta):
        queryset = models.TargetFileGlob.objects.all()
        filtering = {'glob_pattern': ALL,
                     'jobtypes': ALL_WITH_RELATIONS,
                     'knownbugregexes': ALL_WITH_RELATIONS, }
        detail_uri_name = 'glob_pattern'


class BugTrackerBugResource(CommonResource):
    """API Resource for 'BugTrackerBug' model. """

    bug = ReverseOneField('oilserver.api.resources.BugResource', 'bug')
    project = ForeignKey(ProjectResource, 'project', full_list=True)
    created_at = fields.DateTimeField('created_at', readonly=True)
    updated_at = fields.DateTimeField('updated_at', readonly=True)

    class Meta(CommonMeta):
        queryset = models.BugTrackerBug.objects.select_related('project').all()
        excludes = ['id']
        filtering = {
            'bug_number': ALL,
            'bug': ALL_WITH_RELATIONS, }
        detail_uri_name = 'bug_number'


class BugResource(CommonResource):
    """API Resource for 'Bug' model. """

    bugtrackerbug = ToOneField(
        'oilserver.api.resources.BugTrackerBugResource', 'bugtrackerbug',
        full=True)
    knownbugregexes = ReverseManyField(
        'oilserver.api.resources.KnownBugRegexResource', 'knownbugregexes')
    historical_bugoccurrences = fields.ListField('historical_bugoccurrences',
                                                 readonly=True, null=True)
    occurrence_count = fields.IntegerField('occurrence_count', readonly=True,
                                           null=True)
    last_seen = fields.DateTimeField('last_seen', readonly=True, null=True)

    class Meta(CommonMeta):
        queryset = models.Bug.objects.select_related('bugtrackerbug').all()
        filtering = {'summary': ('contains', 'exact'),
                     'uuid': ('exact'),
                     'description': ('exact'),
                     'knownbugregexes': ALL_WITH_RELATIONS,
                     'bugtrackerbug': ALL_WITH_RELATIONS, }

    def dehydrate(self, bundle):
        bundle = super(BugResource, self).dehydrate(bundle)
        bugoccurrence = BugOccurrenceResource().occurrences_for_bug_filters(
            bundle)
        bundle.data['occurrence_count'] = bugoccurrence.count()

        interval = bundle.request.GET.get('historical_bugoccurrences_grouping')
        try:
            bugno = bundle.data['bugtrackerbug'].data['bug_number']
        except (KeyError, AttributeError):
            bugno = None
        if interval in ['day', 'month', 'year'] and bugno:
            bugoccurrences_history = models.BugOccurrence.objects.filter(
                knownbugregex__bug__bugtrackerbug__bug_number=bugno)
            stmnt = "date_trunc('%s', oilserver_bugoccurrence.created_at)" % \
                interval
            timeframe = bugoccurrences_history.extra({"date": stmnt})
            bugocc_data = []
            if timeframe:
                period = timeframe.values("date").order_by("date")
                bugocc_data = list(period.annotate(count=AggCount("id")))
            bundle.data["historical_bugoccurrences"] = bugocc_data
        else:
            del bundle.data['historical_bugoccurrences']

        if bugoccurrence.exists():
            try:
                last_seen = bugoccurrence.latest(
                    'testcaseinstance__build__pipeline__completed_at')
                bundle.data['last_seen'] = \
                    last_seen.testcaseinstance.build.pipeline.completed_at
            except AttributeError:
                bundle.data['last_seen'] = None
        return bundle


class KnownBugRegexResource(CommonResource):
    """API Resource for 'BugTrackerBug' model. """

    bug = ForeignKey(BugResource, 'bug', full_list=True)
    targetfileglobs = ToManyField(
        TargetFileGlobResource, 'targetfileglobs', full=True)
    bugoccurrences = ReverseManyField(
        'oilserver.api.resources.BugOccurrenceResource',
        'bugoccurrences')

    class Meta(CommonMeta):
        queryset = models.KnownBugRegex.objects.select_related('bug').all()
        filtering = {'uuid': ALL,
                     'regex': ALL,
                     'targetfileglobs': ALL_WITH_RELATIONS,
                     'bug': ALL_WITH_RELATIONS,
                     'bugoccurrences': ALL_WITH_RELATIONS}


class BugOccurrenceResource(CommonResource):
    """API Resource for 'BugTrackerBug' model. """

    knownbugregex = ForeignKey(KnownBugRegexResource, 'knownbugregex')
    testcaseinstance = ForeignKey(TestCaseInstanceResource, 'testcaseinstance')
    created_at = fields.DateTimeField('created_at', readonly=True)
    updated_at = fields.DateTimeField('updated_at', readonly=True)

    class Meta(CommonMeta):
        queryset = models.BugOccurrence.objects.all()
        excludes = []
        filtering = {'uuid': ALL,
                     'knownbugregex': ALL_WITH_RELATIONS,
                     'testcaseinstance': ALL_WITH_RELATIONS, }

    def occurrences_for_bug_filters(self, bundle):
        """Get the bug occurrences that match a bug's filter.

        When bugs are found by bug occurrence properties, this matches
        bug occurrences that match those properties. So if we filter for
        bugs with occurrences in pipelines that completed in 2015, only
        the bug occurrences that completed in 2015 will be included.

        Args:
            bundle: The tastypie bundle.
        """
        query_dict = bundle.request.GET
        replace_prefix = 'knownbugregexes__bugoccurrences__'
        bugoccurrence_filters = {}
        for key, value in query_dict.items():
            # remove prefixes from each OR portion of each key
            filter_name = '|'.join(
                [k.replace(replace_prefix, '')
                 for k in key.split('|') if k.startswith(replace_prefix)])

            if filter_name.endswith('__in'):
                # __in defines a list of possible entries, so get a list back.
                # Tastypie expects this to be a string joined by commas
                # our workaround for OR filters does not.
                value = bundle.request.GET.getlist(key)
                if '|' not in key:
                    value = ','.join(value)
            bugoccurrence_filters[filter_name] = value
        bugoccurrence_filters['knownbugregex__bug__uuid'] = bundle.obj.uuid
        built_filters = self.build_filters(filters=bugoccurrence_filters)
        return self.apply_filters(None, built_filters).distinct()


class ReportPeriodResource(CommonResource):
    """API Resource for 'ReportPeriod' model. """

    class Meta(CommonMeta):
        queryset = models.ReportPeriod.objects.all()
        filtering = {'uuid': ('exact',),
                     'name': ('exact',), }


class ReportInstanceResource(CommonResource):
    """API Resource for 'ReportInstance' model. """

    report = ForeignKey(ReportResource, 'report')
    reportperiod = ForeignKey(ReportPeriodResource, 'reportperiod')

    class Meta(CommonMeta):
        queryset = models.ReportInstance.objects.all()
        filtering = {'uuid': ('exact',),
                     'report': ALL_WITH_RELATIONS,
                     'reportperiod': ALL_WITH_RELATIONS, }


class BugReportViewResource(CommonResource):
    """API Resource for 'BugReportView' model. """

    bug = ToOneField(BugResource, 'bug', readonly=True)

    class Meta(CommonMeta):
        queryset = models.BugReportView.objects.all()
        excludes = ['id']
        max_limit = None
        list_allowed_methods = ['get']  # all items
        detail_allowed_methods = []  # individual
        filtering = {'bug': ALL_WITH_RELATIONS,
                     'reportname': ('exact', 'in'),
                     'date': ALL,
                     'environmentname': ('exact', 'in'), }


class PipelineReportViewResource(CommonResource):
    """API Resource for 'PipelineReportView' model. """

    class Meta(CommonMeta):
        queryset = models.PipelineReportView.objects.all()
        excludes = ['id']
        max_limit = None
        list_allowed_methods = ['get']  # all items
        detail_allowed_methods = []  # individual
        filtering = {'reportname': ('exact', 'in'),
                     'date': ALL,
                     'environmentname': ('exact', 'in'), }


class ServiceReportViewResource(CommonResource):
    """API Resource for 'ServiceReportView' model. """

    class Meta(CommonMeta):
        queryset = models.ServiceReportView.objects.all()
        excludes = ['id']
        max_limit = None
        list_allowed_methods = ['get']  # all items
        detail_allowed_methods = []  # individual
        filtering = {'reportname': ('exact', 'in'),
                     'date': ALL,
                     'environmentname': ('exact', 'in'), }


class TestReportViewResource(CommonResource):
    """API Resource for 'TestReportView' model. """

    bug = ToOneField(BugResource, 'bug', readonly=True)

    class Meta(CommonMeta):
        queryset = models.TestReportView.objects.all()
        excludes = ['id']
        max_limit = None
        list_allowed_methods = ['get']  # all items
        detail_allowed_methods = []  # individual
        filtering = {'bug': ALL_WITH_RELATIONS,
                     'reportname': ('exact', 'in'),
                     'date': ALL,
                     'groupname': ALL,
                     'environmentname': ('exact', 'in'), }
