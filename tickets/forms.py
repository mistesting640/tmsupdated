from django import forms
from .models import Ticket
from .models import Comment
from django.contrib.auth.models import User
from django.apps import AppConfig
class TicketForm(forms.ModelForm):

    class Meta:
        model = Ticket
        fields = ['title','description','priority','assigned_to','status']

class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ['message']

class TicketsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tickets'

    def ready(self):
        import tickets.signals  # noqa

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    full_name = forms.CharField(max_length=100)
    mobile_number = forms.CharField(max_length=15)
    business_name = forms.CharField(max_length=150)

    PROJECT_CHOICES = [
        ('TMS', 'TMS'),
        ('CRM', 'CRM'),
        ('ERP', 'ERP'),
    ]
    project = forms.ChoiceField(choices=PROJECT_CHOICES)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data