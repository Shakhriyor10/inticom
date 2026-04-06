from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Profile, ProfileReview, Service, ServiceOption


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
        for field_name, field in self.fields.items():
            if field_name in ('outcall_available', 'incall_available'):
                field.widget.attrs['class'] = 'form-check-input'
                continue
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
            'phone_number',
            'telegram_username',
            'outcall_available',
            'incall_available',
            'description',
            'price_per_hour',
            'price_for_two_hours',
            'price_for_night',
        ]
        labels = {
            'name': 'Имя',
            'age': 'Возраст',
            'gender': 'Пол',
            'height': 'Рост',
            'weight': 'Вес',
            'profile_type': 'Тип профиля',
            'breast_size': 'Размер груди (необязательно)',
            'phone_number': 'Номер телефона',
            'telegram_username': 'Telegram username',
            'outcall_available': 'Выезд',
            'incall_available': 'У себя',
            'description': 'Описание профиля',
            'price_per_hour': 'Общая цена за 1 час',
            'price_for_two_hours': 'Общая цена за 2 часа',
            'price_for_night': 'Общая цена за ночь',
        }

    def clean(self):
        cleaned_data = super().clean()
        phone_number = (cleaned_data.get('phone_number') or '').strip()
        telegram_username = (cleaned_data.get('telegram_username') or '').strip().lstrip('@')

        if not phone_number and not telegram_username:
            raise forms.ValidationError('Укажите номер телефона или Telegram username.')

        cleaned_data['telegram_username'] = telegram_username
        return cleaned_data


class ServiceForm(forms.ModelForm):
    service_options = forms.ModelMultipleChoiceField(
        queryset=ServiceOption.objects.none(),
        label='Выберите услуги',
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )

    def __init__(self, *args, **kwargs):
        available_categories = kwargs.pop('available_categories', [])
        profile = kwargs.pop('profile', None)
        super().__init__(*args, **kwargs)

        queryset = ServiceOption.objects.filter(is_active=True, category__in=available_categories)
        if profile:
            queryset = queryset.exclude(profile_services__profile=profile)
        self.fields['service_options'].queryset = queryset.distinct()
        self.fields['service_options'].widget.attrs['class'] = 'service-options list-unstyled mb-0'

        for field_name, field in self.fields.items():
            css_class = 'form-control'
            if field_name == 'service_options':
                continue
            field.widget.attrs['class'] = css_class

    class Meta:
        model = Service
        fields = [
            'description',
        ]
        labels = {
            'description': 'Комментарий',
        }

class ProfilePriceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = Profile
        fields = ['price_per_hour', 'price_for_two_hours', 'price_for_night']
        labels = {
            'price_per_hour': 'Общая цена за 1 час',
            'price_for_two_hours': 'Общая цена за 2 часа',
            'price_for_night': 'Общая цена за ночь',
        }


class ProfileReviewForm(forms.ModelForm):
    class Meta:
        model = ProfileReview
        fields = ['comment']
        labels = {'comment': 'Комментарий'}
        widgets = {
            'comment': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 2,
                    'placeholder': 'Оставьте ваш отзыв...',
                }
            ),
        }