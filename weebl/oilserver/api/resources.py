import dateutil
import operator
from functools import reduce
from tastypie import fields
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.authorization import DjangoAuthorization
from tastypie.authentication import ApiKeyAuthentication
from tastypie.http import HttpBadRequest, HttpCreated, HttpApplicationError
from tastypie.utils import trailing_slash
from django.conf.urls import url
from django.conf import settings
from django.http import HttpResponse
from django.db.models import Q
from oilserver import models, utils
from oilserver.exceptions import NonUserEditableError


def fixup_set_filters(model_names, applicable_filters):
    """Hack to fix tastypie filter strings.

    Tastypie tries to make filter strings like 'bugoccurrences_set'
    instead of 'bugoccurences'. This replaces the former with the latter
    for a set of model names.

    TODO: See if this can be fixed by specifying reverse relation names
    on models.

    Args:
        model_names (list): A list of object names (e.g.
            ['bug', 'knownbugregex']).
        applicable_filters: filters given to tastypie's apply_filters method.
    """
    for model_name in model_names:
        bad_keys = []
        set_name = model_name + "_set"
        for key in applicable_filters.keys():
            if set_name in key:
                bad_keys.append(key)
        for bad_key in bad_keys:
            value = applicable_filters.pop(bad_key)
            new_key = bad_key.replace(set_name, model_name)
            applicable_filters[new_key] = value


def raise_error_if_in_bundle(bundle, error_if_fields):
    """Raise error if any of the given fields are in the bundle.

    Raises a NonUserEditableError if any of the fields given in error_if_fields
    are present in bundle.data.

    Args:
        bundle: The tastypie bundle.
        error_if_fields (list): A list of field names (e.g. ['created_at',
            'updated_at']).

        Raises:
            NonUserEditableError: Raises an exception.
    """
    bad_fields = []
    for field in error_if_fields:
        if field in bundle.data:
            bad_fields.append(field)
    if bad_fields:
        msg = "Cannot edit field(s): {}".format(", ".join(bad_fields))
        raise NonUserEditableError(msg)


class CommonResource(ModelResource):
    """The parent resource of the other resource objects.

    Provides common methods and overrides for tastypie's default methods.
    """

    def hydrate(self, bundle):
        # Timestamp data should be generated interanlly and not editable:
        error_if_fields = ['created_at', 'updated_at']
        raise_error_if_in_bundle(bundle, error_if_fields)
        return bundle

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

    def build_filters(self, filters=None):
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
        orm_filters = super(CommonResource, self).build_filters(filters)
        orm_filters.update(custom_filters)
        return orm_filters

    def apply_filters(self, request, applicable_filters):
        querysets = []
        for filter_, value in dict(applicable_filters).items():
            if '|' in filter_:
                querysets.append(value)
                del applicable_filters[filter_]
        semi_filtered = super(CommonResource, self).apply_filters(
            request, applicable_filters
        )
        for queryset in querysets:
            semi_filtered = semi_filtered.filter(queryset)
        return semi_filtered


