from django import template
from pybb.models import ForumSubscription

register = template.Library()

@register.filter(name='get_class')
def get_class(value):
    return value.__class__.__name__

@register.simple_tag
def is_subscribed(user, forum):
    existing_subscription = ForumSubscription.objects.filter(user = user, forum = forum)
    if existing_subscription:
        return True
    else:
        return False
