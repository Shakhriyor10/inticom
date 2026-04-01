from django.conf import settings
from django.db import models


class Profile(models.Model):
    class Gender(models.TextChoices):
        FEMALE = 'female', 'Женский'
        MALE = 'male', 'Мужской'
        OTHER = 'other', 'Другой'

    class ProfileType(models.TextChoices):
        MASSEUSE = 'masseuse', 'Массажистка'
        ESCORT = 'escort', 'Проститутка'
        TRANS = 'trans', 'Транссексуал'

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    age = models.PositiveSmallIntegerField()
    gender = models.CharField(max_length=20, choices=Gender.choices)
    height = models.PositiveSmallIntegerField(help_text='Рост в сантиметрах')
    weight = models.PositiveSmallIntegerField(help_text='Вес в килограммах')
    profile_type = models.CharField(max_length=20, choices=ProfileType.choices)
    breast_size = models.CharField(max_length=20, blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f'{self.name} ({self.user.email})'


class ProfilePhoto(models.Model):
    profile = models.ForeignKey(Profile, related_name='photos', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profiles/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'Фото для {self.profile.name}'
