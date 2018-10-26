from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from engage.models import *
from django.contrib.auth.models import User
from engage.forms import SelectForm
import json, re
from django.db.models import Sum
from pytz import timezone
from django.views.generic.base import TemplateView


#from pybb.models import Post


class claimlink_data:
    """ Contains all the info needed to render a supporting or refuting claim"""
    def __init__(self, displayed_claim_title,
                 displayed_claim_id,
                 link_id,
                 link_created,
                 link_bumps_sum,
                 link_user_bumps_sum,
                 topic_id,
                 topic_post_count,
                 link_rank=None,
                 ):
        self.displayed_claim_title = displayed_claim_title            # for listing the title
        self.displayed_claim_id = displayed_claim_id                  # for making the href link
        self.link_id = link_id                  # for telling which link to bump up/down in value
        self.link_created = link_created                  # for telling which link to bump up/down in value
        self.link_bumps_sum = link_bumps_sum    # for putting in the button value
        self.link_user_bumps_sum = link_user_bumps_sum  # for displaying how many votes a user has left
        self.link_rank = link_rank  # for storing the rank of the links
        self.topic_id = topic_id  # for storing the topic id
        self.topic_post_count = topic_post_count  # for storing the number of posts for each count

    def __str__(self):
        return "claim_title:%s claim_id:%s link_id:%s link_created:%s bumps:%s user_bumps:%s link_rank:%s topic_id:%s topic_post_count:%s" %(self.displayed_claim_title,
                                                          self.displayed_claim_id,
                                                          self.link_id,
                                                          self.link_created.replace(tzinfo=timezone('EST')).strftime("%Y%m%d %I:%M:%S %p %Z"),
                                                          self.link_bumps_sum,
                                                          self.link_user_bumps_sum,
                                                          self.link_rank,
                                                          self.topic_id,
                                                          self.topic_post_count
                                                        )


def vote_status(user, claim):
    user_vote = Vote.objects.filter(claim = claim).filter(user=user)
    if len(user_vote) > 0:
        if user_vote[0].direction > 0:
            return "voted_for"
        elif user_vote[0].direction < 0:
            return "voted_against"
    else:
        return(None)



def users_bumps(user, claim, my_link_type):
    #print("users_bumps")

    my_links = claim.sub_links.all().filter(primary_claim=claim).filter(link_type = my_link_type)
    return_user_bumps = []
    for my_link in my_links:
        # get all of the bumps for this supporting link
        link_user_bumps = Bump.objects.filter(claimlink = my_link, user = user)
        if link_user_bumps:
            return_user_bumps.append(link_user_bumps)
    return(return_user_bumps)



def users_remaining_bump_count(user, claim, my_link_type):
    #print("users_remaining_bump_count")
    user_bumps = users_bumps(user, claim, my_link_type)
    user_votes = []
    for user_bump in user_bumps:
        user_votes.append(user_bump.aggregate(Sum('count'))['count__sum'])
    return(MAX_BUMPS() - sum(user_votes))



