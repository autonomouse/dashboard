import itertools
import random
from datetime import datetime, timedelta, timezone
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from oilserver import models
from collections import OrderedDict
from oilserver.management.commands.set_up_site import Command as set_up_site

TEMPEST_TESTS = [
    ('tempest',
     'tempest.scenario.test_network_basic_ops.TestNetworkBasicOps',
     'test_network_basic_ops[compute,gate,network,smoke]'),
    ('tempest',
     'tempest.thirdparty.boto.test_ec2_keys.EC2KeysTest',
     'test_create_ec2_keypair[gate,smoke]'),
    ('tempest',
     'tempest.api.compute.v3.admin.test_quotas.QuotasAdminV3TestJSON',
     'test_get_default_quotas[gate,smoke]'),
]


OIL_GUEST_OS_TESTS = [
    ('OIL guest OS',
     'oil_ci.oil_tests.verification.cloud_image.guest_OS.OILGuestOSTest',
     'test_boot_ssh_image'),
    ('OIL guest OS',
     'oil_ci.oil_tests.verification.cloud_image.guest_OS.OILGuestOSTest',
     'test_boot_ssh_intance_to_instance'),
]


DEPENDENT_JOBS = OrderedDict()

DEPENDENT_JOBS['pipeline_start'] = [[('pipeline_start', 'pipeline_start',
                                    'pipeline_start')]]
DEPENDENT_JOBS['pipeline_deploy'] = [[('pipeline_deploy', 'pipeline_deploy',
                                     'pipeline_deploy')]]
DEPENDENT_JOBS['pipeline_prepare'] = [[('pipeline_prepare', 'pipeline_prepare',
                                      'pipeline_prepare')]]
DEPENDENT_JOBS['test_cloud_image'] = [[('test_cloud_image', 'test_cloud_image',
                                      'test_cloud_image')], OIL_GUEST_OS_TESTS]

INDEPENDENT_JOBS = {
    'test_tempest_smoke': [[('test_tempest_smoke', 'test_tempest_smoke',
                           'test_tempest_smoke')], TEMPEST_TESTS],
    'test_bundletests': [[('test_bundletests', 'test_bundletests',
                         'test_bundletests')]]
}


JOB_TYPES = list(DEPENDENT_JOBS.keys()) + list(INDEPENDENT_JOBS.keys())


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


UBUNTU_VERSIONS = [
    ('precise', '12.04'),
    ('trusty', '14.04'),
]


SDN_CHOICES = [
    'nova-network-flatdhcp',
    'neutron-openvswitch',
    'neutron-contrail',
    'neutron-nvp',
    'neutron-nsx',
    'neutron-openvswitch-hyperv',
    'neutron-metaswitch',
]


COMPUTE_CHOICES = [
    'nova-kvm',
    'nova-hyperv',
    'nova-vmware',
    'nova-lxc',
]


BLOCK_STORAGE_CHOICES = [
    'cinder-iscsi',
    'cinder-ceph',
    'cinder-vmware',
    'cinder-vnx',
]


IMAGE_STORAGE_CHOICES = [
    'glance-swift',
    'glance-ceph',
]


DATABASE_CHOICES = [
    'mysql',
    'galera-cluster',
]

MAASVERSION_CHOICES = [
    'maas_2.1.0+bzr5480-0ubuntu1~16.04.1',
    'maas_2.1.2+bzr5555-0ubuntu1~16.04.1',
    'maas_2.1.3+bzr5573-0ubuntu1~16.04.1',
    'maas_2.2.0~beta1+bzr5675',
]

JUJUVERSION_CHOICES = [
    'juju_2.0-beta15-trusty-amd64',
    'juju_2.0-beta16-trusty-amd64',
    'juju_2.0-beta17-trusty-amd64',
    'juju_2.0-beta18-trusty-amd64',
    'juju_2.0-beta18-xenial-amd64',
    'juju_2.0-rc3-xenial-amd64',
    'juju_2.0.0-xenial-amd64',
    'juju_2.0.1-xenial-amd64',
    'juju_2.0.2-xenial-amd64',
    'juju_2.1-beta2-xenial-amd64',
    'juju_2.1-beta4-xenial-amd64',
]

