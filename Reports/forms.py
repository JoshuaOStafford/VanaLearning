from django import forms
from Reports.models import DRC


class DRCForm(forms.ModelForm):

    class Meta:
        model = DRC
        fields = ('m1', 'm2', 'm3', 'm4', 'm5')

    m1 = forms.BooleanField(label='Appropriate Behavior')
    m2 = forms.BooleanField(label='Attentive')
    m3 = forms.NullBooleanField(label='Completed Homework')
    m4 = forms.BooleanField(label='Needed Reminders and Redirection')
    m5 = forms.BooleanField(label='Organized')