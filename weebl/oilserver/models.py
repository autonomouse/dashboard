import textwrap
from oilserver import utils
from django.db import connection, models
from django.contrib.sites.models import Site
from weebl.__init__ import __api_version__


class TimeStampedBaseModel(models.Model):
    """Base model with timestamp information that is common to many models.
    Please note that not all models will inherit from this base model. In
    particular, any that are part of the initial fixtures file do not
    (servicestatus, testcaseinstancestatus, and jobtype).
    """

    class Meta:
        abstract = True

    created_at = models.DateTimeField(
        default=None,
        blank=True,
        null=True,
        help_text="DateTime this model instance was created.")
    updated_at = models.DateTimeField(
        default=utils.time_now,
        help_text="DateTime this model instance was last updated.")

    def save(self, *args, **kwargs):
        current_time = utils.time_now()
        if self.id is None:
            self.created_at = current_time
        self.updated_at = current_time
        return super(TimeStampedBaseModel, self).save(*args, **kwargs)


def format_partial(format_string, join=" "):
    db_name = "oilserver"
    parameters = [
        'compute',
        'sdn',
        'ubuntuversion',
        'openstackversion',
        'blockstorage',
        'imagestorage',
        'database'
    ]
    return join.join([
        format_string.format(db_name=db_name, field=field)
        for field in parameters])


class Environment(TimeStampedBaseModel):
    """The environment (e.g. Prodstack, Staging)."""
    uuid = models.CharField(
        max_length=36,
        default=utils.generate_uuid,
        unique=True,
        blank=False,
        null=False,
        help_text="UUID of environment.")
    name = models.CharField(
        max_length=255,
        unique=True,
        default=uuid.default,
        blank=True,
        null=True,
        help_text="Name of environment.")
    data_archive_url = models.URLField(
        default=None,
        blank=True,
        null=True,
        help_text="A base URL to the data archive used.")

    def __str__(self):
        return "{} ({})".format(self.name, self.uuid)

    def get_site_settings(self):
        current_site = Site.objects.get_current().id
        return WeeblSetting.objects.get(pk=current_site)

    def get_job_history(self, start_date=None):
        """Return the number of time each run config has been run in this
        environment.

        A list of tuples in the form of (run_config, count) is returned,
        where run_config is a dictionary of component->choice names and
        count is the number of times that combination of components has
        been run.
        """
        selections = format_partial(
            "{db_name}_{field}.name as {field}", join=", ")
        table_fields = format_partial(
            "{db_name}_{field}", join=", ")
        id_joins = format_partial(
            "AND {db_name}_pipeline.{field}_id = {db_name}_{field}.id")
        group_bys = format_partial("{db_name}_{field}.name", join=", ")

        if start_date is None:
            start_date_clause = ""
        else:
            start_date_clause = \
                "AND {db_name}_pipeline.created_at >= '{start_date}'".format(
                    db_name="oilserver",
                    start_date=start_date.isoformat())

        query = textwrap.dedent("""
            SELECT
            {selections},
            COUNT({db_name}_pipeline.id)
            FROM {db_name}_pipeline, {db_name}_buildexecutor,
            {db_name}_jenkins,
            {table_fields}
            WHERE
            {db_name}_pipeline.buildexecutor_id = {db_name}_buildexecutor.id
            {start_date_clause}
            AND {db_name}_buildexecutor.jenkins_id = {db_name}_jenkins.id
            AND {db_name}_jenkins.environment_id = {environment_id}
            {id_joins}
            GROUP BY {group_bys}
            ORDER BY COUNT ASC;""").format(db_name="oilserver",
                                           selections=selections,
                                           table_fields=table_fields,
                                           environment_id=self.id,
                                           id_joins=id_joins,
                                           group_bys=group_bys,
                                           start_date_clause=start_date_clause)
        cursor = connection.cursor()
        cursor.execute(query)
        description = cursor.description
        results = []
        for row in cursor.fetchall():
            row_results = {
                description[i].name: value for i, value in enumerate(row[:-1])
            }
            results.append((row_results, row[-1],))

        return results