SDNS = {choice: ['neutron-api', 'bird', 'neutron-gateway']
        for choice in SDN_CHOICES}
IMAGE_STORAGES = {choice: ['swift', 'glance']
                  for choice in IMAGE_STORAGE_CHOICES}
DATABASES = {choice: ['mysql', 'galera'] for choice in DATABASE_CHOICES}
BLOCK_STORAGES = {choice: ['cinder-vnx', 'cinder']
                  for choice in BLOCK_STORAGE_CHOICES}
COMPUTES = {choice: ['nova-cloud-controller', 'nova-compute']
            for choice in COMPUTE_CHOICES}

PRODUCT_TYPES = {
    'sdn': SDNS,
    'imagestorage': IMAGE_STORAGES,
    'database': DATABASES,
    'compute': COMPUTES,
    'blockstorage': BLOCK_STORAGES
}

MAAS_AND_JUJU = {
    'maas': MAASVERSION_CHOICES,
    'juju': JUJUVERSION_CHOICES
}

TOP_LEVEL_PRODUCTS = ['sdn', 'imagestorage', 'database', 'compute', 'blockstorage']

SW_PRODUCTS = set(itertools.chain.from_iterable(
    [choices.keys() for choices in PRODUCT_TYPES.values()]))

EXTRA_SERVICES = ['keystone', 'rabbitmq-server']

