#!/usr/bin/env python3
import os
import re
import sys
import django
import psycopg2
import psutil
import shutil
from invoke import task, run
from datetime import datetime

application = 'weebl'
local_manage_cmd = "{}/manage.py".format(application)
packaged_manage_cmd = "/usr/bin/django-admin"
manage_cmd = local_manage_cmd
python3_version = '/usr/bin/python3.5'
preamble = "WEEBL_ROOT=`pwd` PYTHONPATH=$PYTHONPATH:`pwd`"
apps = ['oilserver']
postgres_user = "postgres"
postgres_pwd = "passweebl"
test_user = "test_weebl"
prdctn_user = "weebl"
test_pwd = postgres_pwd
prdctn_pwd = postgres_pwd
test_db_name = "test_bugs_database"
prdctn_db_name = "bugs_database"
test_settings = "test_settings"
prdctn_settings = "settings"
file_loc = os.path.dirname(os.path.abspath(__file__))
deploy_path = "{}/{}".format(file_loc, application)  # change
setup_file_loc = "setup.py"
https_proxy = "http://91.189.89.33:3128"

''' REQUIRES install_deps to have been run first. '''

@task(default=True)
def list():
    """List all available tasks."""
    run("invoke --list")
    run('invoke --help')

@task(help={'database': "Type test or production",
        'server': "Defaults to 'runserver'",
        'ip-addr': "IP to run server on. Defaults to 127.0.0.1.",
        'port': "Port to run server on. Defaults to 8000.", })
def go(database, server="runserver", ip_addr="127.0.0.1", port=8000):
    """Set up and run weebl using either a test or a production database."""
    init(database)
    deploy(ip_addr, port, server)

@task(help={'database': "Type test or production", })
def init(database):
    """Set up and run weebl using either a test or a production database."""
    initialise_database(database)
    set_permissions('.')

@task
def run_tests():
    """Run unit, functional, and lint tests for each app."""
    destroy_db(test_db_name, test_pwd, force=True, backup=False)
    initialise_database("test")
    load_fixtures()
    run_lint_tests()
    for app in apps:
        run_unit_tests(app)
    run_functional_tests()

def create_the_right_db(database):
    if database == "production":
        db_name = prdctn_db_name
        db_user = prdctn_user
        pwd = prdctn_pwd
    elif database == "test":
        db_name = test_db_name
        db_user = test_user
        pwd = test_pwd

    create_db_and_user(db_name, db_user, pwd)

    return check_if_database_exists(db_name, pwd)

@task(help={'database': "Type test or production"})
def createdb(database):
    """Set up and run weebl using either a test or a production database."""
    exists = create_the_right_db(database)
    migrate()
    if exists:
        print("Database: {} already exists!".format(database))
        return
    load_fixtures("initial_settings.yaml")

@task(help={'database': "Type test or production"})
def create_empty_db(database):
    """Set up a database with the right permissions but with no tables."""
    create_the_right_db(database)

@task
def syncdb():
    """Synchronise the django database."""
    migrate()

@task
def force_stop():
    """Kill all processes associated with the application."""
    for proc in psutil.process_iter():
        if application in repr(proc.cmdline()):
            file = proc.cmdline()[1] if len(proc.cmdline()) >= 2 else None
            msg = "Killing {} process id {}"
            if file:
                msg += ", run by {}"
            try:
                proc.kill()
                print(msg.format(proc.name(), proc.pid, file))
            except:
                print("Failed to kill {} process id {}."
                      .format(proc.name(), proc.pid))

@task(help={'database': "Type test or production",
            'force': "Destroy even if cannot back up data (not recommended!)"})
def destroy(database, force=False):
    """Destroy either the test or production database and user."""
    if database == "production":
        destroy_production_data(force)
    elif database == "test":
        destroy_test_data(force)


@task(help={'database': "Type test or production",
            'dump_file_path': "Path to dump file"})
