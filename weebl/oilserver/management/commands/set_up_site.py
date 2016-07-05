from django.core.management.base import BaseCommand
from oilserver import models
from django.contrib.sites.models import Site


def main(sitename):
    this_site = get_or_create_site(sitename)
    return get_or_create_settings(this_site)


def get_or_create_site(name):
    if Site.objects.filter(domain=name, name=name).exists():
        return Site.objects.get(domain=name, name=name)
    this_site = Site(domain=name, name=name)
    this_site.save()
    return this_site


def get_or_create_settings(site):
    if models.WeeblSetting.objects.filter(site=site).exists():
        return False
    else:
        settings = models.WeeblSetting(site=site)
        settings.save()
        return True


class Command(BaseCommand):
    help = 'Create instances of Site and Weeblsettings.'

    def feedback(self, msg):
        """ When one management script is calling another (i.e. when fake_data
        is calling this), the print statements from the called script do not
        show up. Using stdout makes them visible, but conversely this doesn't
        work when calling it directly. """
        try:
            self.stdout.write(msg)
        except AttributeError:
            print(msg)
        except Exception:
            pass

    def handle(self, *args, **options):
        try:
            sitename = options['sitename']
        except IndexError:
            msg = 'Please supply site url and name, '
            msg += 'e.g. set_up_site "ProductionWeebl"'
            self.feedback(msg)
            return

        output = main(sitename=sitename)
        self.feedback('Set up complete.')
        if output:
            self.feedback('Weeblsetting instance created.')
        else:
            self.feedback('Weeblsetting instance already exists.')

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('sitename', type=str)
