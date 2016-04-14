import re
from django.utils.safestring import mark_safe
from django import template
from django.conf import settings
from mrvapi.models import *

register = template.Library()

# settings value
@register.simple_tag
def settings_value(key):
    return getattr(settings, key, "")

class_re = re.compile(r'(?<=class=["\'])(.*)(?=["\'])')
@register.filter
def add_class(value, css_class):
    if value:
    	string = unicode(value)
    match = class_re.search(string)
    if match:
        m = re.search(r'^%s$|^%s\s|\s%s\s|\s%s$' % (css_class, css_class, 
                                                    css_class, css_class), 
                                                    match.group(1))
        print match.group(1)
        if not m:
            return mark_safe(class_re.sub(match.group(1) + " " + css_class, 
                                          string))
    else:
        return mark_safe(string.replace('>', ' class="%s">' % css_class))
    return value

@register.filter
def times(number):
    return range(1, number+1);

@register.filter
def char_range(begin, end):
    for c in xrange(ord(begin), ord(end) + 1):
        yield chr(c)

@register.filter
def meters_to_ha(val):
    if val:
        return float(val) / 10000
    return 0.0

@register.filter
def convert_point_to_text(val):
    if val:
        regex = re.compile("([-]?\d+\.\d+)")
        points = regex.findall(str(val))
        return "%s, %s" % (points[0], points[1])
    return ""

@register.filter
def convert_permissions(perm):
    if perm != None:
        if perm == 0:
            return 'Owner'
        elif perm == 1:
            return 'Administrator'
        elif perm == 2:
            return 'User'
        else:
            return 'Unknown'
    return 'Unknown'