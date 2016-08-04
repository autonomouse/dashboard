from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from social.apps.django_app.default.models import UserSocialAuth
from tastypie.models import ApiKey

def create_oilcibot_user(username, email):
    if User.objects.filter(username=username).exists():
        return User.objects.get(username=username)
    user = User(username=username, email=email)
    user.is_staff = True
    user.is_superuser = True
    user.save()
    return user

def create_social_user(user, provider, uid):
    if UserSocialAuth.objects.filter(user=user).exists():
        return UserSocialAuth.objects.get(user=user)
    socialuser = UserSocialAuth(user=user)
    socialuser.provider = provider
    socialuser.uid = uid
    socialuser.save()
    return socialuser

def create_apikey(user, newkey):
    if ApiKey.objects.filter(user=user).exists():
        apikey = ApiKey.objects.get(user=user)
    else:
        apikey = ApiKey(user=user)
        apikey.id = apikey.user_id
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

    def handle(self, *args, **options):
        try:
            username = options['username']
            email = options['email']
            provider = options['provider']
            uid = options['uid']
            apikey = options['apikey']
        except KeyError:
            msg = 'Please supply username, email, provider, uid, '
            msg += 'and apikey, e.g. '
            msg += 'preseed_default_superuser "CanonicalOilCiBot" '
            msg += '"oil-ci-bot@canonical.com" "ubuntu" "oil-ci-bot" '
            msg += '"xxxxxxxxxxxxxxxxxxxxxxxxxxxx"'
            self.feedback(msg)
            return False
        user = create_oilcibot_user(username, email)
        socialuser = create_social_user(user, provider, uid)
        apikey = create_apikey(user, apikey)
        return True