def get_link_data(user, claim, my_link_type):
    #print("get_link_data")
    def package_links(link_data, user, my_links, should_reverse):
        # organizes the data form teh links
        # should_reverse is to find the links in the opposite direction
        for my_link in my_links:
            # get all of the bumps for this supporting link
            link_bumps = Bump.objects.filter(claimlink = my_link)
            link_bumps_sum = 0
            link_user_bumps_sum = 0
            if link_bumps:
                link_bumps_sum = link_bumps.aggregate(Sum('count'))['count__sum']
                if user.is_authenticated:
                    link_user_bumps = link_bumps.filter(user = user)
                    if link_user_bumps:
                        link_user_bumps_sum = link_user_bumps.aggregate(Sum('count'))['count__sum']
            if(should_reverse):
                displayed_claim_title=my_link.primary_claim.title
                displayed_claim_id=my_link.primary_claim.id
            else:
                displayed_claim_title=my_link.linked_claim.title
                displayed_claim_id=my_link.linked_claim.id

            my_claimlink_data = claimlink_data(displayed_claim_title=displayed_claim_title,
                                               displayed_claim_id=displayed_claim_id,
                                               link_id=my_link.id,
                                               link_created=my_link.created,
                                               link_bumps_sum=link_bumps_sum,
                                               link_user_bumps_sum=link_user_bumps_sum,
                                               topic_id=my_link.topic.id,
                                               topic_post_count=my_link.topic.post_count
                                               )
            #print(my_claimlink_data)
            link_data.append(my_claimlink_data)
        return(link_data)

    my_links = claim.sub_links.all().filter(link_type = my_link_type)
    my_link_data = package_links(link_data = [], user = user, my_links = my_links, should_reverse = False)
    
    if (my_link_type.is_directional == False):
        my_reverse_links = ClaimLink.objects.filter(link_type = my_link_type).filter(linked_claim = claim)
        my_link_data = package_links(link_data = my_link_data, user = user, my_links = my_reverse_links, should_reverse = True)

    my_link_data = sorted(my_link_data, key=lambda x: x.link_created, reverse=False) # this will put the older links first in the case of a tie
    my_link_data = sorted(my_link_data, key=lambda x: x.link_bumps_sum, reverse=True)
    my_rank = 0
    for link_datum in my_link_data:
        link_datum.link_rank = my_rank
        my_rank += 1
    return(my_link_data)



# function to tell what is the link_id of the place where the link will be going to
# tells where the link id will go.  the first is the id the second is the id's place to which it will move
#   jquery will use this to get the coordinates of where to more the first id
def movements_in_link_data(old_link_data, new_link_data):
    #print('movements_in_link_data...')
    output_swaps = []
    for old_link_index in range(0, len(old_link_data)):
        old_list_name = old_link_data[old_link_index].displayed_claim_title
        old_list_id = old_link_data[old_link_index].link_id
        new_list_name = new_link_data[old_link_index].displayed_claim_title
        new_list_id = new_link_data[old_link_index].link_id
        if old_list_id != new_list_id:
            output_swaps.append({"link-id-" + str(new_list_id):"link-id-" + str(old_list_id)})
    return(json.dumps(output_swaps))