class WeeblSetting(models.Model):
    """Settings for Weebl."""
    site = models.OneToOneField(
        Site,
        unique=True,
        null=False,
        blank=False,
        help_text="To make sure there is only ever one instance per website.")
    default_environment = models.ForeignKey(
        Environment,
        null=True,
        blank=True,
        default=None,
        help_text="The default environment to display. If none, displays all.")

    def __str__(self):
        return str(self.site)

    @property
    def weebl_version(self):
        return utils.get_weebl_version()

    @property
    def api_version(self):
        return __api_version__


class ServiceStatus(models.Model):
    """Potential states that the CI server (Jenkins) may be in (e.g. up,
    unstable, down, unknown).
    """
    name = models.CharField(
        max_length=255,
        unique=True,
        default="unknown",
        help_text="Current state of the environment.")
    description = models.TextField(
        default=None,
        blank=True,
        null=True,
        help_text="Optional description for status.")

    def __str__(self):
        return self.name


class Jenkins(TimeStampedBaseModel):
    """The Continuous Integration Server."""
    environment = models.OneToOneField(Environment)
    uuid = models.CharField(
        max_length=36,
        default=utils.generate_uuid,
        unique=True,
        blank=False,
        null=False,
        help_text="UUID of the jenkins instance.")
    servicestatus = models.ForeignKey(ServiceStatus)
    external_access_url = models.URLField(
        unique=True,
        help_text="A URL for external access to this server.")
    internal_access_url = models.URLField(
        unique=True,
        default=None,
        blank=True,
        null=True,
        help_text="A URL used internally (e.g. behind a firewall) for access \
        to this server.")
    servicestatus_updated_at = models.DateTimeField(
        default=utils.time_now,
        help_text="DateTime the service status was last updated.")

    def __str__(self):
        return self.external_access_url


class BuildExecutor(TimeStampedBaseModel):
    """The Jenkins build executor (master or slave)."""
    uuid = models.CharField(
        max_length=36,
        default=utils.generate_uuid,
        unique=True,
        blank=False,
        null=False,
        help_text="UUID of the jenkins build executor.")
    name = models.CharField(
        max_length=255,
        help_text="Name of the jenkins build executor.")
    jenkins = models.ForeignKey(Jenkins)

    class Meta:
        # Jenkins will default to naming the build_executers the same thing
        # (e.g. 'master, 'ci-oil-slave-10-0', etc) so while they must be unique
        # within the same environment/jenkins, they will only be unique when
        # combined with the environment/jenkins uuid, externally:
        unique_together = (('name', 'jenkins'),)

        # Order the build executors so they are printed in alphabetical order:
        ordering = ['name']

    def __str__(self):
        return self.uuid


class UbuntuVersion(models.Model):
    """The version of the Ubuntu operating system in a pipeline."""
    name = models.CharField(
        max_length=255,
        unique=True,
        default="",
        help_text="The name of the version of the Ubuntu system.")
    number = models.CharField(
        max_length=10,
        unique=True,
        default="",
        help_text="The numerical version of the Ubuntu system")

    def __str__(self):
        return self.name


class Project(TimeStampedBaseModel):
    """A system for tracking bugs (e.g. Launchpad). """
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Name of project.")
    uuid = models.CharField(
        max_length=36,
        default=utils.generate_uuid,
        unique=True,
        blank=False,
        null=False,
        help_text="UUID of this project.")

    def __str__(self):
        return self.uuid


class Vendor(TimeStampedBaseModel):
    """The partner responsible for the product under test. """
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="The name and/or number of the product type.")
    uuid = models.CharField(
        max_length=36,
        default=utils.generate_uuid,
        unique=True,
        blank=False,
        null=False,
        help_text="UUID of this vendor.")

    def __str__(self):
        return self.uuid


