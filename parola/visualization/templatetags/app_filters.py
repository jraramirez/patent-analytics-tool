from django import template
import urllib

register = template.Library()

@register.filter(name='slash_to_underscore')
def slash_to_underscore(value):
    return value.replace('/','_')

@register.filter(name='url_decode')
def url_decode(value):
    return urllib.parse.unquote(value)