def restore_from_dump(database, dump_file_path):
    """Restore from a dump.

    Blows away the existing database first.

    To create the dump, run this as the postgres user on
    the postgresql unit:

    pg_dump -x -F t bugs_database > clean_dump
    """
    destroy(database, force=True)
    create_empty_db(database)
    if database == "production":
        db_name = prdctn_db_name
    else:
        db_name = test_db_name
    run("sudo -u postgres pg_restore -d bugs_database %s" % (dump_file_path))


@task(help={'database': "Type test or production"})
def backup_database(database, force=False):
    """Backs up database to file."""
    timestamp = datetime.now().strftime("%Y_%m_%d__%H_%M_%S")
    backup_to = "Database_backup__{}__{}.json".format(database, timestamp)
    try:
        run("{} {} dumpdata > {}".format(
            python3_version, manage_cmd, backup_to))
    except:
        msg = "Could not back up {0} database{1}."
        if force is True:
            print(msg.format(application, " - continuing anyway (force)"))
        else:
            print(msg.format(application, " - aborting"))
            return
    return backup_to

@task(help={'fixture': "Fixture to load into database"})
def load_fixtures(fixture="initial_settings.yaml"):
    """Loads up data from a fixtures file (defaults to initial_settings.yaml).
    """
    print("Adding data from {} into database".format(fixture))
    run('{} {} loaddata "{}"'.format(
        python3_version, manage_cmd, fixture))

@task()
def fake_data():
    """Generates fake data for development/debugging."""
    initialise_database("production")
    print("Creating fake data...")
    run('{} {} fake_data'.format(python3_version, manage_cmd))

@task(help={'filetype': "Format of output file (defaults to .png)"})
def schema(filetype="png"):
    """Generates an image depicting the current database schema. """
    run('{} graph_models -X TimeStampedBaseModel -E -a > {}.dot'
        .format(manage_cmd, application))
    run('dot -T{1} {0}.dot -o {0}_schema.{1}'.format(application, filetype))
    run('rm {}.dot'.format(application))
    print("Schema generated at {0}_schema.{1}".format(application, filetype))

@task(help={'username': "Username of existing user to make into a superuser.",
            'database': "Test or production. Defaults to production."})
def make_superuser(username, database="production"):
    """Converts a user into a superuser (the user must have already logged in
    at least once).
    """
    sys.path.append(deploy_path)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'weebl.settings'
    django.setup()
    from django.contrib.auth.models import User
    try:
        user = User.objects.get(username=username)
    except Exception:
        print("There is no user that matches the name: '{}'".format(username))
        users = ", ".join([user.username for user in User.objects.all()])
        if len(users):
            print("Available users are as follows: {}".format(users))
        else:
            print("No users in database - log on via UI to create a user.")
        return
    user.is_staff = True
    user.is_superuser = True
    user.save()
    print("User: '{}' has been given {} superpowers.".format(
          username, application))

@task
def run_lint_tests():
    """Runs lint tests. """
    lint_weebl()

def initialise_database(database):
    if database == "production":
        stngs = prdctn_settings
    elif database == "test":
        stngs = test_settings
    else:
        print("Please provide an option: either 'production' or 'test'")
        return
    set_postgres_password(postgres_pwd)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "{0}.{1}"
                          .format(application, stngs))
    createdb(database)

def migrate():
    """Make migrations and migrate."""
    run("{} {} makemigrations".format(python3_version, manage_cmd),
        pty=True)
    run("{} {} migrate".format(python3_version, manage_cmd),
        pty=True)

def create_production_db():
    create_db_and_user(prdctn_db_name, prdctn_user, prdctn_pwd)

def create_test_db():
    create_db_and_user(test_db_name, test_user, test_pwd)

def migrate_individual_app(application, app):
    run('{} {} makemigrations {}'.format(
        python3_version, manage_cmd, app))
    run('{} {} migrate {}'.format(python3_version, manage_cmd, app))

def destroy_test_data(force):
    rusure = "Are you sure you want to drop the test database and user?! (y/N)"
    if prompt(rusure, default='N', validate=yes_no):
        destroy_db(test_db_name, test_pwd, force=force)
        destroy_user(test_user, test_pwd)

