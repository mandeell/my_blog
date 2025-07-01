from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    """Form for submitting comments on blog posts."""
    class Meta:
        model = Comment
        fields = ['author_name', 'author_email', 'content']