class InternalContact(TimeStampedBaseModel):
    """The Canonical employee who can be contacted regarding this product. """
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="The name and/or number of the product type.")
    staffdirectoryurl = models.URLField(
        default=None,
        blank=True,
        help_text="URL linking to Canonical staff directory.")
    uuid = models.CharField(
        max_length=36,
        default=utils.generate_uuid,
        unique=True,
        blank=False,
        null=False,
        help_text="UUID of this contact.")

    def __str__(self):
        return self.uuid


class Machine(TimeStampedBaseModel):
    """The physical or virtual machine used. """
    uuid = models.CharField(
        max_length=36,
        default=utils.generate_uuid,
        unique=True,
        blank=False,
        null=False,
        help_text="UUID of this machine.")
    hostname = models.CharField(
        max_length=255,
        default=None,
        unique=True,
        blank=True,
        null=True,
        help_text="Host name or IP address of this machine.")

    def __str__(self):
        return self.uuid


class Report(TimeStampedBaseModel):
    """A specific group of product(s) to generate reports for."""
    uuid = models.CharField(
        max_length=36,
        default=utils.generate_uuid,
        unique=True,
        blank=False,
        null=False,
        help_text="UUID of this report.")
    name = models.CharField(
        max_length=255,
        help_text="Pretty name for this report.")

    def __str__(self):
        return self.uuid


class ProductUnderTest(TimeStampedBaseModel):
    """The product that is undergoing testing, such as a piece of hardware
    sold by a vendor.
    """
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="The name of the product.")
    uuid = models.CharField(
        max_length=36,
        default=utils.generate_uuid,
        unique=True,
        blank=False,
        null=False,
        help_text="UUID of this product.")
    project = models.ForeignKey(Project, null=True, blank=True, default=None)
    vendor = models.ForeignKey(Vendor, null=True, blank=True, default=None)
    internalcontact = models.ForeignKey(
        InternalContact, null=True, blank=True, default=None)
    report = models.ManyToManyField(
        Report, null=True, blank=True, default=None)

    def __str__(self):
        return self.uuid


class OpenstackVersion(models.Model):
    """The version of OpenStack running in a pipeline."""
    name = models.CharField(
        max_length=255,
        unique=True,
        default="unknown",
        help_text="The name of the version of the OpenStack system.")

    def __str__(self):
        return self.name


class SDN(models.Model):
    """The type of SDN being used in a pipeline."""
    name = models.CharField(
        max_length=255,
        unique=True,
        default="unknown",
        help_text="The name of the software defined network.")

    def __str__(self):
        return self.name


class Compute(models.Model):
    """The type of Compute being used in a pipeline."""
    name = models.CharField(
        max_length=255,
        unique=True,
        default="unknown",
        help_text="The name of the Compute type.")

    def __str__(self):
        return self.name


class BlockStorage(models.Model):
    """The type of Block Storage being used in a pipeline."""
    name = models.CharField(
        max_length=255,
        unique=True,
        default="unknown",
        help_text="The name of the Block Storage type.")

    def __str__(self):
        return self.name


class ImageStorage(models.Model):
    """The type of Image Storage being used in a pipeline."""
    name = models.CharField(
        max_length=255,
        unique=True,
        default="unknown",
        help_text="The name of the Image Storage type.")

    def __str__(self):
        return self.name


class Database(models.Model):
    """The type of Database being used in a pipeline."""
    name = models.CharField(
        max_length=255,
        unique=True,
        default="unknown",
        help_text="The name of the Database type.")

    def __str__(self):
        return self.name


class Pipeline(TimeStampedBaseModel):
    """The pipelines currently recorded."""
    uuid = models.CharField(
        max_length=36,
        default=utils.generate_uuid,
        unique=True,
        blank=False,
        null=False,
        help_text="The pipeline ID (a UUID).")
    completed_at = models.DateTimeField(
        blank=True,
        null=True,
        default=None,
        auto_now_add=False,
        help_text="DateTime the pipeline was completed.")
    ubuntuversion = models.ForeignKey(
        UbuntuVersion, null=True, blank=True, default=None)
    openstackversion = models.ForeignKey(
        OpenstackVersion, null=True, blank=True, default=None)
    sdn = models.ForeignKey(SDN, null=True, blank=True, default=None)
    compute = models.ForeignKey(Compute, null=True, blank=True, default=None)
    blockstorage = models.ForeignKey(BlockStorage, null=True, blank=True,
                                     default=None)
    imagestorage = models.ForeignKey(ImageStorage, null=True, blank=True,
                                     default=None)
    database = models.ForeignKey(Database, null=True, blank=True, default=None)
    buildexecutor = models.ForeignKey(BuildExecutor)

    def __str__(self):
        return self.uuid


