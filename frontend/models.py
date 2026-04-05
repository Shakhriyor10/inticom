from django.conf import settings
from django.db import models
from django.utils import timezone


class Profile(models.Model):
    class Gender(models.TextChoices):
        FEMALE = 'female', 'Женский'
        MALE = 'male', 'Мужской'
        OTHER = 'other', 'Другой'

    class ProfileType(models.TextChoices):
        MASSEUSE = 'masseuse', 'Массажистка'
        ESCORT = 'escort', 'Проститутка'
        BOTH = 'both', 'Массажистка и проститутка'
        TRANS = 'trans', 'Транссексуал'

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    age = models.PositiveSmallIntegerField()
    gender = models.CharField(max_length=20, choices=Gender.choices)
    height = models.PositiveSmallIntegerField(help_text='Рост в сантиметрах')
    weight = models.PositiveSmallIntegerField(help_text='Вес в килограммах')
    profile_type = models.CharField(max_length=20, choices=ProfileType.choices)
    breast_size = models.CharField(max_length=20, blank=True)
    phone_number = models.CharField(max_length=30, blank=True, verbose_name='Номер телефона')
    telegram_username = models.CharField(max_length=64, blank=True, verbose_name='Telegram username')
    outcall_available = models.BooleanField(default=False, verbose_name='Выезд')
    incall_available = models.BooleanField(default=False, verbose_name='У себя')
    description = models.TextField()
    price_per_hour = models.PositiveIntegerField('Цена анкеты за 1 час', null=True, blank=True)
    price_for_two_hours = models.PositiveIntegerField('Цена анкеты за 2 часа', null=True, blank=True)
    price_for_night = models.PositiveIntegerField('Цена анкеты за ночь', null=True, blank=True)
    is_hot = models.BooleanField(default=False, verbose_name='VIP/Топ анкета')
    hot_until = models.DateField(null=True, blank=True, verbose_name='VIP активен до')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f'{self.name} ({self.user.email})'

    @property
    def is_hot_active(self) -> bool:
        if not self.is_hot:
            return False
        if self.hot_until and self.hot_until < timezone.localdate():
            return False
        return True

    @classmethod
    def deactivate_expired_hot_status(cls) -> None:
        cls.objects.filter(
            is_hot=True,
            hot_until__isnull=False,
            hot_until__lt=timezone.localdate(),
        ).update(is_hot=False)


class ProfilePhoto(models.Model):
    profile = models.ForeignKey(Profile, related_name='photos', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profiles/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'Фото для {self.profile.name}'


class Service(models.Model):
    class Category(models.TextChoices):
        ESCORT = 'escort', 'Для проституток'
        MASSAGE = 'massage', 'Для массажа'

    profile = models.ForeignKey(Profile, related_name='services', on_delete=models.CASCADE)
    service_option = models.ForeignKey(
        'ServiceOption',
        related_name='profile_services',
        on_delete=models.CASCADE,
        verbose_name='Услуга',
    )
    description = models.TextField('Комментарий', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('service_option__category', 'service_option__title')
        constraints = [
            models.UniqueConstraint(
                fields=('profile', 'service_option'),
                name='unique_service_option_per_profile',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.service_option.title} - {self.profile.name}'


class ServiceOption(models.Model):
    class Category(models.TextChoices):
        ESCORT = 'escort', 'Для проституток'
        MASSAGE = 'massage', 'Для массажа'

    category = models.CharField(max_length=20, choices=Category.choices, verbose_name='Категория')
    title = models.CharField(max_length=120, unique=True, verbose_name='Название')
    description = models.TextField('Описание', blank=True)
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('category', 'title')
        verbose_name = 'Справочник услуг'
        verbose_name_plural = 'Справочник услуг'

    def __str__(self) -> str:
        return f'{self.title} ({self.get_category_display()})'


class ProfileReview(models.Model):
    profile = models.ForeignKey(Profile, related_name='reviews', on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='profile_reviews', on_delete=models.CASCADE)
    comment = models.TextField('Комментарий')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Отзыв к анкете'
        verbose_name_plural = 'Отзывы к анкетам'

    def __str__(self) -> str:
        return f'Отзыв для {self.profile.name} от {self.author}'