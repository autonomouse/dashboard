import random

from datetime import (
    datetime,
    timedelta,
    timezone, )

from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from oilserver import models


DEPENDENT_JOBS = [
    'pipeline_start',
    'pipeline_deploy',
    'pipeline_prepare',
    'test_cloud_image'
]


INDEPENDENT_JOBS = [
    'test_tempest_smoke',
    'test_bundletests',
]


JOB_TYPES = DEPENDENT_JOBS + INDEPENDENT_JOBS


BUILD_STATUSES = [
    'unknown',
    'success',
    'failure',
    'aborted',
]


SERVICE_STATUSES = [
    'unknown',
    'up',
    'unstable',
    'down',
]


OPENSTACK_VERSIONS = [
    'havana',
    'icehouse',
    'juno',
    'kilo',
]


SDNS = [
    'nova-network-flatdhcp',
    'neutron-openvswitch',
    'neutron-contrail',
    'neutron-nvp',
    'neutron-nsx',
    'neutron-openvswitch-hyperv',
    'neutron-metaswitch',
]


UBUNTU_VERSIONS = [
    ('precise', '12.04'),
    ('trusty', '14.04'),
]


COMPUTES = [
    'nova-kvm',
    'nova-hyperv',
    'nova-vmware',
    'nova-lxc',
]


BLOCK_STORAGES = [
    'cinder-iscsi',
    'cinder-ceph',
    'cinder-vmware',
    'cinder-vnx',
]


IMAGE_STORAGES = [
    'glance-swift',
    'glance-ceph',
]


DATABASES = [
    'mysql',
    'galera-cluster',
]


COMPONENT_NAME = [
    'neutron',
    'oil-ci',
    'qdaemon',
    'maas',
    'juju',
    'juju-deployer',
    'nova',
    'ceph',
    'kernel',
    'glance',
    'swift',
    'keystone',
]

TARGET_FILES = [
    'console.txt',
    'juju_debug_log.txt'
]

HARDWARE_COMPONENTS = [
    'hp-proliant-DL360E-G8',
    'dell-poweredge-R720XD',
    'cisco-c240-m3',
    'sm15k',
    'cisco-b260-m4'
]

MACHINE_NAMES = [
    'codliver.oil',
    'engine.oil',
    'whale.oil',
    'olive.oil',
    'crude.oil'
]


ENUM_MAPPINGS = [
    (models.JobType, JOB_TYPES, 'name'),
    (models.BuildStatus, BUILD_STATUSES, 'name'),
    (models.ServiceStatus, SERVICE_STATUSES, 'name'),
    (models.OpenstackVersion, OPENSTACK_VERSIONS, 'name'),
    (models.SDN, SDNS, 'name'),
    (models.Compute, COMPUTES, 'name'),
    (models.BlockStorage, BLOCK_STORAGES, 'name'),
    (models.ImageStorage, IMAGE_STORAGES, 'name'),
    (models.Database, DATABASES, 'name'),
    (models.Project, COMPONENT_NAME, 'name'),
    (models.TargetFileGlob, TARGET_FILES, 'glob_pattern'),
    (models.ProductUnderTest, HARDWARE_COMPONENTS, 'name'),
    (models.Machine, MACHINE_NAMES, 'hostname'),
]


FAILURE_VERB = [
    'failed to',
    'did not',
    'reported failure to',
    'crashed while attempting to',
]


OBJECT = [
    'start up',
    'shut down',
    'restart',
    'join cluster',
    'sync disks',
    'restart networking',
    'end process',
    'restart charm',
]


def populate_ubuntu_versions():
    for ubuntu_name, ubuntu_number in UBUNTU_VERSIONS:
        if models.UbuntuVersion.objects.filter(
                name=ubuntu_name).exists():
            continue
        ubuntu_version = models.UbuntuVersion(
            name=ubuntu_name, number=ubuntu_number)
        ubuntu_version.save()


def populate_enum_object(enum_class, enum_list, key='name'):
    for enum in enum_list:
        if enum_class.objects.filter(**{key: enum}).exists():
            continue
        enum_class(**{key: enum}).save()


def populate_enum_objects():
    for enum_class, enum_list, key in ENUM_MAPPINGS:
        populate_enum_object(enum_class, enum_list, key)


def make_environment():
    if models.Environment.objects.exists():
        return
    models.Environment(name='Sample Environment').save()


def make_jenkins():
    if models.Jenkins.objects.exists():
        return

    models.Jenkins(environment=models.Environment.objects.first(),
                   servicestatus=models.ServiceStatus.objects.get(name='up'),
                   external_access_url='https://oil-jenkins.canonical.com/'
                   ).save()


def make_build_executor():
    if models.BuildExecutor.objects.exists():
        return

    models.BuildExecutor(name='unknown',
                         jenkins=models.Jenkins.objects.first(),
                         ).save()


def make_infrastructure():
    make_environment()
    make_jenkins()
    make_build_executor()


def make_bugtrackerbug(component):
    while True:
        try:
            bug_number = random.randint(100000, 3000000)
            project = models.Project.objects.get(name=component)
            bugtrackerbug = models.BugTrackerBug(
                bug_number=bug_number,
                project=project)
            bugtrackerbug.save()
            return bugtrackerbug
        except IntegrityError:
            pass


def get_random_target_file_glob():
    glob_pattern = random.choice(TARGET_FILES)
    return models.TargetFileGlob.objects.get(glob_pattern=glob_pattern)


