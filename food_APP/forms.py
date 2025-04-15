# food_crm/food_APP/forms.py
from django import forms
from .models import B2BLead, B2CLead

class B2BForm(forms.ModelForm):
    class Meta:
        model = B2BLead
        fields = '__all__'  # Include all fields from the B2B model
        widgets = {
            'location': forms.Textarea(attrs={'rows': 3}),
            'existing_menu_budget': forms.Textarea(attrs={'rows': 3}),
        }

class B2CForm(forms.ModelForm):
    event_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = B2CLead
        fields = '__all__'  # Include all fields from the B2C model
        widgets = {
            'delivery_location': forms.Textarea(attrs={'rows': 3}),
            'menu_budget': forms.Textarea(attrs={'rows': 3}),
        }