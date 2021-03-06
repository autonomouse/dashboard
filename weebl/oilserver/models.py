from oilserver import utils
from django.db import models, connection
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


class MaterializedViewRefresher(models.Manager):
    def refresh(self):
        with connection.cursor() as cursor:
            cursor.execute("REFRESH MATERIALIZED VIEW %s" %
                           self.model._meta.db_table)


class MaterializedViewModel(models.Model):
    class Meta:
        abstract = True
        managed = False

    objects = MaterializedViewRefresher()


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
        default='',
        blank=True,
        null=False,
        help_text="A base URL to the data archive used.")

    def __str__(self):
        return "{} ({})".format(self.name, self.uuid)


class WeeblSetting(models.Model):
    """Settings for Weebl."""
    site = models.OneToOneField(
        Site,
        unique=True,
        null=False,
        blank=False,
        help_text="To make sure there is only ever one instance per website.")
    default_environment = models.OneToOneField(
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
    servicestatus = models.ForeignKey(ServiceStatus, related_name='jenkinses')
    external_access_url = models.URLField(
        unique=False,
        blank=True,
        null=True,
        help_text="A URL for external access to this server.")
    internal_access_url = models.URLField(
        unique=True,
        default=None,
        blank=False,
        null=False,
        help_text="A URL used internally (e.g. behind a firewall) for access \
        to this server.")
    servicestatus_updated_at = models.DateTimeField(
        default=utils.time_now,
        help_text="DateTime the service status was last updated.")

    def __str__(self):
        return self.internal_access_url


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
    jenkins = models.ForeignKey(Jenkins, related_name='buildexecutors')

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
        unique=False,
        default="",
        help_text="The numerical version of the Ubuntu system")

    class Meta:
        unique_together = (('name', 'number'),)

    def __str__(self):
        return self.name


class Project(TimeStampedBaseModel):
    """The project that a product falls under. """
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
        null=True,
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


class ProductType(TimeStampedBaseModel):
    """The type of product under test."""
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="The type of product.")
    uuid = models.CharField(
        max_length=36,
        default=utils.generate_uuid,
        unique=True,
        blank=False,
        null=False,
        help_text="UUID of this type of product.")
    toplevel = models.BooleanField(
        default=False,
        help_text="If this is a top-level config option to a pipeline.")

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
    project = models.ForeignKey(
        Project, null=True, blank=True, default=None,
        related_name='productundertests')
    vendor = models.ForeignKey(
        Vendor, null=True, blank=True, default=None,
        related_name='productundertests')
    internalcontact = models.ForeignKey(
        InternalContact, null=True, blank=True, default=None)
    producttype = models.ForeignKey(
        ProductType, null=True, blank=True, default=None,
        related_name='productundertests')
    reports = models.ManyToManyField(
        Report, null=True, blank=True, default=None,
        related_name='productundertests')

    class Meta:
        unique_together = (('name', 'vendor'),)

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


class VersionConfiguration(TimeStampedBaseModel):
    """The versions used for a pipeline."""
    uuid = models.CharField(
        max_length=36,
        default=utils.generate_uuid,
        unique=True,
        blank=False,
        null=False,
        help_text="UUID of this VersionConfiguration.")
    ubuntuversion = models.ForeignKey(
        UbuntuVersion, null=True, blank=True, default=None,
        related_name='versionconfigurations')
    openstackversion = models.ForeignKey(
        OpenstackVersion, null=True, blank=True, default=None,
        related_name='versionconfigurations')

    class Meta:
        unique_together = (('ubuntuversion', 'openstackversion'),)

    def __str__(self):
        return self.uuid


class SolutionTag(TimeStampedBaseModel):
    """The identifier used by CDO QA to refer to a given solution."""
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="The current name of the solution.")
    colour = models.CharField(
        max_length=6,
        default="56334b",
        help_text="HTML colour code (excluding the '#' prefix).")
    show = models.BooleanField(
        default=True,
        help_text="Show on front page.")

    def __str__(self):
        return self.name


class Solution(TimeStampedBaseModel):
    """The set of technologies defined by CDO QA as a solution."""
    cdo_checksum = models.CharField(
        max_length=255,
        unique=True,
        help_text="MD5 checksum used by CDO QA to identify this solution.")
    # A solution will only ever have one tag, as the name of the tag is
    # included in the cdo_checksum generation to make sure they are unique:
    solutiontag = models.ForeignKey(
        SolutionTag,
        null=True,
        blank=True,
        default=None)

    def __str__(self):
        return self.cdo_checksum


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
    solution = models.ForeignKey(
        Solution, null=True, blank=True, default=None)
    versionconfiguration = models.ForeignKey(
        VersionConfiguration, null=True, blank=True, default=None,
        related_name='pipelines')
    buildexecutor = models.ForeignKey(BuildExecutor, related_name='pipelines')

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
    machine = models.ForeignKey(
        Machine, null=True, blank=True, default=None,
        related_name='machineconfigurations')
    productundertests = models.ManyToManyField(
        ProductUnderTest, null=True, blank=True, default=None,
        related_name='machineconfigurations')

    def __str__(self):
        return self.uuid


