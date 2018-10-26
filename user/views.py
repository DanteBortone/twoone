from django.shortcuts import render
from engage.models import Claim, ClaimLink
from django.views.generic.base import TemplateView
from django.views.generic import ListView
from pybb.views import PaginatorMixin
from pybb import defaults
from pybb.models import Post, Topic, Forum
from django.http import HttpResponse
from itertools import chain
from django.contrib.auth.models import User

from django.urls import reverse


class HomeView(PaginatorMixin, ListView):
    paginate_by = defaults.PYBB_TOPIC_PAGE_SIZE
    #template_object_name = 'post_list'
    template_name = 'subscribed_items.html'

    def subscription_response(self, subcribed_item, subscribe, **kwargs):
        print("subscribe_response")
        print("subscribe: ", subscribe)
        # this is also in EngageView
        my_response = ''
        if self.request.user.is_authenticated:
            if subscribe == "true":
                if not (self.request.user in subcribed_item.subscribers.all()):
                    # subscribe
                    subcribed_item.subscribers.add(self.request.user)
            else:
                if self.request.user in subcribed_item.subscribers.all():
                    # unsubscribe
                    subcribed_item.subscribers.remove(self.request.user)
        else:
            print("Unauthenticated user just made a subscription.  They should never have been given this option.")
            return HttpResponse(my_response)


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
                        my_response = self.subscription_response(forum, request.POST['subscribe'])
                elif post_action == "topic_subscription":
                    print("topic_subscription");
                    if 'topic_id' in post_items:
                        topic = Topic.objects.filter(id = request.POST['topic_id'])[0]
                        my_response = self.subscription_response(topic, request.POST['subscribe'])
                else:
                    print("HomeView - unknown post_action: ", post_action);

        return(HttpResponse(my_response))

    def get_queryset(self):
        print("HomeView: get_queryset")

        if self.request.user.is_authenticated:
            subscribed_topics = Topic.objects.filter(subscribers=self.request.user)
            posts_qs = Post.objects.filter(topic__in=subscribed_topics)
            subscribed_forums = Forum.objects.filter(subscribers=self.request.user)
            subscribed_claims = Claim.objects.filter(forum__in=subscribed_forums)
            claimlinks_qs = ClaimLink.objects.filter(primary_claim__in=subscribed_claims)
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

