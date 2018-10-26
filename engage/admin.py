from django.contrib import admin
from .models import Claim, ClaimLink, ClaimLinkType, Vote, Bump

admin.site.register(Claim)
admin.site.register(ClaimLink)
admin.site.register(ClaimLinkType)
admin.site.register(Vote)
admin.site.register(Bump)

