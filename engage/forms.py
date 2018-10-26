from django import forms
from engage.models import Claim


class SelectForm(forms.Form):
    def __init__(self,*args,**kwargs):
        self.selections = kwargs.pop('selections')
        self.my_required_text = kwargs.pop('my_required_text')
        self.my_excluded_text = kwargs.pop('my_excluded_text')
        super(SelectForm,self).__init__(*args,**kwargs)
        self.fields['add_claim'].queryset = self.selections
        # have to define the default entries here as well as the view
        #  this one will handle the form submissions or adding new objects and the deafault state
        #  the view will handle other changes to the selections
        if(len(self.my_required_text + self.my_excluded_text) > 0):
            if len(self.selections) == 0:
                self.fields['add_claim'].empty_label = "No claims found"
            elif len(self.selections) == 1:
                self.fields['add_claim'].empty_label = "1 claim found"
            else:
                self.fields['add_claim'].empty_label = str(len(self.selections)) + " claims found"
        else:
            self.fields['add_claim'].empty_label = "Enter text in search fields to load selections"
        self.fields['required_text'].initial = self.my_required_text
        self.fields['excluded_text'].initial = self.my_excluded_text

    add_claim = forms.ModelChoiceField(queryset = Claim.objects.none(),
                                       widget=forms.Select(attrs={
                                                           'class':'custom-select',
                                                           #'onfocus':'console.log("add_claim: onfocus")',
                                                           #'onselect':'console.log("add_claim: onselect")',
                                                           #'onclick':'console.log("add_claim: onclick")',
                                                           }))
                                       
    required_text = forms.CharField(label='Include: ',
                                    required=False,
                                    widget=forms.TextInput(attrs={
                                                           'class':'form-control',
                                                           #'onblur':'submit_form_data(),console.log("required_text: onblur")',
                                                           # onfocusout triggers twice??? onblur only triggers once
                                                           #'onfocusout':'submit_form_data(),console.log("required_text: onfocusout")',
                                                           #'onkeyup':'enter_pressed_submit()',
                                                           }))
    excluded_text = forms.CharField(label='Exclude: ',
                                    required=False,
                                    widget=forms.TextInput(attrs={
                                                           'class':'form-control',
                                                           #'onblur':'submit_form_data(),console.log("excluded_text: onblur")',
                                                           #'onkeyup':'enter_pressed_submit()',
                                                           }))