class MachineConfiguration(TimeStampedBaseModel):
    """The instance of a machine deployment, i.e. the circumstances in which a
    machine was deployed and the particular configuration used.
    """
    uuid = models.CharField(
        max_length=36,
        default=utils.generate_uuid,
        unique=True,
        blank=False,
        null=False,
        help_text="UUID of this machine.")
    machine = models.ForeignKey(Machine, null=True, blank=True, default=None)
    pipeline = models.ForeignKey(Pipeline, null=True, blank=True, default=None)
    productundertest = models.ManyToManyField(
        ProductUnderTest, null=True, blank=True, default=None)

    def __str__(self):
        return self.uuid


class JujuService(TimeStampedBaseModel):
    """The service, as defined by Juju."""
    uuid = models.CharField(
        max_length=36,
        default=utils.generate_uuid,
        unique=True,
        blank=False,
        null=False,
        help_text="UUID of this Juju service.")
    name = models.CharField(
        max_length=255,
        unique=True,
        default="unknown",
        help_text="The name of the Juju service.")
    productundertest = models.ForeignKey(
        ProductUnderTest, null=True, blank=True, default=None)

    def __str__(self):
        return self.uuid


class JujuServiceDeployment(TimeStampedBaseModel):
    """The instance of the deployed Juju service."""
    uuid = models.CharField(
        max_length=36,
        default=utils.generate_uuid,
        unique=True,
        blank=False,
        null=False,
        help_text="UUID of this juju service deployment.")
    jujuservice = models.ForeignKey(
        JujuService, null=True, blank=True, default=None)

    def __str__(self):
        return self.uuid


class Unit(TimeStampedBaseModel):
    """The unit, as defined by Juju."""
    uuid = models.CharField(
        max_length=36,
        default=utils.generate_uuid,
        unique=True,
        blank=False,
        null=False,
        help_text="UUID of this unit.")
    number = models.IntegerField(
        default=0,
        blank=False,
        null=False,
        help_text="Number of this unit (unit is: service_name/unit_number).")
    machineconfiguration = models.ForeignKey(
        MachineConfiguration, null=True, blank=True, default=None)
    jujuservicedeployment = models.ForeignKey(
        JujuServiceDeployment, null=True, blank=True, default=None)

    class Meta:
        unique_together = (('number', 'jujuservicedeployment'),)

    def __str__(self):
        return self.uuid


class JobType(models.Model):
    """The type of job run (e.g. pipeline_deploy, pipeline_prepare,
    test_tempest_smoke).
    """
    name = models.CharField(
        max_length=255,
        unique=True,
        default="pipeline_deploy",
        help_text="The type of job.")
    description = models.TextField(
        default=None,
        blank=True,
        null=True,
        help_text="Optional description of job type.")

    def __str__(self):
        return self.name