def destroy_production_data(force):

    rusure1 = "You want to drop the PRODUCTION database (y/N)"
    rusure1 += " - are you absolutely sure about that?! (y/N)"
    rusure2 = "Really? I'll only ask one more time after this!!! (y/N)"
    rusure3 = "I don't believe you. Call me paranoid, but this is PRODUCTION "
    rusure3 += "data we're talking about! Type \"I am sure\" to proceed:\n>"
    rusure4 = "Are you sure you want to drop the user: {}?! (y/N)"

    if prompt(rusure1, default='N', validate=yes_no):
        if prompt(rusure2, default='N', validate=yes_no):
            if prompt(rusure3, default='N', validate=i_am_sure):
                destroy_db(prdctn_db_name, prdctn_pwd, force=force)
                user = prdctn_user
                if prompt(rusure4.format(user), default='N', validate=yes_no):
                    destroy_user(prdctn_user, prdctn_pwd)
                else:
                    print("User deletion aborted")
                return
    print("Phew - that was close...")

def create_db_and_user(db_name, user, pwd):
    create_user(user, pwd)
    create_database(db_name, user, pwd)

def db_cxn(sql, pwd, dbname='postgres', user='postgres', host='localhost',
           isolation_lvl=0):
    con = psycopg2.connect(dbname=dbname, user=user, host=host, password=pwd)
    con.set_isolation_level(isolation_lvl)
    cursor = con.cursor()
    try:
        cursor.execute(sql)
        response = cursor.fetchall()
    except psycopg2.ProgrammingError as e:
        response = e
    cursor.close()
    con.close()
    return response

def set_postgres_password(pwd):
    """Sets the superuser password - this is especially useful shortly after
    a new postgres installation as no default password is given and the user
    must first log in as root to change it. This should be run with 'sudo'.
    """
    sql = "alter user postgres with password '{}'".format(pwd)
    run('''sudo -u postgres psql -U postgres -d postgres -c "{}";'''
        .format(sql))

def check_if_user_exists(user, pwd):
    sql_check_user = "SELECT 1 FROM pg_roles WHERE rolname='{}'"
    sql = sql_check_user.format(user)
    try:
        return True if db_cxn(sql, pwd)[0][0] else False
    except:
        return False

def check_if_database_exists(database, pwd):
    sql = "SELECT * from pg_database where datname='{}'".format(database)
    out = db_cxn(sql, pwd)
    exists = False
    for element in out:
        if database in element:
            exists = True
    return exists

def destroy_db(database, pwd, force=False, backup=True):
    if not check_if_database_exists(database, pwd):
        print("Database '{}' does not exist!".format(database))
        return

    if backup:
        backup_to = backup_database(database, force)

    # Drop the database:
    sql = "DROP DATABASE IF EXISTS {}".format(database)
    db_cxn(sql, pwd)
    succeeded = not check_if_database_exists(database, pwd)
    if succeeded is False:
        print("Problem destroying database: {}".format(database))
    elif succeeded is True:
        msg = "Database: {} destroyed.".format(database)
        if backup and backup_to:
            msg += "Data backed up to {}".format(backup_to)
        print(msg)

def destroy_user(user, pwd):
    sql = "DROP USER IF EXISTS {}".format(user)
    db_cxn(sql, pwd)
    succeeded = not check_if_user_exists(user, pwd)
    if succeeded is False:
        print("Problem destroying user: {}".format(user))
    elif succeeded is True:
        print("User: {} destroyed".format(user))

def create_user(user, pwd):
    sql_create_user = "CREATE USER {} WITH PASSWORD '{}';"
    sql_make_superuser = "ALTER ROLE {} WITH SUPERUSER;"
    exists = check_if_user_exists(user, pwd)
    if exists:
        print("User: {} already exists".format(user))
        return
    sql1 = sql_create_user.format(user, pwd)
    db_cxn(sql1, pwd)
    succeeded = check_if_user_exists(user, pwd)
    if succeeded is False:
        print("Problem creating user: {}".format(user))
    else:
        sql2 = sql_make_superuser.format(user, pwd)
        db_cxn(sql2, pwd)
        print("User: {} created".format(user))

