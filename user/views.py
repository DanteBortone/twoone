from django.shortcuts import render
from engage.models import Claim, ClaimLink
from django.views.generic.base import TemplateView
from django.views.generic import ListView
from pybb.views import PaginatorMixin
from pybb import defaults
from pybb.models import Post, Topic, Forum, ForumSubscription
from django.http import HttpResponse
from itertools import chain
from django.contrib.auth.models import User

from django.urls import reverse

def topic_subscription_response(user, subscribed_item, subscribe):
    print("topic_subscription_response")
    print("subscribe: ", subscribe)
    # this is also in EngageView
    my_response = ''
    if user.is_authenticated:
        if subscribe == "true":
            if not (user in subscribed_item.subscribers.all()):
                # subscribe
                subscribed_item.subscribers.add(user)
        else:
            if user in subscribed_item.subscribers.all():
                # unsubscribe
                subscribed_item.subscribers.remove(user)
    else:
        print("Unauthenticated user just tired to make a subscription.  They should never have been given this option.")
    return HttpResponse(my_response)
    
def forum_subscription_response(user, subscribed_item, subscribe):
    print("forum_subscription_response")
    print("subscribe: ", subscribe)
    # this is also in EngageView
    my_response = ''
    if user.is_authenticated:
        # does this subscritpion exist already
        existing_subscription = ForumSubscription.objects.filter(user = user, forum = subscribed_item)
        if subscribe == "true":
            print("will attempt to subscribe..")
            if not existing_subscription:
                new_subscription = ForumSubscription()
                new_subscription.user = user
                new_subscription.forum = subscribed_item
                new_subscription.type = 1 # not going to setup subscribing to all posts for now
                new_subscription.save()
        else:
            if existing_subscription:
                existing_subscription.delete()
    else:
        print("Unauthenticated user just tired to make a subscription.  They should never have been given this option.")
    return HttpResponse(my_response)

class HomeView(PaginatorMixin, ListView):
    paginate_by = defaults.PYBB_TOPIC_PAGE_SIZE
    #template_object_name = 'post_list'
    template_name = 'subscribed_items.html'

    def post(self, request,  *args, **kwargs):
        print("HomeView POST!!!")
        my_response = ''
        if request.user.is_authenticated:
            post_items = list(request.POST.keys())
            print("post_items :", post_items)
            if 'post_action' in post_items:
                post_action = request.POST['post_action']
                print("post_action : ", post_action)
                if post_action == "forum_subscription":
                    if 'forum_id' in post_items:
                        forum = Forum.objects.filter(id = request.POST['forum_id'])[0]
                        my_response = forum_subscription_response(request.user, forum, request.POST['subscribe'])
                elif post_action == "topic_subscription":
                    print("topic_subscription");
                    if 'topic_id' in post_items:
                        topic = Topic.objects.filter(id = request.POST['topic_id'])[0]
                        my_response = topic_subscription_response(request.user, topic, request.POST['subscribe'])
                else:
                    print("HomeView - unknown post_action: ", post_action);

        return(HttpResponse(my_response))

    def get_queryset(self):
        print("HomeView: get_queryset")

        if self.request.user.is_authenticated:
            subscribed_topics = Topic.objects.filter(subscribers=self.request.user)
            posts_qs = Post.objects.filter(topic__in=subscribed_topics)
            forum_subscriptions = ForumSubscription.objects.filter(user=self.request.user)
            if forum_subscriptions:
                subscribed_forums = []
                for forum_subscription in forum_subscriptions:
                    subscribed_forums.append(forum_subscription.forum)
                print("subscribed_forums: ", subscribed_forums)
                subscribed_claims = Claim.objects.filter(forum__in=subscribed_forums)
                print("subscribed_claims: ", subscribed_claims)
                claimlinks_qs = ClaimLink.objects.filter(primary_claim__in=subscribed_claims)
                print("claimlinks_qs: ", claimlinks_qs)
            else:
                claimlinks_qs = ClaimLink.objects.none()
        else:
            posts_qs = Post.objects.all()
            claimlinks_qs = ClaimLink.objects.all()

        combined_list = list(chain(posts_qs, claimlinks_qs))
        combined_list.sort(key=lambda x: x.created, reverse=True)

        print(combined_list)
        
        return combined_list

    def get_context_data(self, **kwargs):
        # print("HomeView:get_context_data")
        ctx = super(HomeView, self).get_context_data(**kwargs)
        ctx['first_post'] = None
        ctx['my_url'] = reverse('user:homepage', current_app=self.request.resolver_match.namespace)
        return ctx



class NewView(HomeView):
    template_name = 'new_topics.html'
    
    def get_queryset(self):
        qs = ClaimLink.objects.order_by('-created')
        return qs
    
    def get_context_data(self, **kwargs):
        #print("NewView:get_context_data")
        ctx = super(NewView, self).get_context_data(**kwargs)
        ctx['my_url'] = reverse('user:new', current_app=self.request.resolver_match.namespace)
        return ctx

