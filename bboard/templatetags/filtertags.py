from datetime import datetime

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import escape
from django.utils.safestring import mark_safe, SafeText

register = template.Library()


@register.filter
# @stringfilter
def currency(value, name='тг.'):
    # if not isinstance(value, SafeText):
    #     value = escape(value)
    return mark_safe(f'<strong>{value:.2f} {name}</strong>')


@register.filter
def truncate_half(string):
    return mark_safe(f'{str(string)[:int(len(str(string))/2)]}...')


@register.filter
def to_upper(value):
    return value.upper()

# register.filter('currency', currency)

# @register.filter(expects_localtime=True)
# def datetimefilter(value):
#     pass


# Т Е Г
@register.simple_tag()
def lst(sep, *args):
    return mark_safe(f'{sep.join(args)} (<strong>Итого: {len(args)}</strong>)')


@register.simple_tag()
def string_to_list(sep, string):
    array = list(map(str, string))
    return mark_safe(f'{sep.join(array)} (<strong>Итого: {len(array)}</strong>)')

# @register.simple_tag(takes_context=True)
# def lst(context, sep, *args):
#     pass


@register.inclusion_tag('tags/ulist.html')
def ulist(*args):
    return {'items': args}


@register.simple_tag
def current_datetime(format_string):
    return mark_safe(f'<h2>Entry Date and Time: <strong>{datetime.now().strftime(format_string)}</strong></h2>')