class EnvironmentResource(CommonResource):
    """API Resource for 'Environment' model. """
    class Meta:
        queryset = models.Environment.objects.all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['uuid', 'name']
        authorization = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
        always_return_data = True
        filtering = {
            'uuid': ('exact',),
            'name': ('exact', 'in',)}
        detail_uri_name = 'uuid'

    def prepend_urls(self):
        # Create "by_name" as a new end-point:
        # FIXME: We should use filtering here, not a separate new URL.
        resource_regex = "P<resource_name>{})".format(self._meta.resource_name)
        name_regex = "(?P<name>\w[\w/-]*)"
        end_point = "by_name"
        new_url = r"^(?{}/{}/{}{}$".format(resource_regex, end_point,
                                           name_regex, trailing_slash())
        return [url(new_url,
                    self.wrap_view('get_by_name'),
                    name="api_get_by_name"), ]

    def get_by_name(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        name = kwargs['name']
        if models.Environment.objects.filter(name=name).exists():
            environment = models.Environment.objects.get(name=name)
            bundle = self.build_bundle(obj=environment, request=request)
            return self.create_response(request, self.full_dehydrate(bundle))

    def dehydrate(self, bundle):
        """Include the job history of an environment, if requested."""
        bundle = super(EnvironmentResource, self).dehydrate(bundle)
        if 'include_job_history' in bundle.request.GET:
            if 'history_start_date' in bundle.request.GET:
                parsed_date = dateutil.parser.parse(
                    bundle.request.GET['history_start_date'])
                job_history = bundle.obj.get_job_history(
                    start_date=parsed_date)
            else:
                job_history = bundle.obj.get_job_history()
            bundle.data['job_history'] = job_history
        return bundle


class ServiceStatusResource(CommonResource):
    """API Resource for 'ServiceStatus' model. """

    class Meta:
        queryset = models.ServiceStatus.objects.all()
        list_allowed_methods = ['get']  # all items
        detail_allowed_methods = ['get']  # individual
        fields = ['name', 'description']
        authorization = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
        always_return_data = True
        filtering = {'name': ('exact',), }
        detail_uri_name = 'name'


class JenkinsResource(CommonResource):
    """API Resource for 'Jenkins' model.

    Attributes:
        environment: Foreign key to the Environment resource.
        servicestatus: Foreign key to the ServiceStatus resource.
    """

    environment = fields.ForeignKey(EnvironmentResource, 'environment')
    servicestatus = fields.ForeignKey(ServiceStatusResource, 'servicestatus')

    class Meta:
        queryset = models.Jenkins.objects.all()
        fields = ['environment', 'servicestatus', 'external_access_url',
                  'internal_access_url', 'servicestatus_updated_at', 'uuid']
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        authorization = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
        always_return_data = True
        filtering = {
            'environment': ALL_WITH_RELATIONS,
            'uuid': ('exact',),
        }
        detail_uri_name = 'uuid'

    def hydrate(self, bundle):
        # Update timestamp (also prevents user submitting timestamp data):
        # FIXME: No need for this field now that we have updated_at from
        # the base model.
        bundle.data['servicestatus_updated_at'] = utils.time_now()
        return super(JenkinsResource, self).hydrate(bundle)


class BuildExecutorResource(CommonResource):
    """API Resource for 'BuildExecutor' model.

    Attributes:
        jenkins: Foreign key to the Jenkins resource.
    """

    jenkins = fields.ForeignKey(JenkinsResource, 'jenkins')

    class Meta:
        queryset = models.BuildExecutor.objects.all()
        fields = ['name', 'uuid', 'jenkins']
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        authorization = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
        always_return_data = True
        filtering = {'jenkins': ALL_WITH_RELATIONS,
                     'name': ALL,
                     'uuid': ALL, }
        detail_uri_name = 'uuid'


class UbuntuVersionResource(CommonResource):
    """API Resource for 'UbuntuVersion' model. """

    class Meta:
        queryset = models.UbuntuVersion.objects.all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['name', 'number']
        authorization = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
        always_return_data = True
        filtering = {'name': ALL, }
        detail_uri_name = 'name'


class ProjectResource(CommonResource):
    """API Resource for 'Project' model. """

    class Meta:
        queryset = models.Project.objects.all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['name', 'uuid']
        authorization = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
        always_return_data = True
        filtering = {
            'uuid': ('uuid',),
            'name': ('exact',), }
        detail_uri_name = 'uuid'


class VendorResource(CommonResource):
    """API Resource for 'Vendor' model. """

    class Meta:
        queryset = models.Vendor.objects.all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['name', 'description', 'uuid']
        authorization = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
        always_return_data = True
        filtering = {
            'uuid': ('uuid',),
            'name': ('exact',), }
        detail_uri_name = 'uuid'


class InternalContactResource(CommonResource):
    """API Resource for 'InternalContact' model. """

    class Meta:
        queryset = models.InternalContact.objects.all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['name', 'uuid']
        authorization = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
        always_return_data = True
        filtering = {
            'uuid': ('uuid',),
            'name': ALL, }
        detail_uri_name = 'uuid'


class MachineResource(CommonResource):
    """API Resource for 'Machine' model. """

    machineconfiguration = fields.ToManyField(
        'oilserver.api.resources.MachineConfigurationResource',
        'machineconfiguration', null=True, readonly=True)

    class Meta:
        queryset = models.Machine.objects.all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['hostname', 'uuid', 'machineconfiguration']
        authorization = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
        always_return_data = True
        filtering = {
            'machineconfiguration': ALL_WITH_RELATIONS,
            'hostname': ('exact', 'in',),
            'uuid': ('exact',), }
        detail_uri_name = 'uuid'

    def apply_filters(self, request, applicable_filters):
        fixup_set_filters(['machineconfiguration'], applicable_filters)
        return super(MachineResource, self).apply_filters(
            request, applicable_filters).distinct()


class ReportResource(CommonResource):
    """API Resource for 'Report' model. """

    class Meta:
        queryset = models.Report.objects.all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['name', 'uuid']
        authorization = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
        always_return_data = True
        filtering = {
            'uuid': ('exact',),
            'name': ('exact',), }
        detail_uri_name = 'uuid'


class ProductUnderTestResource(CommonResource):
    """API Resource for 'ProductUnderTest' model.

    Attributes:
        project: Foreign key to the Project resource.
        vendor: Foreign key to the Vendor resource.
        internalcontact: Foreign key to the InternalContact resource.
        report: To-Many relation to the Report resource.
    """

    project = fields.ForeignKey(
        ProjectResource, 'project', full=True, null=True)
    vendor = fields.ForeignKey(VendorResource, 'vendor', full=True, null=True)
    internalcontact = fields.ForeignKey(
        InternalContactResource, 'internalcontact', full=True, null=True)
    report = fields.ToManyField(
        ReportResource, 'report', full=True, null=True)

    class Meta:
        queryset = models.ProductUnderTest.objects.all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = [
            'name', 'project', 'vendor', 'uuid', 'internalcontact', 'report']
        authorization = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
        always_return_data = True
        filtering = {
            'project': ('exact',),
            'internalcontact': ('exact',),
            'vendor': ('exact',),
            'report': ('exact',),
            'uuid': ('uuid',),
            'name': ('exact', 'in',), }
        detail_uri_name = 'uuid'


class OpenstackVersionResource(CommonResource):
    """API Resource for 'OpenstackVersion' model. """

    class Meta:
        queryset = models.OpenstackVersion.objects.all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['name']
        authorization = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
        always_return_data = True
        filtering = {'name': ALL, }
        detail_uri_name = 'name'


class SDNResource(CommonResource):
    """API Resource for 'SDN' model. """

    class Meta:
        resource_name = 'sdn'
        queryset = models.SDN.objects.all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['name']
        authorization = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
        always_return_data = True
        filtering = {'name': ALL, }
        detail_uri_name = 'name'


class ComputeResource(CommonResource):
    """API Resource for 'Compute' model. """

    class Meta:
        queryset = models.Compute.objects.all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['name']
        authorization = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
        always_return_data = True
        filtering = {'name': ALL, }
        detail_uri_name = 'name'


class BlockStorageResource(CommonResource):
    """API Resource for 'BlockStorage' model. """

    class Meta:
        queryset = models.BlockStorage.objects.all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['name']
        authorization = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
        always_return_data = True
        filtering = {'name': ALL, }
        detail_uri_name = 'name'


class ImageStorageResource(CommonResource):
    """API Resource for 'ImageStorage' model. """

    class Meta:
        queryset = models.ImageStorage.objects.all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['name']
        authorization = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
        always_return_data = True
        filtering = {'name': ALL, }
        detail_uri_name = 'name'


class DatabaseResource(CommonResource):
    """API Resource for 'Database' model. """

    class Meta:
        queryset = models.Database.objects.all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['name']
        authorization = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
        always_return_data = True
        filtering = {'name': ALL, }
        detail_uri_name = 'name'


class PipelineResource(CommonResource):
    """API Resource for 'Pipeline' model.

    Attributes:
        ubuntuversion: Foreign key to the UbuntuVersion resource.
        buildexecutor: Foreign key to the BuildExecutor resource.
        openstackversion: Foreign key to the OpenstackVersion resource.
        sdn: Foreign key to the SDN resource.
        compute: Foreign key to the Compute resource.
        blockstorage: Foreign key to the BlockStorage resource.
        imagestorage: Foreign key to the ImageStorage resource.
        database: Foreign key to the Database resource.
        build: To-Many relation to the Build resource.
    """

    ubuntuversion = fields.ForeignKey(
        UbuntuVersionResource, 'ubuntuversion', full=True, null=True)
    buildexecutor = fields.ForeignKey(BuildExecutorResource, 'buildexecutor')
    openstackversion = fields.ForeignKey(
        OpenstackVersionResource, 'openstackversion', full=True, null=True)
    sdn = fields.ForeignKey(SDNResource, 'sdn', full=True, null=True)
    compute = fields.ForeignKey(ComputeResource, 'compute',
                                full=True, null=True)
    blockstorage = fields.ForeignKey(BlockStorageResource, 'blockstorage',
                                     full=True, null=True)
    imagestorage = fields.ForeignKey(ImageStorageResource, 'imagestorage',
                                     full=True, null=True)
    database = fields.ForeignKey(DatabaseResource, 'database',
                                 full=True, null=True)
    build = fields.ToManyField(
        'oilserver.api.resources.BuildResource',
        'build', null=True, readonly=True)
    machineconfiguration = fields.ToManyField(
        'oilserver.api.resources.MachineConfigurationResource',
        'machineconfiguration', null=True, readonly=True)

    class Meta:
        queryset = models.Pipeline.objects.select_related(
            'ubuntuversion', 'openstackversion', 'sdn', 'compute',
            'blockstorage', 'imagestorage', 'database',
            'buildexecutor').all()
        fields = [
            'uuid', 'build', 'buildexecutor', 'completed_at', 'ubuntuversion',
            'openstackversion', 'sdn', 'compute', 'blockstorage',
            'imagestorage', 'database', 'machineconfiguration']
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        authorization = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
        always_return_data = True
        filtering = {'uuid': ALL,
                     'build': ALL_WITH_RELATIONS,
                     'completed_at': ALL,
                     'ubuntuversion': ALL_WITH_RELATIONS,
                     'openstackversion': ALL_WITH_RELATIONS,
                     'sdn': ALL_WITH_RELATIONS,
                     'compute': ALL_WITH_RELATIONS,
                     'blockstorage': ALL_WITH_RELATIONS,
                     'imagestorage': ALL_WITH_RELATIONS,
                     'database': ALL_WITH_RELATIONS,
                     'buildexecutor': ALL_WITH_RELATIONS,
                     'machineconfiguration': ALL_WITH_RELATIONS,
                     }
        detail_uri_name = 'uuid'

    def apply_filters(self, request, applicable_filters):
        fixup_set_filters(['build'], applicable_filters)
        return super(PipelineResource, self).apply_filters(
            request, applicable_filters).distinct()

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


class MachineConfigurationResource(CommonResource):
    """API Resource for 'Machine' model.

    Attributes:
        machine: To-Many relation to the Machine resource.
        pipeline: Foreign key to the Pipeline resource.
    """

    machine = fields.ForeignKey(
        MachineResource, 'machine', full=True, null=True)
    pipeline = fields.ForeignKey(
        PipelineResource, 'pipeline', full=True, null=True)
    productundertest = fields.ToManyField(
        ProductUnderTestResource, 'productundertest', full=True, null=True)
    unit = fields.ToManyField(
        'oilserver.api.resources.UnitResource',
        'unit', null=True, readonly=True)

    class Meta:
        queryset = models.MachineConfiguration.objects.all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['name', 'uuid', 'machine', 'pipeline', 'productundertest',
                  'unit']
        authorization = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
        always_return_data = True
        filtering = {
            'machine': ALL_WITH_RELATIONS,
            'name': ('exact',),
            'uuid': ('exact',),
            'pipeline': ALL_WITH_RELATIONS,
            'productundertest': ALL_WITH_RELATIONS,
            'unit': ALL_WITH_RELATIONS, }
        detail_uri_name = 'uuid'


class JujuServiceResource(CommonResource):
    """API Resource for 'JujuService' model.

    Attributes:
        productundertest: To-Many relation to the ProductUnderTest resource.
    """

    productundertest = fields.ToManyField(
        ProductUnderTestResource, 'productundertest', full=True, null=True)

    class Meta:
        queryset = models.JujuService.objects.all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['uuid', 'name', 'productundertest']
        authorization = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
        always_return_data = True
        filtering = {
            'uuid': ('exact',),
            'name': ('exact',),
            'productundertest': ALL_WITH_RELATIONS, }
        detail_uri_name = 'name'


class JujuServiceDeploymentResource(CommonResource):
    """API Resource for 'JujuServiceDeployment' model.

    Attributes:
        jujuservice: Foreign key to the JujuService resource.
    """

    jujuservice = fields.ForeignKey(
        JujuServiceResource, 'jujuservice', full=True, null=True)

    class Meta:
        queryset = models.JujuServiceDeployment.objects.all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['uuid', 'jujuservice']
        authorization = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
        always_return_data = True
        filtering = {
            'uuid': ('exact',),
            'jujuservice': ALL_WITH_RELATIONS, }
        detail_uri_name = 'name'


class UnitResource(CommonResource):
    """API Resource for 'Unit' model.

    Attributes:
        machineconfiguration: Foreign key to the MachineConfiguration resource.
        jujuservicedeployment: Foreign key to the JujuServiceDeployment
            resource.
    """

    machineconfiguration = fields.ForeignKey(
        MachineConfigurationResource, 'machineconfiguration', full=True,
        null=True)
    jujuservicedeployment = fields.ForeignKey(JujuServiceDeploymentResource,
                                              'jujuservicedeployment',
                                              full=True, null=True)

    class Meta:
        queryset = models.Unit.objects.all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['uuid', 'number', 'machineconfiguration',
                  'jujuservicedeployment']
        authorization = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
        always_return_data = True
        filtering = {
            'uuid': ('exact',),
            'number': ('exact',),
            'machineconfiguration': ALL_WITH_RELATIONS,
            'jujuservicedeployment': ALL_WITH_RELATIONS, }
        detail_uri_name = 'uuid'


class JobTypeResource(CommonResource):
    """API Resource for 'JobType' model. """

    class Meta:
        queryset = models.JobType.objects.all()
        list_allowed_methods = ['get']  # all items
        detail_allowed_methods = ['get']  # individual
        fields = ['name', 'description']
        authorization = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
        always_return_data = True
        filtering = {'name': ALL, }
        detail_uri_name = 'name'


class BuildResource(CommonResource):
    """API Resource for 'Pipeline' model.

    Attributes:
        pipeline: Foreign key to the Pipeline resource.
        jobtype: Foreign key to the JobType resource.
        testcaseinstances: To-Many relation to the TestCaseInstance resource.
    """

    pipeline = fields.ForeignKey(PipelineResource, 'pipeline')
    jobtype = fields.ForeignKey(JobTypeResource, 'jobtype')
    testcaseinstances = fields.ToManyField(
        'oilserver.api.resources.TestCaseInstanceResource',
        'testcaseinstance', null=True, readonly=True, use_in='detail')

    class Meta:
        queryset = models.Build.objects.all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['uuid', 'build_id', 'build_started_at',
                  'build_finished_at', 'build_analysed_at', 'pipeline',
                  'jobtype', 'testcaseinstances']
        authorization = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
        always_return_data = True
        filtering = {'uuid': ALL,
                     'build_id': ALL,
                     'jobtype': ALL_WITH_RELATIONS,
                     'pipeline': ALL_WITH_RELATIONS,
                     'testcaseinstances': ALL_WITH_RELATIONS, }
        detail_uri_name = 'uuid'

    def dehydrate(self, bundle):
        bundle = super(BuildResource, self).dehydrate(bundle)
        bundle.data['jenkins_build_url'] = bundle.obj.jenkins_build_url
        return bundle

    def apply_filters(self, request, applicable_filters):
        fixup_set_filters(['testcaseinstances'], applicable_filters)
        return super(BuildResource, self).apply_filters(
            request, applicable_filters).distinct()


class TestFrameworkResource(CommonResource):
    """API Resource for 'TestFramework' model. """

    class Meta:
        queryset = models.TestFramework.objects.all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['name', 'description', 'version', 'uuid']
        authorization = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
        always_return_data = True
        filtering = {'name': ('exact'),
                     'version': ('exact'),
                     'uuid': ('exact'), }
        detail_uri_name = 'uuid'


class TestCaseClassResource(CommonResource):
    """API Resource for 'TestCaseClass' model.

    Attributes:
        testframework: Foreign key to the TestFramework resource.
    """

    testframework = fields.ForeignKey(
        TestFrameworkResource, 'testframework', full=True, null=True)

    class Meta:
        queryset = models.TestCaseClass.objects.all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['name', 'testframework', 'uuid']
        authorization = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
        always_return_data = True
        filtering = {
            'name': ('exact'),
            'uuid': ('exact'),
            'testframework': ALL_WITH_RELATIONS,
        }
        detail_uri_name = 'uuid'


class TestCaseInstanceStatusResource(CommonResource):
    """API Resource for 'TestCaseInstanceStatus' model. """

    class Meta:
        queryset = models.TestCaseInstanceStatus.objects.all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['name', 'description']
        authorization = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
        always_return_data = True
        filtering = {
            'name': ('exact', 'in'),
        }
        detail_uri_name = 'name'


class TestCaseResource(CommonResource):
    """API Resource for 'TestCase' model.

    Attributes:
        testcaseclass: Foreign key to the TestCaseClass resource.
    """

    testcaseclass = fields.ForeignKey(
        TestCaseClassResource, 'testcaseclass', full=True, null=True)

    class Meta:
        queryset = models.TestCase.objects.all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['name', 'testcaseclass', 'uuid']
        authorization = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
        always_return_data = True
        filtering = {
            'name': ('exact'),
            'uuid': ('exact'),
            'testcaseclass': ALL_WITH_RELATIONS,
        }
        detail_uri_name = 'uuid'


class TestCaseInstanceResource(CommonResource):
    """API Resource for 'TestCaseInstance' model.

    Attributes:
        testcaseinstancestatus: Foreign key to the
            TestCaseInstanceStatusResource resource.
        build: Foreign key to the BuildResource resource.
        testcase: Foreign key to the TestCase resource.
    """

    testcaseinstancestatus = fields.ForeignKey(
        TestCaseInstanceStatusResource, 'testcaseinstancestatus', full=True,
        null=True)
    build = fields.ForeignKey(BuildResource, 'build', full=True, null=True)
    testcase = fields.ForeignKey(
        TestCaseResource, 'testcase', full=True, null=True)

    class Meta:
        queryset = models.TestCaseInstance.objects.all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['testcaseinstancestatus', 'uuid', 'build', 'testcase']
        authorization = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
        always_return_data = True
        filtering = {
            'uuid': ('exact'),
            'build': ALL_WITH_RELATIONS,
            'testcaseinstancestatus': ALL_WITH_RELATIONS,
            'testcase': ALL_WITH_RELATIONS,
        }
        detail_uri_name = 'uuid'


class TargetFileGlobResource(CommonResource):
    """API Resource for 'TargetFileGlob' model.

    Attributes:
        jobtypes: To-Many relation to the JobType resource.
    """
    jobtypes = fields.ToManyField('oilserver.api.resources.JobTypeResource',
                                  'jobtypes', full=True, null=True)

    class Meta:
        queryset = models.TargetFileGlob.objects.all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['glob_pattern', 'jobtypes']
        authorization = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
        always_return_data = True
        filtering = {'glob_pattern': ALL,
                     'jobtypes': ALL_WITH_RELATIONS, }
        detail_uri_name = 'glob_pattern'


REPLACE_PREFIX = 'knownbugregex__bugoccurrences__'


def get_bugoccurrence_filters(bundle):
    """Construct and return bug occurrence filters.

    For each item in the request.GET.query_dict dictionary of bundle, find the
    queries that start with the path given in REPLACE_PREFIX and end with
    '__in', and return them with the additon of regex > bug > uuid  = uuid.

    Args:
        bundle: The tastypie bundle.

    Returns:
        bugoccurrence_filters: A dictionary .
    """
    query_dict = bundle.request.GET
    bugoccurrence_filters = {}
    for key, value in query_dict.items():
        if not key.startswith(REPLACE_PREFIX):
            continue
        filter_name = key.replace(REPLACE_PREFIX, '')

        if filter_name.endswith('__in'):
            bugoccurrence_filters[filter_name] = \
                bundle.request.GET.getlist(key)
        else:
            bugoccurrence_filters[filter_name] = value
    bugoccurrence_filters['regex__bug__uuid'] = bundle.obj.uuid
    return bugoccurrence_filters


def get_bugoccurrences(bundle):
    """Get the bug occurrences that match a bug's filter.

    When bugs are found by bug occurrence properties, this matches
    bug occurrences that match those properties. So if we filter for
    bugs with occurrences in pipelines that completed in 2015, only
    the bug occurrences that completed in 2015 will be included.

    Args:
        bundle: The tastypie bundle.
    """
    bugoccurrence_filters = get_bugoccurrence_filters(bundle)
    return models.BugOccurrence.objects.filter(**bugoccurrence_filters)


class BugTrackerBugResource(CommonResource):
    """API Resource for 'BugTrackerBug' model.

    Attributes:
        project: Foreign key to the Project resource.
    """

    project = fields.ForeignKey(
        ProjectResource, 'project', full=True, null=True)

    class Meta:
        queryset = models.BugTrackerBug.objects.select_related('project').all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['uuid', 'bug_number', 'project', 'created_at', 'updated_at']
        authorization = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
        always_return_data = True
        filtering = {'bug_number': ALL, }
        detail_uri_name = 'uuid'


class BugResource(CommonResource):
    """API Resource for 'Bug' model.

    Attributes:
        knownbugregex: To-Many relation to the KnownBugRegex resource.
        bugtrackerbug: To-One relation to the BugTrckerBug resource.
    """

    knownbugregex = fields.ToManyField(
        'oilserver.api.resources.KnownBugRegexResource',
        'knownbugregex_set', null=True)
    # FIXME: based on my experiences with Build, I think can get rid of '_set'
    # here, although I'm not sure what's using it, so cannot check...
    bugtrackerbug = fields.ToOneField(
        'oilserver.api.resources.BugTrackerBugResource',
        'bugtrackerbug', full=True, null=True)

    class Meta:
        queryset = models.Bug.objects.select_related('bugtrackerbug').all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['uuid', 'summary', 'description', 'knownbugregex',
                  'bugtrackerbug', 'created_at', 'updated_at']
        authorization = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
        always_return_data = True
        filtering = {'summary': ('contains', 'exact'),
                     'uuid': ('exact'),
                     'knownbugregex': ALL_WITH_RELATIONS,
                     'bugtrackerbug': ALL_WITH_RELATIONS, }
        detail_uri_name = 'uuid'

    def apply_filters(self, request, applicable_filters):
        fixup_set_filters(
            ['bugoccurrence', 'knownbugregex'], applicable_filters)
        return super(BugResource, self).apply_filters(
            request, applicable_filters).distinct()

    def dehydrate(self, bundle):
        bundle = super(BugResource, self).dehydrate(bundle)
        bugoccurrences = get_bugoccurrences(bundle)
        bundle.data['occurrence_count'] = bugoccurrences.count()
        if bugoccurrences.exists():
            try:
                last_seen = bugoccurrences.latest(
                    'testcaseinstance__build__pipeline__completed_at')
                bundle.data['last_seen'] =\
                    last_seen.testcaseinstance.build.pipeline.completed_at
            except AttributeError:
                bundle.data['last_seen'] = None
        return bundle


class KnownBugRegexResource(CommonResource):
    """API Resource for 'BugTrackerBug' model.

    Attributes:
        targetfileglobs: To-Many relation to the TargetFileGlobs resource.
        bug: Foreign key to the Bug resource.
        bugoccurrences: To-Many relation to the BugOccurrences resource.
    """

    targetfileglobs = fields.ToManyField(
        TargetFileGlobResource, 'targetfileglobs', full=True)
    bug = fields.ForeignKey(BugResource, 'bug', full=True, null=True)
    bugoccurrences = fields.ToManyField(
        'oilserver.api.resources.BugOccurrenceResource',
        'bugoccurrence_set', null=True, use_in='detail')

    class Meta:
        queryset = models.KnownBugRegex.objects.select_related('bug').all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['bug', 'uuid', 'regex', 'targetfileglobs', 'bugoccurrences'
                  'created_at', 'updated_at']
        authorization = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
        always_return_data = True
        filtering = {'uuid': ALL,
                     'regex': ALL,
                     'targetfileglobs': ALL_WITH_RELATIONS,
                     'bug': ALL_WITH_RELATIONS,
                     'bugoccurrences': ALL_WITH_RELATIONS}
        detail_uri_name = 'uuid'

    def apply_filters(self, request, applicable_filters):
        fixup_set_filters(['bugoccurrences'], applicable_filters)
        return super(KnownBugRegexResource, self).apply_filters(
            request, applicable_filters).distinct()


class BugOccurrenceResource(CommonResource):
    """API Resource for 'BugTrackerBug' model.

    Attributes:
        build: Foreign key to the Build resource.
        regex: Foreign key to the KnownBugRegex resource.
        testcaseinstance: Foreign key to the TestCaseInstance resource.
    """

    regex = fields.ForeignKey(KnownBugRegexResource, 'regex')
    testcaseinstance = fields.ForeignKey(
        TestCaseInstanceResource, 'testcaseinstance')

    class Meta:
        queryset = models.BugOccurrence.objects.all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['uuid', 'regex', 'testcaseinstance', 'created_at',
                  'updated_at']
        authorization = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
        always_return_data = True
        filtering = {'uuid': ALL,
                     'regex': ALL_WITH_RELATIONS,
                     'testcaseinstance': ALL_WITH_RELATIONS, }
        detail_uri_name = 'uuid'


class ReportPeriodResource(CommonResource):
    """API Resource for 'ReportPeriod' model.

    Attributes:
        build: Foreign key to the Build resource.
        regex: Foreign key to the KnownBugRegex resource.
    """

    class Meta:
        queryset = models.ReportPeriod.objects.all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['uuid', 'name', 'start_date', 'end_date', 'overall_summary']
        authorization = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
        always_return_data = True
        filtering = {'uuid': ('exact',),
                     'name': ('exact',), }
        detail_uri_name = 'uuid'


class ReportInstanceResource(CommonResource):
    """API Resource for 'ReportInstance' model.

    Attributes:
        report: Foreign key to the Report resource.
        report_period: Foreign key to the ReportPeriod resource.
    """
    report = fields.ForeignKey(ReportResource, 'report')
    report_period = fields.ForeignKey(ReportPeriodResource, 'report_period')

    class Meta:
        queryset = models.ReportInstance.objects.all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['uuid', 'specific_summary', 'report', 'report_period']
        authorization = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
        always_return_data = True
        filtering = {'uuid': ('exact',),
                     'report': ('exact',),
                     'report_period': ('exact',), }
        detail_uri_name = 'uuid'


class ReportPeriodResource(CommonResource):
    """API Resource for 'ReportPeriod' model.

    Attributes:
        build: Foreign key to the Build resource.
        regex: Foreign key to the KnownBugRegex resource.
    """

    class Meta:
        queryset = models.ReportPeriod.objects.all()
        list_allowed_methods = ['get', 'post', 'delete']  # all items
        detail_allowed_methods = ['get', 'post', 'put', 'delete']  # individual
        fields = ['uuid', 'name', 'start_date', 'end_date', 'overall_summary']
        authorization = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
        always_return_data = True
        filtering = {'uuid': ('exact',),
                     'name': ('exact',), }
        detail_uri_name = 'uuid'
