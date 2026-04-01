from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Profile, Service


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'autofocus': True}))


class SignUpForm(UserCreationForm):
    username = forms.EmailField(label='Email')

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

    def clean_username(self):
        email = self.cleaned_data['username'].strip().lower()
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data['username']
        user.username = email
        user.email = email
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'name',
            'age',
            'gender',
            'height',
            'weight',
            'profile_type',
            'breast_size',
            'description',
        ]
        labels = {
            'name': 'Имя',
            'age': 'Возраст',
            'gender': 'Пол',
            'height': 'Рост',
            'weight': 'Вес',
            'profile_type': 'Тип профиля',
            'breast_size': 'Размер груди (необязательно)',
            'description': 'Описание профиля',
        }


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = [
            'category',
            'title',
            'description',
            'price_per_hour',
            'price_for_two_hours',
            'price_for_night',
        ]
        labels = {
            'category': 'Категория услуги',
            'title': 'Название услуги',
            'description': 'Описание услуги',
            'price_per_hour': 'Цена за 1 час',
            'price_for_two_hours': 'Цена за 2 часа',
            'price_for_night': 'Цена за ночь',
        }
