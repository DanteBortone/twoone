from django.shortcuts import render, redirect
from create.forms import ClaimForm
from engage.models import Claim
import re

def create(request):
    my_warning = ""
    

    if request.method == 'POST':
        post_items = list(request.POST.keys())
        print(post_items)
        my_title = request.POST['create_claim']
        print("my_title:" + my_title)
        
        my_title = my_title.strip() # drop whitespace
        my_title = " ".join(my_title.split()) # drop double spaces
        
        # validate word count is high enough
        seperate_words = re.sub("[^\w]", " ",  my_title).split()
        if len(seperate_words) < 3: # check word count
            my_warning = "A claim requires at least 3 words."
            print(my_warning)
        
        # the same title will be allowed for now
        
        if my_warning == "":
            create_claim = Claim.create(title=my_title, user = request.user)
            create_claim.save()
            if "add" in post_items:
                print("stay here")
                form = ClaimForm()
                context = {
                    'warning':"",
                    'form': form
                }
                my_return = render(request, 'create/create.html', context)
                    
            elif "add_go" in post_items:
                print("goto create page")
                my_return = redirect('/engage/' + str(create_claim.id) + '/')
                    
        else: # there is a warning
            form = ClaimForm(request.POST)
            context = {
                'warning':my_warning,
                'form': form
            }
            my_return = render(request, 'create/create.html', context)
                
    else: # not a post
        form = ClaimForm()
        context = {
            'warning':"",
            'form': form
            }
        my_return = render(request, 'create/create.html', context)

    return my_return


# check title:
# can't be a question(eg start with what, when, where, who, whom, why,
#                           which, whomever, how, are, could, couldn't, aren't, doesn't
#                           should, shouldn't, would, wouldn't must musn't can, can't, whose,
#                           conjunctions 'or' 'and' 'but'
#                           however, therefore, finally, first second third
#                           or end with a question
# not a repeat of another one
# show others that are similar
# show warning if needed
# choice after creation: engage add another
# add definitions

# whats next
# add forum
# define terms - is there an easy place to get/select numbered definitions
# add votes for relevance ( 10 votes per agrument allows 5 ordered points 4,3,2,1,0)
# add votes for aggree disagree
# how are urls attached? 1 per support / refutation
