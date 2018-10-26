from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from pybb.models import Topic, Forum, Category

# the max number of votes one can give to bump a claim up in priority
def MAX_BUMPS():
    return 10

def claim_category():
    return Category.objects.filter(name = "Claims")[0]

class Claim(models.Model):
    title = models.CharField(max_length=85)
    note = models.CharField(max_length=200, blank=True)
    pub_date = models.DateTimeField('date published', default=timezone.now)
    forum = models.ForeignKey(Forum, on_delete=models.CASCADE, related_name = 'claims', null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'claims', null=True)

    @classmethod
    def create(cls, title, user):
        print("Claim:create")
        my_forum = Forum(name = title, category = claim_category())
        my_forum.save()
        my_claim = cls(title = title,
                       forum = my_forum,
                       user = user
                       )
        return my_claim

    def __str__(self):
        return self.title


class ClaimLinkType(models.Model):
    title = models.CharField(max_length=35) # similarity
    forward_name = models.CharField(max_length=35) # is_similar_to | is_supported_by | is_refuted_by
    reverse_name = models.CharField(max_length=35) # is_similar_to | supports        | refutes
    is_directional = models.BooleanField(default=True)
    is_recursive = models.BooleanField(default=True)
    
    #add_item_text = models.CharField(max_length=35)
    #no_links_text = models.CharField(max_length=35)
    #disabled_add_claimlink_tooltip_text = models.CharField(max_length=60)
    #enabled_add_claimlink_tooltip_text = models.CharField(max_length=60)
    def add_item_text(self):
        return "Add %s" % self.title
    def no_links_text(self):
        return "Nothing %s this claim." % self.reverse_name
    def disabled_add_claimlink_tooltip_text(self):
        return "Must vote against main claim to add %s." % self.title
    def enabled_add_claimlink_tooltip_text(self):
        return "Add %s." % self.title
    
    # (eg is_similar_to and is_the_antithesis_of are non directional and not recursive)
    def __str__(self):
        return "%s" % self.title


class ClaimLink(models.Model):
    created = models.DateTimeField('date created', default=timezone.now)
    primary_claim = models.ForeignKey(Claim, on_delete=models.CASCADE, related_name = 'sub_links')
    linked_claim = models.ForeignKey(Claim, on_delete=models.CASCADE, related_name = 'super_links')
    link_type = models.ForeignKey(ClaimLinkType, on_delete=models.CASCADE, related_name = 'links')
    topic = models.OneToOneField(Topic, on_delete=models.CASCADE, related_name = 'link', null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'links', null=True)

    @classmethod
    def create(cls, primary_claim, linked_claim, link_type, user):
        print("ClaimLink:create")
        my_topic = Topic(name = linked_claim.title + " " +
                         link_type.reverse_name.upper() + " " +
                         primary_claim.title,
                         forum = primary_claim.forum,
                         user = user)
        my_topic.save()
        link = cls(primary_claim = primary_claim,
                   linked_claim = linked_claim,
                   link_type = link_type,
                   topic = my_topic,
                   user = user
                   )
        return link
    
    def __str__(self):
        return "%s %s %s" % (self.linked_claim.title, self.link_type.reverse_name.upper(), self.primary_claim.title)


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'votes')
    claim = models.ForeignKey(Claim, on_delete=models.CASCADE, related_name = 'votes')
    direction = models.IntegerField(validators=[MinValueValidator(-1), MaxValueValidator(1)])
    def __str__(self):
        if self.direction == 1:
            connecting_text = "VOTED FOR"
        elif self.direction == -1:
            connecting_text = "VOTED AGAINST"
        elif self.direction == 0:
            connecting_text = "RETRACTED VOTE ON"
        else:
            connecting_text = "INVALID VALUE"
        return "%s %s %s" % (self.user.username, connecting_text, self.claim.title)


class Bump(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'bumps')
    claimlink = models.ForeignKey(ClaimLink, on_delete=models.CASCADE, related_name = 'bumps')
    count = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(MAX_BUMPS())])
    def __str__(self):
        return "%s bumps for %s by %s" % (self.count, self.claimlink, self.user.username)


def supporting_linktype():
    my_linktype = ClaimLinkType.objects.filter(title="supporting claim")
    try:
        my_linktype
    except NameError:
        return None
    else:
        if(my_linktype):
            return my_linktype[0]
        else:
            return None

def refuting_linktype():
    my_linktype = ClaimLinkType.objects.filter(title="refuting claim")
    try:
        my_linktype
    except NameError:
        return None
    else:
        if(my_linktype):
            return my_linktype[0]
        else:
            return None

def similar_linktype():
    my_linktype = ClaimLinkType.objects.filter(title="similar claim")
    try:
        my_linktype
    except NameError:
        return None
    else:
        if(my_linktype):
            return my_linktype[0]
        else:
            return None

def opposite_linktype():
    my_linktype = ClaimLinkType.objects.filter(title="opposite claim")
    try:
        my_linktype
    except NameError:
        return None
    else:
        if(my_linktype):
            return my_linktype[0]
        else:
            return None