class Build(TimeStampedBaseModel):
    """The build numbers for each job."""
    uuid = models.CharField(
        max_length=36,
        default=utils.generate_uuid,
        unique=True,
        blank=False,
        null=False,
        help_text="UUID of this build.")
    build_id = models.CharField(
        max_length=255,
        help_text="The build number or other identifier used by jenkins.")
    build_started_at = models.DateTimeField(
        default=None,
        blank=True,
        null=True,
        help_text="DateTime the build was started.")
    build_finished_at = models.DateTimeField(
        default=None,
        blank=True,
        null=True,
        help_text="DateTime the build finished.")
    build_analysed_at = models.DateTimeField(
        default=None,
        blank=True,
        null=True,
        help_text="DateTime build analysed by weebl, or None if unanalysed.")
    pipeline = models.ForeignKey(Pipeline)
    jobtype = models.ForeignKey(JobType)

    class Meta:
        unique_together = (('pipeline', 'jobtype'),)

    def __str__(self):
        return self.uuid

    @property
    def jenkins_build_url(self):
        url = self.pipeline.buildexecutor.jenkins.external_access_url
        return "{}/job/{}/{}/".format(
            url.rstrip('/'), self.jobtype.name, self.build_id)


class TestFramework(TimeStampedBaseModel):
    """The suite of Openstack tests used."""
    name = models.CharField(
        max_length=255,
        blank=False,
        null=False,
        help_text="Name of the testing framework.")
    description = models.TextField(
        default=None,
        blank=True,
        null=True,
        help_text="Optional description for this test framework.")
    version = models.TextField(
        default=None,
        blank=True,
        null=True,
        help_text="Version of this test framework.")
    uuid = models.CharField(
        max_length=36,
        default=utils.generate_uuid,
        unique=True,
        blank=False,
        null=False,
        help_text="UUID of this test framework and version.")

    class Meta:
        unique_together = (('name', 'version'),)

    def __str__(self):
        return "{}_{}".format(self.name, self.version)


class TestCaseClass(TimeStampedBaseModel):
    """The class of test cases, within the larger suite of Openstack tests
    used.
    """
    name = models.CharField(
        max_length=255,
        blank=False,
        null=False,
        help_text="Name of this individual test case.")
    testframework = models.ForeignKey(
        TestFramework, null=True, blank=True, default=None)
    uuid = models.CharField(
        max_length=36,
        default=utils.generate_uuid,
        unique=True,
        blank=False,
        null=False,
        help_text="UUID of this testcaseclass.")

    class Meta:
        unique_together = (('name', 'testframework'),)

    def __str__(self):
        return self.name


class TestCaseInstanceStatus(models.Model):
    """Potential states that the build may be in following being run on the CI
    server (Jenkins; e.g. success, failure, aborted, unknown).
    """
    name = models.CharField(
        max_length=255,
        unique=True,
        default="unknown",
        help_text="The resulting outcome of the test.")
    description = models.TextField(
        default=None,
        blank=True,
        null=True,
        help_text="Optional description for outcome.")

    def __str__(self):
        return self.name


class TestCase(TimeStampedBaseModel):
    """The individual test case - part of the larger suite of Openstack tests
    used.
    """
    name = models.CharField(
        max_length=255,
        blank=False,
        null=False,
        help_text="Name of this individual test case.")
    testcaseclass = models.ForeignKey(
        TestCaseClass, null=True, blank=True, default=None)
    uuid = models.CharField(
        max_length=36,
        default=utils.generate_uuid,
        unique=True,
        blank=False,
        null=False,
        help_text="UUID of this testcase.")

    class Meta:
        unique_together = (('name', 'testcaseclass'),)

    def __str__(self):
        return self.name


class TestCaseInstance(TimeStampedBaseModel):
    """Potential states that the build may be in following being run on the CI
    server (Jenkins; e.g. success, failure, aborted, unknown).
    """
    testcaseinstancestatus = models.ForeignKey(
        TestCaseInstanceStatus, null=True, blank=True, default=None)
    uuid = models.CharField(
        max_length=36,
        default=utils.generate_uuid,
        unique=True,
        blank=False,
        null=False,
        help_text="UUID of this TestCase.")
    build = models.ForeignKey(Build, default=None)
    testcase = models.ForeignKey(TestCase, default=None)

    class Meta:
        unique_together = (('testcase', 'build'),)

    def __str__(self):
        return self.uuid


class TargetFileGlob(TimeStampedBaseModel):
    """The target file."""
    glob_pattern = models.TextField(
        unique=True,
        help_text="Glob pattern used to match one or more target files.")
    jobtypes = models.ManyToManyField(
        JobType, null=True, blank=True, default=None)

    def __str__(self):
        return self.glob_pattern


