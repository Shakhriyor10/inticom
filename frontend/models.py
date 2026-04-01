from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class UserManager(BaseUserManager):
    """Менеджер пользователей с авторизацией по email."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Поле email обязательно для заполнения.')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Профиль человека + учетные данные для входа."""

    username = None

    email = models.EmailField('Email (логин)', unique=True)
    full_name = models.CharField('Имя', max_length=255)
    height = models.PositiveSmallIntegerField('Рост (см)')
    weight = models.PositiveSmallIntegerField('Вес (кг)')
    age = models.PositiveSmallIntegerField('Возраст')
    phone_number = models.CharField('Номер телефона', max_length=20, blank=True, null=True)
    telegram_username = models.CharField('Telegram username', max_length=64, blank=True, null=True)
    profile_description = models.TextField('Описание профиля')
    is_active_profile = models.BooleanField('Статус активности', default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.full_name or self.email


class UserProfilePhoto(models.Model):
    """Фотографии профиля пользователя (до 6 шт.)."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profile_photos', verbose_name='Пользователь')
    photo = models.ImageField('Фото профиля', upload_to='profile_photos/')
    created_at = models.DateTimeField('Дата добавления', auto_now_add=True)

    class Meta:
        verbose_name = 'Фото профиля'
        verbose_name_plural = 'Фото профилей'
        ordering = ('-created_at',)

    def clean(self):
        super().clean()

        if not self.user_id:
            return

        existing_count = self.user.profile_photos.exclude(pk=self.pk).count()
        if existing_count >= 6:
            raise ValidationError('Можно загрузить не более 6 фотографий профиля.')

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'Фото #{self.pk or "new"} для {self.user}'
