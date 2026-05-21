from django import forms
from .models import Company

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'logo', 'link', 'question_count', 'needs_white_bg']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. TCS'
            }),
            'logo': forms.ClearableFileInput(attrs={
                'class': 'form-file-input',
                'accept': 'image/*'
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
