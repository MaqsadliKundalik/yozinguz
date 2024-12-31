from django import forms
from .models import Post, Comment, Profile, Tag
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
import re

class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email manzilingiz'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Foydalanuvchi nomi'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Parol'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Parolni tasdiqlang'
        })

class PostForm(forms.ModelForm):
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Teglarni probel bilan ajrating (masalan: yangiliklar texnologiya dasturlash)'
        })
    )

    class Meta:
        model = Post
        fields = ['title', 'content', 'image', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Post sarlavhasi'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Post matnini kiriting...',
                'rows': 5
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }

    def clean_tags(self):
        tags = self.cleaned_data.get('tags', '')
        if not tags:
            return []
        
        tag_list = [tag.strip() for tag in tags.split() if tag.strip()]
        
        def slugify(text):
            cyrillic_to_latin = {
                'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
                'ж': 'j', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
                'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
                'ф': 'f', 'х': 'x', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch', 'ъ': '',
                'ы': 'i', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'
            }
            
            text = text.lower()
            
            for cyrillic, latin in cyrillic_to_latin.items():
                text = text.replace(cyrillic, latin)
            
            text = re.sub(r'[^a-z0-9-]', '-', text)
            
            text = re.sub(r'-+', '-', text)
            
            return text.strip('-')

        tag_objects = []
        for tag_name in tag_list:
            slug = slugify(tag_name)
            if slug: 
                tag, created = Tag.objects.get_or_create(
                    name=tag_name,
                    defaults={'slug': slug}
                )
                tag_objects.append(tag)
        
        return tag_objects

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'bio', 'position']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'O\'zingiz haqingizda qisqacha ma\'lumot...',
                'rows': 4
            }),
            'position': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Lavozimingiz (masalan: Marketolog | CEO Business)'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Ismingiz'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email manzilingiz'
    }))
    subject = forms.CharField(max_length=200, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Xabar mavzusi'
    }))
    message = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'placeholder': 'Xabar matnini kiriting',
        'rows': 5
    }))