def create_database(database, user, pwd):
    sql_createdb = sql_create_db = "CREATE DATABASE {};".format(database, user)
    sql_user_create_db_privilege = "ALTER USER \"{}\" CREATEDB;"
    sql_grant_user_all_db_priv = "GRANT ALL PRIVILEGES ON DATABASE {} TO {};"
    db_cxn(sql_user_create_db_privilege, pwd)
    db_cxn(sql_createdb, pwd)
    db_cxn(sql_grant_user_all_db_priv, pwd)
    succeeded = check_if_database_exists(database, pwd)
    if succeeded is False:
        print("Problem creating database: {}".format(database))
    else:
        print("Database: {} created".format(database))

def prompt(message, default, validate):
    answer = input(message)
    answer = default if answer == '' else answer
    try:
        return validate(answer)
    except:
        print("\n{} is not recognised, try again:\n".format(answer))
        return prompt(message, default, validate)

def run_unit_tests(app=None):
    try:
        if app is None:
            print("Running unit tests")
            run("{} {} test".format(python3_version, manage_cmd),
                pty=True)
        else:
            print("Running functional and unit tests for {}...".format(app))
            run("{} {} test {}".format(
                python3_version, manage_cmd, app), pty=True)
        print('OK')
    except Exception as e:
        print("Some tests failed")

def lint_weebl():
    print("Running flake8 lint tests on weebl code...")
    try:
        cmd = "{1} -m flake8 --exclude={0}/tests/,"
        cmd += "{0}/{0}/wsgi.py,{0}/oilserver/migrations/ {0} --ignore=F403"
        run(cmd.format(application, python3_version), pty=True)
        print('OK')
    except Exception as e:
        print("Some tests failed")

def run_functional_tests(app=None):
    """While this could and probably should be done as part of 'manage.py test'
    selenium with webdriver for some reason is still not available for Python3.
    As a result, it is being run separately under Python2.
    """
    print("Running functional tests")
    try:
        run("python2 {}/tests_functional.py".format(application))
        print('OK')
    except Exception as e:
        print("Some tests failed")

def yes_no(val):
    YES_OR_NO = re.compile("^(y|n|yes|no)$",re.IGNORECASE)
    if YES_OR_NO.match(val):
        return val.lower() == 'y' or val.lower() == 'yes'
    raise Exception("Enter y or n")

def i_am_sure(val):
    return True if val.lower() == "i am sure" else False

def deploy(ipaddr=None, port=None, server="runserver"):
    if server == "runserver":
        deploy_with_runserver(ipaddr, port)

def deploy_with_runserver(ipaddr, port):
    result = run('{} {} {} runserver {}:{}'.format(
        preamble, python3_version, manage_cmd, ipaddr, port), pty=True)

def mkdir(directory):
    """ Make a directory, check and throw an error if failed. """
    if not os.path.isdir(directory):
        try:
            os.makedirs(directory)
        except OSError:
            if not os.path.isdir(directory):
                raise


def set_permissions(folder):
    """Walk through the weebl folder and change the owner of any files or
    folders owned by root to the user who is running weebl. This is because
    some folders such as __pycache__ often end up being owned by root and would
    otherwise mean that tools/release_package would need to be run as sudo as
    well in order for git clean to work.
    """
    sudo_id = os.environ.get('SUDO_ID', 1000)
    sudo_gid = os.environ.get('SUDO_GID', 1000)

    print("Removing root permissions from weebl subdirectories...")
    for dirpath, _, filenames in os.walk(folder):
        if os.stat(dirpath).st_uid == 0:
            chown(sudo_id, sudo_gid, dirpath)
            for filename in filenames:
                fpath = os.path.abspath(os.path.join(dirpath, filename))
                chown(sudo_id, sudo_gid, fpath)
    print("done.")

def chown(uid, gid, dirpath):
    run("sudo chown {}:{} {}".format(uid, gid, dirpath))