class Charm(TimeStampedBaseModel):
    """The Juju charm used."""
    uuid = models.CharField(
        max_length=36,
        default=utils.generate_uuid,
        unique=True,
        blank=False,
        null=False,
        help_text="UUID of this Juju charm.")
    name = models.CharField(
        max_length=255,
        default="unknown",
        help_text="The name of the Juju charm.")
    charm_source_url = models.URLField(
        null=False,
        help_text="The source of this charm.")

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
    colour = models.CharField(
        max_length=6,
        default="56334b",
        help_text="HTML colour code for this job (excluding the '#' prefix).")
    order = models.IntegerField(
        default=0,
        blank=False,
        null=False,
        help_text="Order in which jobs are run/should be displayed in UI.")
    plot = models.BooleanField(
        default=False,
        help_text="Show on plots (e.g. success rate and trends graphs).")

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
    pipeline = models.ForeignKey(Pipeline, related_name='builds')
    jobtype = models.ForeignKey(JobType, related_name='builds')

    class Meta:
        unique_together = (('pipeline', 'jobtype'),)

    def __str__(self):
        return self.uuid

    @property
    def jenkins_build_url(self):
        url = self.pipeline.buildexecutor.jenkins.external_access_url
        if len(url):
            return "{}/job/{}/{}/".format(
                url.rstrip('/'), self.jobtype.name, self.build_id)
        return None


class JujuServiceDeployment(TimeStampedBaseModel):
    """The instance of the deployed Juju service."""
    uuid = models.CharField(
        max_length=36,
        default=utils.generate_uuid,
        unique=True,
        blank=False,
        null=False,
        help_text="UUID of this juju service deployment.")
    pipeline = models.ForeignKey(
        Pipeline, null=True, related_name='jujuservicedeployments')
    success = models.NullBooleanField(
        default=None,
        help_text="Whether this juju service deployed successfully.")
    jujuservice = models.ForeignKey(
        JujuService, null=True, blank=True, default=None,
        related_name='jujuservicedeployments')
    productundertest = models.ForeignKey(
        ProductUnderTest, null=True, related_name='jujuservicedeployments')
    charm = models.ForeignKey(
        Charm, null=True, related_name='jujuservicedeployments')

    class Meta:
        unique_together = (('pipeline', 'charm', 'jujuservice'),)

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
        MachineConfiguration, null=True, blank=True, default=None,
        related_name='units')
    jujuservicedeployment = models.ForeignKey(
        JujuServiceDeployment, null=True, related_name='units')

    class Meta:
        unique_together = (('number', 'jujuservicedeployment'),)

    def __str__(self):
        return self.uuid


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


class ReportSection(TimeStampedBaseModel):
    """The section of a report."""
    uuid = models.CharField(
        max_length=36,
        default=utils.generate_uuid,
        unique=True,
        blank=False,
        null=False,
        help_text="UUID of the report section.")
    name = models.CharField(
        max_length=255,
        default=None,
        unique=False,
        blank=True,
        null=True,
        help_text="The section of detailed report.")
    functionalgroup = models.CharField(
        max_length=255,
        default=None,
        unique=False,
        blank=True,
        null=True,
        help_text="The functionality this subsection tests.")

    class Meta:
        unique_together = (('name', 'functionalgroup'),)

    def __str__(self):
        return self.name + ':' + self.functionalgroup


class TestCaseClass(TimeStampedBaseModel):
    """The class of test cases, within the larger suite of Openstack tests
    used.
    """
    name = models.CharField(
        max_length=255,
        blank=False,
        null=False,
        help_text="Name of this individual test case class.")
    producttypes = models.ManyToManyField(
        ProductType, null=True, blank=True, default=None,
        related_name='testcaseclasses',
        help_text='Product types this class tests.')
    testframework = models.ForeignKey(
        TestFramework, null=True, related_name='testcaseclasses')
    reportsection = models.ForeignKey(
        ReportSection, null=True, related_name='testcaseclasses')
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


class TestCaseInstanceStatus(TimeStampedBaseModel):
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
        TestCaseClass, null=True, related_name='testcases')
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
        TestCaseInstanceStatus, null=True, blank=True, default=None,
        related_name='testcaseinstances')
    uuid = models.CharField(
        max_length=36,
        default=utils.generate_uuid,
        unique=True,
        blank=False,
        null=False,
        help_text="UUID of this TestCase.")
    build = models.ForeignKey(
        Build, default=None, related_name='testcaseinstances')
    testcase = models.ForeignKey(
        TestCase, default=None, related_name='testcaseinstances')

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
        JobType, null=True, blank=True, default=None,
        related_name='targetfileglobs')

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
    project = models.ForeignKey(
        Project, null=True, blank=True, default=None,
        related_name='bugtrackerbugs')

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
        unique=True,
        blank=True,
        null=True,
        default=None)

    def __str__(self):
        return self.uuid


