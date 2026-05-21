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


from django.contrib.auth.models import User

class ChangeCredentialsForm(forms.Form):
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': '••••••••'}),
        label="Current Password"
    )
    new_username = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'New username (optional)'}),
        label="New Username"
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': '••••••••'}),
        required=False,
        label="New Password"
    )
    confirm_new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': '••••••••'}),
        required=False,
        label="Confirm New Password"
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise forms.ValidationError("Incorrect current password.")
        return current_password

    def clean(self):
        cleaned_data = super().clean()
        new_username = cleaned_data.get('new_username')
        new_password = cleaned_data.get('new_password')
        confirm_new_password = cleaned_data.get('confirm_new_password')

        if new_username:
            if User.objects.filter(username=new_username).exclude(pk=self.user.pk).exists():
                self.add_error('new_username', "This username is already taken.")

        if new_password or confirm_new_password:
            if new_password != confirm_new_password:
                self.add_error('confirm_new_password', "New passwords do not match.")
            elif len(new_password) < 6:
                self.add_error('new_password', "Password must be at least 6 characters.")

        if not new_username and not new_password:
            raise forms.ValidationError("Please provide a new username or a new password to update.")

        return cleaned_data