# is_supporting indictes if it's the supporting_linktype, refuting_linktype
def render_claimlinks(user, claim, my_link_type):
    # print("render_claimlinks")
    # before we start looping through the links
    #   lets first figure out some things that will be true for every link

    # this is a quick patch to get rid of the is_supporting variable
    #   is_supporting should be removed entirely at some point. it's redundant in a lot of cases
    disable_add_button = True
    can_bump_this_side = False

    if not user.is_authenticated:
        up_button_class = "claims bump-btn cant-vote greyed-out"
        down_button_class = "claims bump-btn cant-vote greyed-out"
        up_tooltip = "Login to bump claims."
        down_tooltip = "Login to remove bumps from your claims."
        concluding_note = "Login to vote and bump claims."
    
    else: # user is authenticated
        # determine if the user can bump items for this relationship
        if(my_link_type != supporting_linktype() and my_link_type != refuting_linktype()):
            # users don't ahve to vote for linktype to  bump if they aren't supporting or refuting claims.
            can_bump_this_side = True
            disable_add_button = False
        else:
            # supporting and refuting bumps require that the user voted for/against it
            user_vote = Vote.objects.filter(claim = claim).filter(user=user)
            if user_vote:
                if user_vote[0].direction > 0: # if user had voted_for
                    #print("my_link_type: ", my_link_type)
                    #print("supporting_linktype: ", supporting_linktype())
                    if my_link_type == supporting_linktype():
                        can_bump_this_side = True
                        disable_add_button = False
                elif user_vote[0].direction < 0: # if user had voted_against
                    if my_link_type == refuting_linktype():
                        can_bump_this_side = True
                        disable_add_button = False

            else :
                print("render_claimlinks: User has not voted.")

        if not can_bump_this_side:
            # user is logged in but can't vote for this side
            #    either because they haven't voted at all
            #    OR they voted for the other side
            up_button_class = "claims bump-btn cant-vote greyed-out"
            down_button_class = "claims bump-btn cant-vote greyed-out"
            down_tooltip = "You may only remove your own bumps."

            if my_link_type == supporting_linktype():
                class_specific_bump_tip_text = "for"
            elif my_link_type == refuting_linktype():
                class_specific_bump_tip_text = "against"

            up_tooltip = "Vote " + class_specific_bump_tip_text + " main claim to bump items."
            concluding_note = "Vote " + class_specific_bump_tip_text + " main claim to bump items."


    # okay, now lets loop through the links

    link_data = get_link_data(user, claim, my_link_type)
    remaining_bumps = MAX_BUMPS() - sum(map(lambda x: int(x.link_user_bumps_sum), link_data))

    my_html = '<div id="' + my_link_type.title.replace(" ", "-") + '-links" class="collapse show" role="tabpanel" style="padding-top:6px">'

    if not link_data: # there are no links
        # intentionally provocative here to get opposing users to put things in if they disagree
        concluding_note = my_link_type.no_links_text()
    else:
        my_html += '<div class="claim-group">'
        my_html += '<span class="bump-span related-claim-header">Bumps</span>'
        my_html += '<span class="claim-span related-claim-header">Claim</span>'
        my_html += '<span class="post-span related-claim-header">Posts</span>'

        # first need to figure out up/down_button_class up/down_tooltip and concluding_note
        #    for these more specific cases
        user_at_max_number_of_votes = remaining_bumps == 0

        for this_claimlink in link_data:
            if user.is_authenticated: # up/down_button_class up/down_tooltip and concluding_note  when not authenticated
                if can_bump_this_side: # up/down_button_class up/down_tooltip and concluding_note  when user cant bump
                    number_of_user_votes_for_this_link = this_claimlink.link_user_bumps_sum
                    # handle the bump downs
                    if number_of_user_votes_for_this_link > 0:
                        down_button_class = "claims bump-btn can-vote has-voted-0" # has-voted-0 is the blue button
                        down_tooltip = "Remove your bumps."
                    else:
                        down_button_class = "claims bump-btn cant-vote greyed-out"
                        down_tooltip = "You may only remove your own bumps."

                    # now handle the bump ups
                    if remaining_bumps == 0:
                        concluding_note = "You have no bumps remaining."
                    elif remaining_bumps == 1:
                        concluding_note = "You have 1 bump remaining."
                    elif remaining_bumps > 1:
                        concluding_note = "You have " + str(remaining_bumps) + " bumps remaining."

                    if not user_at_max_number_of_votes:
                        up_button_class = "claims bump-btn can-vote has-voted-" + str(number_of_user_votes_for_this_link)
                        if number_of_user_votes_for_this_link > 0:
                            up_tooltip = "You have bumped this " + str(number_of_user_votes_for_this_link) + " times."
                        else:
                            up_tooltip = "Bump claim"
                    else:
                        if number_of_user_votes_for_this_link > 0:
                            up_button_class = "claims bump-btn cant-vote has-voted-" + str(number_of_user_votes_for_this_link)
                            if number_of_user_votes_for_this_link == MAX_BUMPS():#the user has spent all of their votes on this item
                                up_tooltip = "You have used all " + str(number_of_user_votes_for_this_link) + " of your bumps on this item."
                            else:
                                up_tooltip = "You have bumped this " + str(number_of_user_votes_for_this_link) + " times. Remove bumps from other items to bump this one."
                        else:
                            up_button_class = "claims bump-btn cant-vote greyed-out"
                            up_tooltip = "You have used all of your bumps.  Remove bumps from other items to bump this one."
    
            # we have all the info we need. now let's make the line for the supporting/refuting claimlink
            if "cant-vote" in up_button_class:
                disabled = "disabled"
            else:
                disabled = ""
            my_html += '<div style="position: relative;" id="link-id-'+str(this_claimlink.link_id)+'"><span class="bump-span"><button class="'+ up_button_class +'" title="' + up_tooltip + '" type="button" id="bump_up" onclick="bump(' + str(this_claimlink.link_id) + ',\'up\');" pointer-events:auto  ' + disabled + '>&#9650;</button>'
            my_html += '<font class="claims" id="vote_result" style="color:black">' + str(this_claimlink.link_bumps_sum) + '</font>'
            
            if "cant-vote" in down_button_class:
                disabled = "disabled"
            else:
                disabled = ""
            my_html += '<button class="'+ down_button_class +'" title="' + down_tooltip + '" type="button" id="bump_down" onclick="bump(' + str(this_claimlink.link_id) + ',\'down\');" pointer-events:auto ' + disabled + '>&#9660;</button></span>'
            
            my_html += '<span class="claim-span"><a class="claims" href="/engage/' + str(this_claimlink.displayed_claim_id) + '/">' + this_claimlink.displayed_claim_title + '</a></span>'
            # if it's the first post the normal topic view can't handle it so we need to append /post/add/
            first_post_append = ""
            if this_claimlink.topic_post_count == 0:
                first_post_append = '/post/add'
            my_html += '<span class="post-span"><a class="posts" href="/forum/topic/' + str(this_claimlink.topic_id) + first_post_append + '/">' + str(this_claimlink.topic_post_count) + '</a></div></span>'
    
        my_html += '</div>' # outside of for loop

    # all done with making the links.  time to close...
    my_html += '<span class="claim-list-note">' + concluding_note + '</span>'
    my_html += '<input class="btn btn-outline-secondary float-right btn-sm" style="margin-right:5px" type="submit" name="submit" value="Add" onclick="show_modal(\'' + my_link_type.add_item_text() + '\', ' + str(my_link_type.id) + ');"'
    if disable_add_button:
        my_html += ' disabled title="'+ my_link_type.disabled_add_claimlink_tooltip_text() +'"/>'
    else:
        my_html += ' title="' + my_link_type.enabled_add_claimlink_tooltip_text() + '"/>'
    my_html += '</div>'
    return(my_html)