class KnownBugRegex(TimeStampedBaseModel):
    """The regex used to identify a bug."""
    bug = models.ForeignKey(
        Bug, null=True, blank=True, default=None,
        related_name='knownbugregexes')
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
    targetfileglobs = models.ManyToManyField(
        TargetFileGlob, related_name='knownbugregexes')

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
        TestCaseInstance, null=True, blank=True, default=None,
        related_name='bugoccurrences')
    knownbugregex = models.ForeignKey(
        KnownBugRegex, related_name='bugoccurrences')

    class Meta:
        # Only create one BugOccurrence instance per build/regex combo:
        unique_together = (('testcaseinstance', 'knownbugregex'),)

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
    report = models.ForeignKey(Report, related_name='reportinstances')
    reportperiod = models.ForeignKey(
        ReportPeriod, related_name='reportinstances')

    class Meta:
        unique_together = (('report', 'reportperiod'),)

    def __str__(self):
        return self.uuid


class ConfigurationChoices(models.Model):
    """View of configuration choices made for pipelines."""
    pipeline = models.OneToOneField(Pipeline)
    openstackversion = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="The openstackversion choice.")
    ubuntuversion = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="The ubuntuversion choice.")
    blockstorage = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="The blockstorage choice.")
    compute = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="The compute choice.")
    database = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="The database choice.")
    imagestorage = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="The imagestorage choice.")
    sdn = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="The sdn choice.")

    class Meta:
        managed = False

    def __str__(self):
        return self.pipeline.uuid


class BugReportView(MaterializedViewModel):
    """View of bug information for reports."""
    reportname = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="The name of the corresponding report.")
    date = models.DateTimeField(
        default=None,
        blank=True,
        null=True,
        help_text="DateTime of these bugs.")
    environmentname = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="The name of the corresponding environment.")
    groupname = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="The name of the corresponding group.")
    bug = models.ForeignKey(Bug, related_name='bugreportviews')
    occurrences = models.IntegerField(
        default=0,
        blank=False,
        null=False,
        help_text="Number of occurrences of the bug.")


class PipelineReportView(MaterializedViewModel):
    """View of pipeline information for reports."""
    reportname = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="The name of the corresponding report.")
    date = models.DateTimeField(
        default=None,
        blank=True,
        null=True,
        help_text="DateTime of these bugs.")
    environmentname = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="The name of the corresponding environment.")
    numpipelines = models.IntegerField(
        default=0,
        blank=False,
        null=False,
        help_text="Number of pipelines.")
    numdeployfail = models.IntegerField(
        default=0,
        blank=False,
        null=False,
        help_text="Number of failed deploy stages.")
    numpreparefail = models.IntegerField(
        default=0,
        blank=False,
        null=False,
        help_text="Number of failed prepare stages.")
    numtestfail = models.IntegerField(
        default=0,
        blank=False,
        null=False,
        help_text="Number of failed test stages.")


class ServiceReportView(MaterializedViewModel):
    """View of service information for reports."""
    reportname = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="The name of the corresponding report.")
    date = models.DateTimeField(
        default=None,
        blank=True,
        null=True,
        help_text="DateTime of these bugs.")
    environmentname = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="The name of the corresponding environment.")
    numpipelines = models.IntegerField(
        default=0,
        blank=False,
        null=False,
        help_text="Number of pipelines.")
    producttypename = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="The name of the corresponding producttype.")
    productundertestname = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="The name of the corresponding productundertest.")
    numsuccess = models.IntegerField(
        default=0,
        blank=False,
        null=False,
        help_text="Number of successful deploys for the productundertest.")


class TestReportView(MaterializedViewModel):
    """View of test information for reports."""
    reportname = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="The name of the corresponding report.")
    date = models.DateTimeField(
        default=None,
        blank=True,
        null=True,
        help_text="DateTime of these bugs.")
    environmentname = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="The name of the corresponding environment.")
    openstackversionname = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="The name of the corresponding OpenStack version.")
    ubuntuversionname = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="The name of the corresponding Ubuntu version.")
    groupname = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Product this testcase tests.")
    subgroupname = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Functional group of the testcase.")
    testcasename = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="The name of the corresponding testcase.")
    testcaseclassname = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="The name of the corresponding testcaseclass.")
    testframeworkname = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="The name of the corresponding testframework.")
    bug = models.ForeignKey(Bug, related_name='testreportviews')
    numtestcases = models.IntegerField(
        default=0,
        blank=False,
        null=False,
        help_text="Number of total testcases ran.")
    numsuccess = models.IntegerField(
        default=0,
        blank=False,
        null=False,
        help_text="Number of successful testcases.")
    numskipped = models.IntegerField(
        default=0,
        blank=False,
        null=False,
        help_text="Number of skipped testcases.")
    numfailed = models.IntegerField(
        default=0,
        blank=False,
        null=False,
        help_text="Number of failed testcases.")
