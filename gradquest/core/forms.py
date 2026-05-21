from django import forms
from .models import Company

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'logo', 'logo_url', 'link', 'question_count', 'needs_white_bg']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. TCS'
            }),
            'logo': forms.ClearableFileInput(attrs={
                'class': 'form-file-input',
                'accept': 'image/*'
            }),
            'logo_url': forms.URLInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. https://i.imgur.com/example.png'
            }),
            'link': forms.URLInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. https://leetcode.com/problem-list/dh5qyu77/'
            }),
            'question_count': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. 200+ Questions'
            }),
            'needs_white_bg': forms.CheckboxInput(attrs={
                'class': 'form-checkbox'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        logo = cleaned_data.get('logo')
        logo_url = cleaned_data.get('logo_url')
        if not logo and not logo_url:
            raise forms.ValidationError("Please provide either a logo file upload or a direct logo image URL.")
        return cleaned_data
