from django import forms
from engage.models import Claim

class ClaimForm(forms.Form):
    create_claim = forms.CharField(label='Title: ',
                                    required=True,
                                    widget=forms.TextInput(attrs={
                                                           'class':'form-control',
                                                           }))