SERVICES = [
    'keystone',
    'mysql',
    'galera',
    'nova-cloud-controller',
    'rabbitmq-server',
    'nova-compute',
    'neutron-gateway',
    'neutron-api',
    'bird',
    'swift',
    'glance',
    'cinder-vnx',
    'cinder',
    'maas',
    'juju',
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


VENDORS = {
    'hp-proliant-DL360E-G8': 'HP',
    'dell-poweredge-R720XD': 'Dell',
    'cisco-c240-m3': 'Cisco', 'cisco-b260-m4': 'Cisco',
    'sm15k': 'SeaMicro',
    'nova-hyperv': 'HyperV',
    'neutron-nvp': 'VMware', 'neutron-nsx': 'VMware',
}


MACHINE_NAMES = [
    'codliver.oil',
    'engine.oil',
    'whale.oil',
    'olive.oil',
    'crude.oil'
]

CHARMS = [
    'cs:trusty/charmedimsure-001',
    'cs:trusty/princecharming-156',
    'cs:trusty/smallornamentwornonanecklace-020',
    'cs:trusty/bad90stvaboutwitches-666',
]

ENUM_MAPPINGS = [
    (models.JobType, JOB_TYPES, 'name'),
    (models.TestCaseInstanceStatus, BUILD_STATUSES, 'name'),
    (models.ServiceStatus, SERVICE_STATUSES, 'name'),
    (models.OpenstackVersion, OPENSTACK_VERSIONS, 'name'),
    (models.Project, COMPONENT_NAME, 'name'),
    (models.TargetFileGlob, TARGET_FILES, 'glob_pattern'),
    (models.ProductUnderTest, HARDWARE_COMPONENTS, 'name'),
    (models.ProductUnderTest, SW_PRODUCTS, 'name'),
    (models.ProductUnderTest, MAASVERSION_CHOICES, 'name'),
    (models.ProductUnderTest, JUJUVERSION_CHOICES, 'name'),
    (models.Vendor, set(VENDORS.values()), 'name'),
    (models.Report, set(VENDORS.values()), 'name'),
    (models.Machine, MACHINE_NAMES, 'hostname'),
    (models.JujuService, SERVICES, 'name'),
    (models.ProductType, PRODUCT_TYPES.keys(), 'name'),
    (models.ProductType, MAAS_AND_JUJU.keys(), 'name'),
    (models.ProductType, ['hardware'], 'name'),
    (models.Charm, CHARMS, 'charm_source_url'),
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


SOLUTIONTAG_CHOICES = [
    'stable',
    'custom1',
    'custom2',
]


def random_selection(items, min_=1, max_=None):
    if max_ is None:
        max_ = len(items)
    return random.sample(items, random.randint(min_, max_))


def populate_ubuntu_versions():
    for ubuntu_name, ubuntu_number in UBUNTU_VERSIONS:
        if models.UbuntuVersion.objects.filter(
                name=ubuntu_name).exists():
            continue
        ubuntu_version = models.UbuntuVersion(
            name=ubuntu_name, number=ubuntu_number)
        ubuntu_version.save()


def create_single_object(enum_class, item, key):
    if not enum_class.objects.filter(**{key: item}).exists():
        enum_class(**{key: item}).save()
    return enum_class.objects.get(**{key: item})


def populate_enum_object(enum_class, enum_list, key='name'):
    for enum in enum_list:
        create_single_object(enum_class, enum, key)


def populate_enum_objects():
    for enum_class, enum_list, key in ENUM_MAPPINGS:
        populate_enum_object(enum_class, enum_list, key)


def populate_vendors():
    for productundertest in models.ProductUnderTest.objects.all():
        if productundertest.name in VENDORS:
            productundertest.vendor = models.Vendor.objects.get(
                name=VENDORS[productundertest.name])
            productundertest.save()


def make_product(PUT_keys, producttype):
    for productundertest in PUT_keys:
        product = get_or_create(models.ProductUnderTest, name=productundertest)
        product.producttype = producttype
        product.save()

def populate_producttypes():
    for producttype in models.ProductType.objects.all():
        producttype.toplevel = True if producttype.name in TOP_LEVEL_PRODUCTS else False
        producttype.save()
        PRODUCTUNDERTESTS = PRODUCT_TYPES.get(producttype.name)
        if PRODUCTUNDERTESTS is None:
            make_product(HARDWARE_COMPONENTS, producttype)
        else:
            make_product(PRODUCTUNDERTESTS.keys(), producttype)


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


def get_random_hw_productundertest():
    product = random.choice(HARDWARE_COMPONENTS)
    return models.ProductUnderTest.objects.get(name=product)


def get_random_maas_and_juju_versions():
    maas = random.choice(MAAS_AND_JUJU['maas'])
    maas_PUT, maas_created = models.ProductUnderTest.objects.get_or_create(name=maas)
    maas_PUT.producttype = models.ProductType.objects.get(name='maas')
    maas_PUT.save()
    juju = random.choice(MAAS_AND_JUJU['juju'])
    juju_PUT, juju_created = models.ProductUnderTest.objects.get_or_create(name=juju)
    juju_PUT.producttype = models.ProductType.objects.get(name='juju')
    juju_PUT.save()
    return (maas_PUT, juju_PUT)


def make_pipeline_sw_choices():
    return {product_type: random.choice(list(products.keys()))
            for product_type, products in PRODUCT_TYPES.items()}


def get_services(sw_choices):
    for product_type, choice in sw_choices.items():
        possible_services = PRODUCT_TYPES[product_type][choice]
        chosen_services = random.sample(
            possible_services, random.randint(1, len(possible_services)))
        for service in chosen_services:
            jujuservice = models.JujuService.objects.get(name=service)
            productundertest = models.ProductUnderTest.objects.get(name=choice)
            yield (jujuservice, productundertest)
    # also give out other non-toplevel services
    extra_services = random.sample(
        EXTRA_SERVICES, random.randint(1, len(EXTRA_SERVICES)))
    for extra_service in extra_services:
        yield (models.JujuService.objects.get(name=extra_service), None)


def get_random_charm():
    charm = random.choice(CHARMS)
    return models.Charm.objects.get(charm_source_url=charm)


def get_or_create(model, **kwargs):
    return model.objects.get_or_create(**kwargs)[0]


def get_random_versionconfiguration():
    args = {
        'openstackversion': random_enum(models.OpenstackVersion),
        'ubuntuversion': random_enum(models.UbuntuVersion)
    }
    return get_or_create(models.VersionConfiguration, **args)


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


def make_bugs(target_count):
    current_count = models.Bug.objects.count()
    for i in range(current_count, target_count):
        bug = make_bug()
        make_known_bug_regex(bug)


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
        versionconfiguration=get_random_versionconfiguration(),
    )
    pipeline.save()
    return pipeline


def get_test_case_instance_status(success_rate):
    if random.random() < success_rate:
        test_case_instance_status_name = 'success'
    else:
        test_case_instance_status_name = 'failure'
    test_case_instance_status = models.TestCaseInstanceStatus.objects.get(
        name=test_case_instance_status_name)
    return test_case_instance_status


def make_bug_occurrence(testcaseinstance):
    regexes = models.KnownBugRegex.objects.all()
    regex = random.choice(regexes)
    bug_occurrence = models.BugOccurrence(
        testcaseinstance=testcaseinstance,
        knownbugregex=regex)
    bug_occurrence.save()


def make_testcaseinstance(testcase, build, success_rate):
    test_case_instance_status = get_test_case_instance_status(success_rate)
    testcaseinstance = models.TestCaseInstance(
        testcaseinstancestatus=test_case_instance_status,
        build=build,
        testcase=testcase)
    testcaseinstance.save()
    return testcaseinstance, test_case_instance_status


def make_build(pipeline, jobtype, testcases, success_rate, started_at=None):
    build = models.Build(
        pipeline=pipeline,
        jobtype=jobtype,
        build_id=random.randint(100000, 3000000),
        build_started_at=started_at)
    build.save()

    for testcase in testcases:
        testcaseinstance, test_case_instance_status = make_testcaseinstance(
            testcase, build, success_rate)

    if test_case_instance_status.name == 'failure':
        make_bug_occurrence(testcaseinstance)
        if jobtype.name == 'pipeline_deploy':
            deployments = models.JujuServiceDeployment.objects.filter(
                pipeline=pipeline)
            listified_deployments = [item for item in deployments]
            for deployment in random_selection(listified_deployments):
                deployment.success = False
                deployment.save()

    return build, test_case_instance_status


def make_testframework(framework_name):
    try:
        testframework = models.TestFramework(
            name=framework_name,
            description=framework_name,
            version='notapplicable')

        testframework.save()
    except IntegrityError:
        testframework = models.TestFramework.objects.get(name=framework_name)
    return testframework


def make_testclass(testframework, testclass_name):
    mapping = {
        'network': models.ProductType.objects.get(name='sdn'),
        'compute': models.ProductType.objects.get(name='compute')
    }
    try:
        testcaseclass = models.TestCaseClass(
            name=testclass_name,
            testframework=testframework)
        testcaseclass.save()
        for name, producttype in mapping.items():
            if name in testclass_name:
                testcaseclass.producttypes.add(producttype)
                testcaseclass.save()
    except IntegrityError:
        testcaseclass = models.TestCaseClass.objects.get(name=testclass_name)
    return testcaseclass


def make_testcase(testcaseclass, test_name):
    try:
        testcase = models.TestCase(
            name=test_name,
            testcaseclass=testcaseclass)
        testcase.save()
    except IntegrityError:
        testcase = models.TestCase.objects.get(name=test_name)
    return testcase


def make_test_framework_class_and_case(framework_name, testclass_name,
                                       test_name):
    testframework = make_testframework(framework_name)
    testcaseclass = make_testclass(testframework, testclass_name)
    return make_testcase(testcaseclass, test_name)


def make_target_file_globs(glob_pattern):
    target_file_glob = models.TargetFileGlob(
        glob_pattern=glob_pattern)
    target_file_glob.save()
    target_file_glob.jobtypes.add(get_random_job_type())
    target_file_glob.save()


def make_dependent_builds(pipeline):
    # For more realistic fake data, the 2 hour offset could be variable.
    job_start_time = pipeline.completed_at - timedelta(hours=2)
    for jobtype_name, tests in DEPENDENT_JOBS.items():
        testcases = []
        for _test in tests:
            test = random.choice(_test)
            testcase = make_test_framework_class_and_case(*test)
            testcases.append(testcase)

        build, test_case_instance_status = make_build(
            pipeline=pipeline,
            jobtype=models.JobType.objects.get(name=jobtype_name),
            testcases=testcases,
            success_rate=0.9,
            started_at=job_start_time)

        if test_case_instance_status.name == 'failure':
            return False

        # For more realistic fake data, the 15 minute offset between
        # job start times could be variable.
        job_start_time = job_start_time + timedelta(minutes=15)

    return True


def make_independent_builds(pipeline):
    for jobtype_name, tests in INDEPENDENT_JOBS.items():
        testcases = []
        for _test in tests:
            test = random.choice(_test)
            testcase = make_test_framework_class_and_case(*test)
            testcases.append(testcase)

        make_build(
            pipeline=pipeline,
            jobtype=models.JobType.objects.get(name=jobtype_name),
            testcases=testcases,
            success_rate=0.5)


def make_builds(pipeline):
    if not make_dependent_builds(pipeline):
        return
    make_independent_builds(pipeline)


def get_random_machineconfig():
    machine = get_random_machine()
    return models.MachineConfiguration.objects.filter(machine=machine)[0]


def deploy_services(pipeline_uuid, machineconfigs):
    pipeline = models.Pipeline.objects.get(uuid=pipeline_uuid)
    pipeline_sw_choices = make_pipeline_sw_choices()
    for service, sw_product in get_services(pipeline_sw_choices):
        # Pick a random charm to go with it - not entirely realistic though...
        charm = get_random_charm()
        jujuservicedeployment = models.JujuServiceDeployment(
            charm=charm,
            jujuservice=service,
            productundertest=sw_product,
            pipeline=pipeline)
        jujuservicedeployment.save()

        for unit_number in range(0, random.randint(1, 3)):
            machineconfiguration = get_random_machineconfig()
            unit = models.Unit(number=unit_number,
                               jujuservicedeployment=jujuservicedeployment,
                               machineconfiguration=machineconfiguration)
            unit.save()


def configure_machines(maas, juju):
    machineconfigs = []
    for machine in models.Machine.objects.all():
        hardware = get_random_hw_productundertest()
        machineconfiguration = models.MachineConfiguration(
            machine=machine)
        machineconfiguration.save()
        machineconfiguration.productundertests.add(hardware)
        machineconfiguration.productundertests.add(maas)
        machineconfiguration.productundertests.add(juju)
        machineconfiguration.save()
        machineconfigs.append(machineconfiguration)
    return machineconfigs


def make_pipelines(num_pipelines, machineconfigs, num_repeats=3):
    current_count = models.Pipeline.objects.count()
    solutiontags = [xxx for xxx in SOLUTIONTAG_CHOICES] * num_repeats
    num_solutions = num_solutions = len(solutiontags)
    add_solutions_to = random.sample(range(1, num_pipelines), num_solutions)
    for i in range(current_count, num_pipelines):
        pipeline = make_pipeline()
        deploy_services(pipeline, machineconfigs)
        make_builds(pipeline)
        if i in add_solutions_to:
            tag_name = solutiontags[add_solutions_to.index(i)]
            [solution_tag, st_created] = models.SolutionTag.objects.get_or_create(name=tag_name)
            [solution, s_created] = models.Solution.objects.get_or_create(
                solutiontag=solution_tag, cdo_checksum=solution_tag)
            pipeline.solution = solution
            pipeline.save()


def populate_data(num_bugs, num_pipelines):
    populate_enum_objects()
    populate_ubuntu_versions()
    (maas, juju) = get_random_maas_and_juju_versions()
    populate_producttypes()
    populate_vendors()
    make_infrastructure()
    make_bugs(num_bugs)
    machineconfigs = configure_machines(maas, juju)
    make_pipelines(num_pipelines, machineconfigs)


class Command(BaseCommand):
    help = 'Create fake application data'
    setup = set_up_site()
    setup.handle(sitename="Local Weebl")

    def handle(self, *args, **options):
        self.stdout.write('Creating fake application data!')
        populate_data(num_bugs=30, num_pipelines=1050)
