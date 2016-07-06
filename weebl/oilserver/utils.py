import re
import pytz
import string
import random
from copy import copy
from datetime import datetime, timedelta
from dateutil import parser
from django.utils import timezone
from uuid import uuid4
from weebl import __version__


def time_now():
    return timezone.now()


def generate_uuid():
    return str(uuid4())


def get_weebl_version():
    return __version__


def generate_random_string(n=10, uppercase=False):
    ascii = string.ascii_uppercase if uppercase else string.ascii_lowercase
    return "".join(random.choice(ascii) for i in range(n))


def generate_random_url(n=10):
    return "http://www.{}.com".format(generate_random_string(n))


def generate_random_date(limit_seconds=5000000000, when="any"):
    delta = timedelta(seconds=random.randint(0, limit_seconds))
    if when.lower() == "any":
        if random.randint(0, 9) % 2:
            when = "future"
        else:
            when = "past"
    if when.lower() == "future":
        timestamp = datetime.now() + delta
    else:
        timestamp = datetime.now() - delta
    return timestamp


def generate_random_number_as_string(length=5, not_this=None):
    minimum = int("1" + ("0" * (length - 1)))
    maximum = int("9" * length)
    n = str(random.randint(minimum, maximum))
    return n if n != str(not_this) else generate_random_number_as_string(
        length=length, not_this=not_this)


def timestamp_as_string(timestamp, ts_format='%a %d %b %y %H:%M:%S'):
    timestamp_dt = normalise_timestamp(timestamp)
    return timestamp_dt.strftime(ts_format)


def normalise_timestamp(timestamp):
    if timestamp is None:
        return

    if type(timestamp) is str:
        return parser.parse(timestamp)
    else:
        return timestamp.replace(tzinfo=None)


def time_since(timestamp):
    timestamp_dt = normalise_timestamp(timestamp)
    return timezone.now() - pytz.utc.localize(timestamp_dt)


def time_difference_less_than_x_mins(timestamp, minutes):
    return time_since(timestamp) < timedelta(minutes=minutes)


def uuid_re_pattern():
    opt = "A-Fa-f0-9"
    uuid_pattern = "[" + opt + "]{8}-?[" + opt + "]{4}-?[" + opt + "]{4}-?["
    uuid_pattern += opt + "]{4}-?[" + opt + "]{12}"
    return uuid_pattern


def uuid_check(uuid):
    regex = re.compile("^" + uuid_re_pattern(), re.I)
    match = regex.match(uuid)
    return bool(match)


def pop(dictionary, fields):
    fields = list(fields) if fields is not list else fields
    for field in fields:
        try:
            dictionary.pop(field)
        except KeyError:
            pass
    return dictionary


def object_to_dict(model):
    """Turns a model object into a dict."""
    return {k: getattr(model, k)
            for k in model._meta.get_all_field_names() if hasattr(model, k)}


def get_value(dict_, key):
    """Get either exact values from dict_ or if key is a tuple, return a tuple
    in the same order of values"""
    if not isinstance(key, tuple):
        return dict_[key]
    return tuple([dict_[k] for k in key])


def get_or_create_new_model(model, key, get_params_dict, new_params_dict=None):
    if new_params_dict is None:
        new_params_dict = get_params_dict
    model_key_values = set()
    for model_object in model.objects.all():
        model_key_values.add(get_value(object_to_dict(model_object), key))
    if get_value(get_params_dict, key) not in model_key_values:
        new_model = model(**new_params_dict)
        new_model.save()
    return model.objects.get(**get_params_dict)


def update_copy(original, new):
    """Return a copy of a dict with overridden values"""
    returns = copy(original)
    returns.update(new)
    return returns


def override_defaults(function, default_kwargs):
    """Return a function that is the same as the given one, just with different
    default kwargs. Does not run given function till the returned one is
    called.
    Example:
        def one(thing=4):
            print (thing)
        two = override_defaults(one, {'thing': 5})
        one() # prints 4
        two() # prints 5
    """
    return lambda *args, **kwargs: function(
        *args, **update_copy(default_kwargs, kwargs))