class EngageView(TemplateView):
    template_name = 'engage/build.html'

    # if the db is flushed the linktype will return none.  need to cover for this occurance
    if supporting_linktype() is not None:
        open_tab = supporting_linktype().title.replace(" ", "-")
    else:
        open_tab = ""

    link_movements = None
    new_link_id = ""
    
    def render_all_links(self, claim):
        my_user = self.request.user
        all_links = {'rendered_supporting_links': render_claimlinks(my_user, claim, my_link_type = supporting_linktype()),
                    'rendered_refuting_links': render_claimlinks(my_user, claim, my_link_type = refuting_linktype()),
                    'rendered_similar_links': render_claimlinks(my_user, claim, my_link_type = similar_linktype()),
                    'rendered_opposite_links': render_claimlinks(my_user, claim, my_link_type = opposite_linktype())}
        return(all_links)

    def get_vote_info(self, claim):
        claim_votes = Vote.objects.filter(claim = claim)
        print(claim_votes)
        claim_vote_total = sum(v.direction for v in claim_votes)
        
        up_vote_total = sum(v.direction > 0 for v in claim_votes)
        down_vote_total = sum(v.direction < 0 for v in claim_votes) * -1

        class_vote_up = 'vote-btn cant-vote no-access'
        class_vote_down = 'vote-btn cant-vote no-access'
        
        # set the attributes of the voting arrows
        if self.request.user.is_authenticated:
            class_vote_up = 'vote-btn can-vote no-votes-yet'
            class_vote_down = 'vote-btn can-vote no-votes-yet'
            user_vote = claim_votes.filter(user=self.request.user)
            if len(user_vote) > 0:
                if user_vote[0].direction < 0:
                    class_vote_down = 'vote-btn cant-vote has-voted-for'
                if user_vote[0].direction > 0:
                    class_vote_up = 'vote-btn cant-vote has-voted-for'
            else:
                print("build: User has not voted here")
        vote_info = {'class_vote_up': class_vote_up,
                    'class_vote_down': class_vote_down,
            'claim_vote_total': str(claim_vote_total) + "("+ str(up_vote_total) + ":" + str(down_vote_total) + ")",}
        return(vote_info)

    def bump_post_response(self, claim):
        print("BUMP!!!!")
        bump_direction = self.request.POST['bump_direction']
        #print("bump_direction: %s" % bump_direction)
        this_claimlink_id = self.request.POST['claimlink_id']
        this_claimlink = ClaimLink.objects.filter(id = this_claimlink_id)[0]
        claim_link_type = this_claimlink.link_type
                    
        user_vote_status = vote_status(self.request.user, claim)
        rendered_links = ""
        old_link_data = get_link_data(self.request.user, claim, claim_link_type)
        if (claim_link_type != supporting_linktype() and (claim_link_type != refuting_linktype())):
            # anyone can bump this.
            bump_allowed = True
        else: # it IS a supporting or refuting relationship
            # The user can only bump the side they voted for.
            if (user_vote_status == "voted_for" and claim_link_type == supporting_linktype()) or \
                (user_vote_status == "voted_against" and claim_link_type == refuting_linktype()):
                bump_allowed = True
            else:
                print("The user isn't allowed to bump a side they didn't vote for.")
                bump_allowed = False
                
        if bump_direction == "up":
            print('bump_up')
            if bump_allowed:
                bumps_available = users_remaining_bump_count(self.request.user, claim, claim_link_type)
                #print("bumps_available: %s" % bumps_available)
                if bumps_available > 0:
                    previous_bumps = Bump.objects.filter(user = self.request.user, claimlink = this_claimlink)
                    if not previous_bumps:
                        # create a new bump
                        previous_bumps = Bump(user = self.request.user, claimlink = this_claimlink, count = 1)
                        previous_bumps.save()
                    else:
                        # increase amount of old bump
                        previous_bumps = previous_bumps[0]
                        previous_bumps.count += 1
                        previous_bumps.save()
                    rendered_links = render_claimlinks(self.request.user, claim, my_link_type = claim_link_type)
                else:
                    print("User has used up all of his/her votes.")
        if bump_direction == "down":
            print('bump_down')
            if bump_allowed:
                # i don't know if claim links for supporting and refuting have unique id's
                previous_bumps = Bump.objects.filter(user = self.request.user, claimlink = this_claimlink)
                if not previous_bumps:
                    print("User had no votes here to begin with. Not going to allow negative votes for now.")
                else:
                    # increase amount of old bump
                    previous_bumps = previous_bumps[0]
                    #print(previous_bumps.count)
                    previous_bumps.count -= 1
                    #print(previous_bumps.count)
                    previous_bumps.save()
                    if previous_bumps.count < 1:
                        #print('deleting_bump_object')
                        Bump.objects.get(id=previous_bumps.id).delete()
                    rendered_links = render_claimlinks(self.request.user, claim, my_link_type = claim_link_type)
                        
        # return for the bump_up/down posts
        new_link_data = get_link_data(self.request.user, claim, claim_link_type)
        link_movements = movements_in_link_data(old_link_data, new_link_data)
        print("bump link_movements: ", link_movements)

        bump_return_items = {
            'my_class': claim_link_type.title,
            'rendered_links' : rendered_links,
            'link_movements' : link_movements,
        }
        print("bump_return_items: ", bump_return_items)
        print("json.dumps(bump_return_items): ", json.dumps(bump_return_items))
        return HttpResponse(json.dumps(bump_return_items))


    def vote_post_response(self, claim):
        print("VOTE!!!!")
        link_movements = None
        vote_result = self.request.POST['vote']
        vote_required_rendered_supporting_links = ""
        vote_required_rendered_refuting_links = ""
        # this is also done in setting the attributes of the voting arrows but the vote will change here
        #   so maybe it's better to get the vote again.
        user_vote = Vote.objects.filter(claim = claim).filter(user=self.request.user)
        if user_vote:
            #print("user_vote")
            if (user_vote[0].direction < 0 and vote_result == "vote_for") or (user_vote[0].direction > 0 and vote_result == "vote_against"):
                print("they already voted one direction and are changing their vote")
                print("vote_result: %s" % vote_result)
                if(vote_result == "vote_for"):
                    # if they voted against we need to check the supporting_links and get rid of any bumps there visa versa
                    claim_link_type = refuting_linktype()
                else:
                    claim_link_type = supporting_linktype()
                possibly_lost_bumps = users_bumps(self.request.user, claim, claim_link_type)
                print("possibly_lost_bumps: %s" % possibly_lost_bumps)
                if possibly_lost_bumps:
                    old_link_data = get_link_data(self.request.user, claim, claim_link_type)
                    print("Dumping user's bumps.")
                    for lost_bump in possibly_lost_bumps:
                        lost_bump.delete()
                    new_link_data = get_link_data(self.request.user, claim, claim_link_type)
                    link_movements = movements_in_link_data(old_link_data, new_link_data)
                user_vote.delete() # delete their old vote
            else:
                print("They are trying to vote down multiple times.")

        else:
            # it's their first time voting
            if vote_result == "vote_against": # if user had voted_against
                place_vote = Vote(user=self.request.user, claim=claim, direction=-1)
                place_vote.save()
            if vote_result == "vote_for":
                place_vote = Vote(user=self.request.user, claim=claim, direction=1)
                place_vote.save()
        vote_required_rendered_supporting_links = render_claimlinks(self.request.user, claim, my_link_type = supporting_linktype())
        vote_required_rendered_refuting_links = render_claimlinks(self.request.user, claim, my_link_type = refuting_linktype())

        vote_update = {'rendered_supporting_links': vote_required_rendered_supporting_links,
                        'rendered_refuting_links': vote_required_rendered_refuting_links,
                        'link_movements': link_movements,}
        vote_update.update(self.get_vote_info(claim))
        return(HttpResponse(json.dumps(vote_update)))
            
            
    def modify_choicefield_post_response(self, claim, post_items):
        print("MODIFY_CHOICEFIELD!!!!")
        my_required_text = ""
        my_excluded_text = ""
        if 'claim_link_type_id' in post_items:
            claim_link_type = ClaimLinkType.objects.filter(id = self.request.POST['claim_link_type_id'])[0]
        else:
            print("modify_choicefield_post_response: must have a claim_link_type_id")
            HttpResponse('')
        if 'required_text' in post_items:
            my_required_text = self.request.POST['required_text']
        if 'excluded_text' in post_items:
            my_excluded_text = self.request.POST['excluded_text']
        
        my_required_text = my_required_text.strip()
        my_excluded_text = my_excluded_text.strip()

        if(len(my_required_text + my_excluded_text) > 0):
            selections = Claim.objects.exclude(id = claim.id)
            # if the link type isn't directional then the selections should also exclude the reverse
            #   ie A is similar to B, the B should exclude the A and B from it's selections.
            if selections:
                if not claim_link_type.is_directional:
                    reverse_links = ClaimLink.objects.filter(link_type = claim_link_type).filter(linked_claim = claim)
                    for reverse_link in reverse_links:
                        selections = selections.exclude(id = reverse_link.primary_claim.id)
            if(len(my_required_text) > 0):
                split_required_text = re.sub("[^\w]", " ",  my_required_text).split()
                for this_word in split_required_text:
                    selections = selections.filter(title__icontains=this_word)
            if(len(my_excluded_text) > 0):
                split_excluded_text = re.sub("[^\w]", " ",  my_excluded_text).split()
                for this_word in split_excluded_text:
                    selections = selections.exclude(title__icontains=this_word)
            remove_objects = ClaimLink.objects.filter(primary_claim = claim, link_type = claim_link_type)
            for remove_object in remove_objects:
                selections = selections.exclude(title__icontains=remove_object.linked_claim.title)

            if len(selections) == 0:
                warn_no_selections = "No claims found"
            elif len(selections) == 1:
                warn_no_selections = "1 claim found"
            else:
                warn_no_selections = str(len(selections)) + " claims found"
        else:
            warn_no_selections = "Enter text in search fields to load selections"
            selections = Claim.objects.none()

        # used when refreshing choices of argument select for pop-up modal: site_files/templates/select_modal.html
        #   the modal select button calls build.html:submit_form_data()
        my_selection_ids = list(selections.values_list('pk', flat=True))
        my_selection_titles = list(selections.values_list('title', flat=True))

        selection_update = {
            'selection_ids': my_selection_ids,
            'selection_titles': my_selection_titles,
            'warn_no_selections':warn_no_selections,
        }
        return HttpResponse(json.dumps(selection_update))

    def get_context_data(self, **kwargs):
        #print("EngageView:get_context_data")
        claim = get_object_or_404(Claim, pk=self.kwargs['pk'])
        #ctx = super(EngageView, self).get_context_data(**kwargs)
        ctx = self.get_vote_info(claim)
        ctx['claim'] = claim
        vote_info = self.get_vote_info(claim)
        #ctx.update(vote_info)
        ctx['warn_no_selections'] = "Enter text in search fields to load selections"
        ctx['link_form'] = SelectForm(selections=Claim.objects.none(),
                                  my_required_text="",
                                  my_excluded_text="",
                                  )
        ctx['open_tab'] = supporting_linktype().title.replace(" ", "-")
        #my_tv = TopicView()
        #ctx['topic'] = my_tv.get_topic(pk=1)
        
        # get the subscription status
        #print("claim.forum: ", claim.forum)
        #print("subscribed: ", self.request.user in claim.forum.subscribers.all())
        
        ctx["subscribed"] = self.request.user in claim.forum.subscribers.all()
        ctx.update(self.render_all_links(claim))
        #print('get form:', ctx['form'])
        return(ctx)

    def submit_post_response(self, claim, post_items, **kwargs):
        new_link_id = None
        print("SUBMIT!!!!")
        if 'claim_link_type_id' in post_items:
            claim_link_type = ClaimLinkType.objects.filter(id = self.request.POST['claim_link_type_id'])[0]
        else:
            print("submit_post_response: must have a claim_link_type_id")
            HttpResponse('')
        if self.request.user.is_authenticated:
            attach_claim = Claim.objects.filter(id = self.request.POST['add_claim'])[0]
            already_existing_link = ClaimLink.objects.filter(primary_claim = claim, linked_claim = attach_claim, link_type = claim_link_type)
            if already_existing_link:
                print("This connection has already been made:")
                print(already_existing_link)
            else:
                print(claim_link_type.is_directional)
                create_the_link = True
                if not claim_link_type.is_directional: # for non-directional links we need to chekc the other direction
                    print("The claim link type is not directional")
                    #then we need to check the links in the opposite direction
                    reverse_link = ClaimLink.objects.filter(primary_claim = attach_claim, linked_claim = claim, link_type = claim_link_type)
                    print("reverse link: ", reverse_link)
                    if reverse_link:
                        print("This reverse link for this exists so another will not be created. This should not have been presented as a selection choice. May indicate hacking attempt.")
                        create_the_link = False
                if create_the_link:
                    print("creating link")
                    open_tab = claim_link_type.title.replace(" ", "-")
                    new_link = ClaimLink.create(primary_claim = claim,
                                                linked_claim = attach_claim,
                                                link_type = claim_link_type,
                                                user = self.request.user)
                    new_link.save()
                    new_link_id = "link-id-" + str(new_link.id)
                    # also need to make a topic that will have the same id
        
        if new_link_id is not None:
            #my_tv = TopicView()
            #my_topic = my_tv.get_topic(pk=1)
            ctx = self.get_context_data()
            #print("dir(ctx): ", dir(ctx))
            ctx['new_link_id'] = new_link_id
            ctx['open_tab'] = claim_link_type.title.replace(" ", "-")
            return render(self.request, 'engage/build.html', ctx)
        else :
            return HttpResponse('')

    def subscribe_response(self, claim, subscribe, **kwargs):
        my_response = ''
        if self.request.user.is_authenticated:
            if subscribe == "true":
                if not (self.request.user in claim.forum.subscribers.all()):
                    # subscribe to forum
                    claim.forum.subscribers.add(self.request.user)
                    #my_response = json.dumps({'subscription_status': 'subscribed',})
            else:
                if self.request.user in claim.forum.subscribers.all():
                    # unsubscribe from forum
                    claim.forum.subscribers.remove(self.request.user)
                    #my_response = json.dumps({'subscription_status': 'unsubscribed',})
        else:
            print("Unauthenticated user just subscribed to a forum through the EngageView.  They should never have been given this option.")
        return HttpResponse(my_response)

    def post(self, request,  *args, **kwargs):
        print("POST!!!")
        my_response = HttpResponse('')
        if request.user.is_authenticated:
            post_items = list(request.POST.keys())
            if 'claim_id' in post_items:
                claim = Claim.objects.filter(id = request.POST['claim_id'])[0]
                if 'post_action' in post_items:
                    post_action = request.POST['post_action']
                    print("post_action: ", post_action)
                    if post_action == "vote":
                        my_response = self.vote_post_response(claim)
                    elif post_action == "bump":
                        my_response = self.bump_post_response(claim)
                    elif post_action == "modify_choicefield":
                        my_response = self.modify_choicefield_post_response(claim, post_items)
                    elif post_action == "subscribe":
                        my_response = self.subscribe_response(claim, request.POST['subscribe'])
                elif 'submit' in post_items:
                    my_response = self.submit_post_response(claim, post_items, **kwargs)
            else:
                print("The post has no claim_id.  What exactly do you expect me to do with this?")
        else:
            print("User is not authenticated and may not post.")
        return(my_response)



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Search
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def search(request):
    print("search request")
    # get all keys
    post_items = list(request.POST.keys())
    my_required_text = ""
    my_excluded_text = ""

    print("post_items: ", post_items)
    if request.method == 'POST':
        if 'required_text' in post_items:
            print("required_text=%s" % request.POST['required_text'])
            my_required_text = request.POST['required_text']
            my_required_text = my_required_text.strip()
        if 'excluded_text' in post_items:
            print("excluded_text=%s" % request.POST['excluded_text'])
            my_excluded_text = request.POST['excluded_text']
            my_excluded_text = my_excluded_text.strip()

        if 'submit' in post_items:
            go_to_claim = Claim.objects.filter(id = request.POST['add_claim'])[0]
            # now goto that page
            return(redirect('/engage/' + str(go_to_claim.id) + '/'))

    if(len(my_required_text + my_excluded_text) > 0):
        selections = Claim.objects.all()
        if(len(my_required_text) > 0):
            split_required_text = re.sub("[^\w]", " ",  my_required_text).split()
            for this_word in split_required_text:
                selections = selections.filter(title__icontains=this_word)
        if(len(my_excluded_text) > 0):
            split_excluded_text = re.sub("[^\w]", " ",  my_excluded_text).split()
            for this_word in split_excluded_text:
                selections = selections.exclude(title__icontains=this_word)
        if len(selections) == 0:
                warn_no_selections = "No claims found"
        elif len(selections) == 1:
            warn_no_selections = "1 claim found"
        else:
            warn_no_selections = str(len(selections)) + " claims found"
    else:
        warn_no_selections = "Enter text in search fields to load selections"
        selections = Claim.objects.none()
    if 'refresh_choices' in post_items:
        my_selection_ids = list(selections.values_list('pk', flat=True))
        my_selection_titles = list(selections.values_list('title', flat=True))
        selection_update = {
            'selection_ids': my_selection_ids,
            'selection_titles': my_selection_titles,
            'warn_no_selections':warn_no_selections,
        }
        return HttpResponse(json.dumps(selection_update))
    else:
        print("sending link form")
        link_form = SelectForm(selections=selections,
                          my_required_text=my_required_text,
                          my_excluded_text=my_excluded_text,
                          )
        context = {
            'warn_no_selections':warn_no_selections,
            'link_form': link_form
        }
        return render(request, 'engage/search.html', context)
