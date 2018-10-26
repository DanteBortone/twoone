from django import forms
from engage.models import Claim


class LoginForm(forms.Form):
    add_claim = forms.ModelChoiceField(queryset = Claim.objects.none())
    polarity = forms.ChoiceField(widget=forms.RadioSelect(attrs={
                                                          'onclick':'submit_form_data()',
                                                          }),
                                 choices=(('support', 'Add supporting claim',), ('refute', 'Add refuting claim',)),
                                 )
    required_text = forms.CharField(label='Include: ',
                                    required=False,
                                    widget=forms.TextInput(attrs={
                                                           'onfocusout':'submit_form_data()',
                                                           'onkeyup':'enter_pressed_submit()',
                                                           }))
    excluded_text = forms.CharField(label='Exclude: ',
                                    required=False,
                                    widget=forms.TextInput(attrs={
                                                           'onfocusout':'submit_form_data()',
                                                           'onkeyup':'enter_pressed_submit()',
                                                           }))