def get_random_job_type():
    job_type = random.choice(JOB_TYPES)
    return models.JobType.objects.get(name=job_type)


def get_random_machine():
    machine = random.choice(MACHINE_NAMES)
    return models.Machine.objects.get(hostname=machine)


def get_random_productundertest():
    product = random.choice(HARDWARE_COMPONENTS)
    return models.ProductUnderTest.objects.get(name=product)


def make_bug():
    component = random.choice(COMPONENT_NAME)
    while True:
        try:
            summary = "%s %s %s" % (
                component,
                random.choice(FAILURE_VERB),
                random.choice(OBJECT),
            )
            bug = models.Bug(
                summary=summary,
                bugtrackerbug=make_bugtrackerbug(component)
            )
            bug.save()
        except IntegrityError:
            pass
        else:
            break
    return bug


def random_regex():
    return "%s{%s}-%s(%s)" % (
        random.randint(0, 100000),
        random.randint(0, 100000),
        random.randint(0, 100000),
        random.randint(0, 100000), )


def make_known_bug_regex(bug):
    while True:
        try:
            regex = random_regex()
            known_bug_regex = models.KnownBugRegex(
                bug=bug,
                regex=regex)
            known_bug_regex.save()
            known_bug_regex.targetfileglobs.add(get_random_target_file_glob())
            known_bug_regex.save()
        except IntegrityError:
            pass
        else:
            break

    return known_bug_regex


def make_bugs():
    target_count = 30
    current_count = models.Bug.objects.count()
    for i in range(current_count, target_count):
        bug = make_bug()
        known_bug_regex = make_known_bug_regex(bug)


def random_date(start, end):
    return start + timedelta(
        seconds=random.randint(0, int((end - start).total_seconds())))


def random_enum(enum_class):
    enum_values = enum_class.objects.all()
    return random.choice(enum_values)


def make_pipeline():
    completed_at = random_date(
        datetime(2015, 1, 1, tzinfo=timezone.utc),
        datetime.now(timezone.utc))
    pipeline = models.Pipeline(
        completed_at=completed_at,
        buildexecutor=models.BuildExecutor.objects.first(),
        openstackversion=random_enum(models.OpenstackVersion),
        ubuntuversion=random_enum(models.UbuntuVersion),
        sdn=random_enum(models.SDN),
        compute=random_enum(models.Compute),
        blockstorage=random_enum(models.BlockStorage),
        imagestorage=random_enum(models.ImageStorage),
        database=random_enum(models.Database),
    )
    pipeline.save()
    return pipeline


def get_build_status(success_rate):
    if random.random() < success_rate:
        build_status_name = 'success'
    else:
        build_status_name = 'failure'
    build_status = models.BuildStatus.objects.get(
        name=build_status_name)
    return build_status


def make_bug_occurrence(build):
    regexes = models.KnownBugRegex.objects.all()
    regex = random.choice(regexes)
    bug_occurrence = models.BugOccurrence(
        build=build,
        regex=regex)
    bug_occurrence.save()


def make_build(pipeline, jobtype, success_rate):
    build_status = get_build_status(success_rate)
    build = models.Build(
        pipeline=pipeline,
        buildstatus=build_status,
        jobtype=jobtype,
        build_id=random.randint(100000, 3000000))
    build.save()

    if build_status.name == 'failure':
        make_bug_occurrence(build)

    return build


def make_target_file_globs(glob_pattern):
    target_file_glob = models.TargetFileGlob(
        glob_pattern=glob_pattern)
    target_file_glob.save()
    target_file_glob.jobtypes.add(get_random_job_type())
    target_file_glob.save()


def make_dependent_builds(pipeline):
    for jobtype_name in DEPENDENT_JOBS:
        build = make_build(
            pipeline=pipeline,
            jobtype=models.JobType.objects.get(name=jobtype_name),
            success_rate=0.9)

        if build.buildstatus.name == 'failure':
            return False

    return True


def make_independent_builds(pipeline):
    for jobtype_name in INDEPENDENT_JOBS:
        make_build(
            pipeline=pipeline,
            jobtype=models.JobType.objects.get(name=jobtype_name),
            success_rate=0.5)


def make_builds(pipeline):
    if not make_dependent_builds(pipeline):
        return

    make_independent_builds(pipeline)


def make_hardware(pipeline):
    for _ in range(random.randint(1,5)):
        pl = models.Pipeline.objects.get(uuid=pipeline)
        machine_configuration = models.MachineConfiguration(
            pipeline=pl,
            machine=get_random_machine())
        machine_configuration.save()
        for _ in range(random.randint(1,2)):
            machine_configuration.productundertest.add(
                get_random_productundertest())
            machine_configuration.save()


def make_pipelines():
    target_count = 1050
    current_count = models.Pipeline.objects.count()
    for i in range(current_count, target_count):
        pipeline = make_pipeline()
        make_builds(pipeline)
        make_hardware(pipeline)

def populate_data():
    populate_enum_objects()
    populate_ubuntu_versions()
    make_infrastructure()
    make_bugs()
    make_pipelines()


class Command(BaseCommand):
    help = 'Create fake application data'

    def add_arguments(self, parser):
        parser.add_argument('poll_id', nargs='+', type=int)

    def handle(self, *args, **options):
        self.stdout.write('Creating fake application data!')
        populate_data()
