from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Profile, Service, ServiceOption


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'autofocus': True}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class SignUpForm(UserCreationForm):
    username = forms.EmailField(label='Email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

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
    def __init__(self, *args, **kwargs):
        available_categories = kwargs.pop('available_categories', [])
        profile = kwargs.pop('profile', None)
        super().__init__(*args, **kwargs)

        queryset = ServiceOption.objects.filter(is_active=True, category__in=available_categories)
        if profile:
            queryset = queryset.exclude(profile_services__profile=profile)
        self.fields['service_option'].queryset = queryset.distinct()

        for field_name, field in self.fields.items():
            css_class = 'form-control'
            if field_name == 'service_option':
                css_class = 'form-select'
            field.widget.attrs['class'] = css_class

    class Meta:
        model = Service
        fields = [
            'service_option',
            'description',
            'price_per_hour',
            'price_for_two_hours',
            'price_for_night',
        ]
        labels = {
            'service_option': 'Выберите услугу',
            'description': 'Комментарий',
            'price_per_hour': 'Цена за 1 час',
            'price_for_two_hours': 'Цена за 2 часа',
            'price_for_night': 'Цена за ночь',
        }