class BugTrackerBug(TimeStampedBaseModel):
    """An error that has resulted in an incorrect or unexpected behaviour or
    result, externally recorded on a bug-tracker (such as Launchpad).
    """
    bug_number = models.IntegerField(
        unique=True,
        blank=False,
        null=False,
        help_text="Designation of this bug (e.g. Launchpad bug number).")
    uuid = models.CharField(
        max_length=36,
        default=utils.generate_uuid,
        unique=True,
        blank=False,
        null=False,
        help_text="UUID of this bug.")
    project = models.ForeignKey(Project, null=True, blank=True, default=None)

    def __str__(self):
        return self.uuid


class Bug(TimeStampedBaseModel):
    """An error in OIL that has resulted in an incorrect or unexpected
    behaviour or result.
    """
    uuid = models.CharField(
        max_length=36,
        default=utils.generate_uuid,
        unique=True,
        blank=False,
        null=False,
        help_text="UUID of this bug.")
    summary = models.CharField(
        max_length=255,
        unique=True,
        default=uuid.default,
        help_text="Brief overview of bug.")
    description = models.TextField(
        default=None,
        blank=True,
        null=True,
        help_text="Full description of bug.")
    bugtrackerbug = models.OneToOneField(
        BugTrackerBug,
        help_text="Bug tracker bug associated with this bug.",
        blank=True,
        null=True,
        default=None)

    def __str__(self):
        return self.uuid


class KnownBugRegex(TimeStampedBaseModel):
    """The regex used to identify a bug."""
    bug = models.ForeignKey(Bug, null=True, blank=True, default=None)
    uuid = models.CharField(
        max_length=36,
        default=utils.generate_uuid,
        unique=True,
        blank=False,
        null=False,
        help_text="UUID of this pattern.")
    # While regex must be unique, it can be set to multiple target files:
    regex = models.TextField(
        unique=True,
        help_text="The regular expression used to identify a bug occurrence.")
    targetfileglobs = models.ManyToManyField(TargetFileGlob)

    def __str__(self):
        return self.uuid


class BugOccurrence(TimeStampedBaseModel):
    """The occurrence of a bug."""
    uuid = models.CharField(
        max_length=36,
        default=utils.generate_uuid,
        unique=True,
        blank=False,
        null=False,
        help_text="UUID of this bug occurrence.")
    testcaseinstance = models.ForeignKey(
        TestCaseInstance, null=True, blank=True, default=None)
    regex = models.ForeignKey(KnownBugRegex)

    class Meta:
        # Only create one BugOccurrence instance per build/regex combo:
        unique_together = (('testcaseinstance', 'regex'),)

    def __str__(self):
        return self.uuid


class ReportPeriod(TimeStampedBaseModel):
    """Time period for a set of reports"""
    uuid = models.CharField(
        max_length=36,
        default=utils.generate_uuid,
        unique=True,
        blank=False,
        null=False,
        help_text="UUID of this time range.")
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Pretty name for time range.")
    start_date = models.DateTimeField(
        default=None,
        help_text="Start DateTime reports of this period will cover.")
    end_date = models.DateTimeField(
        default=None,
        help_text="End DateTime reports of this period will cover.")
    overall_summary = models.TextField(
        default=None,
        blank=True,
        null=True,
        help_text="Summary text for time period.")

    def __str__(self):
        return self.uuid


class ReportInstance(TimeStampedBaseModel):
    """The instance of a report."""
    uuid = models.CharField(
        max_length=36,
        default=utils.generate_uuid,
        unique=True,
        blank=False,
        null=False,
        help_text="UUID of this report instance.")
    specific_summary = models.TextField(
        default=None,
        blank=True,
        null=True,
        help_text="Summary text for specific report.")
    report = models.ForeignKey(Report)
    report_period = models.ForeignKey(ReportPeriod)

    def __str__(self):
        return self.uuid
