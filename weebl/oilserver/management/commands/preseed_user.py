from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from social.apps.django_app.default.models import UserSocialAuth
from tastypie.models import ApiKey


def create_user(username, email, superuser=False):
    user, _created = User.objects.get_or_create(username=username, email=email)
    user.is_staff = True
    user.is_superuser = superuser
    user.save()
    return user


def create_social_user(user, provider, uid):
    socialuser, _created = UserSocialAuth.objects.get_or_create(user=user)
    socialuser.provider = provider
    socialuser.uid = uid
    socialuser.save()
    return socialuser


def create_apikey(user, newkey):
    apikey, _created = ApiKey.objects.get_or_create(user=user)
    apikey.key = newkey
    apikey.save()
    return apikey


class Command(BaseCommand):
    help = 'Sets up the initial superuser.'

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

    def add_arguments(self, parser):
        parser.add_argument('username')
        parser.add_argument('email')
        parser.add_argument('provider')
        parser.add_argument('uid')
        parser.add_argument('apikey')
        parser.add_argument('is_superuser')

    def handle(self, *args, **options):
        try:
            username = options['username']
            email = options['email']
            provider = options['provider']
            uid = options['uid']
            apikey = options['apikey']
            is_superuser = options.get('is_superuser', False)
        except KeyError:
            msg = 'Please supply username, email, provider, uid, '
            msg += 'apikey and is_superuser, e.g. '
            msg += 'preseed_default_superuser "CanonicalOilCiBot" '
            msg += '"oil-ci-bot@canonical.com" "ubuntu" "oil-ci-bot" '
            msg += '"xxxxxxxxxxxxxxxxxxxxxxxxxxxx", "False"'
            self.feedback(msg)
            raise
        superuser = True if is_superuser == 'True' else False
        user = create_user(username, email, superuser)
        create_social_user(user, provider, uid)
        apikey = create_apikey(user, apikey)
