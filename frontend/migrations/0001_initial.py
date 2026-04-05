from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('age', models.PositiveSmallIntegerField()),
                ('gender', models.CharField(choices=[('female', 'Женский'), ('male', 'Мужской'), ('other', 'Другой')], max_length=20)),
                ('height', models.PositiveSmallIntegerField(help_text='Рост в сантиметрах')),
                ('weight', models.PositiveSmallIntegerField(help_text='Вес в килограммах')),
                ('profile_type', models.CharField(choices=[('masseuse', 'Массажистка'), ('escort', 'Проститутка'), ('both', 'Массажистка и проститутка'), ('trans', 'Транссексуал')], max_length=20)),
                ('breast_size', models.CharField(blank=True, max_length=20)),
                ('phone_number', models.CharField(blank=True, max_length=30, verbose_name='Номер телефона')),
                ('telegram_username', models.CharField(blank=True, max_length=64, verbose_name='Telegram username')),
                ('outcall_available', models.BooleanField(default=False, verbose_name='Выезд')),
                ('incall_available', models.BooleanField(default=False, verbose_name='У себя')),
                ('description', models.TextField()),
                ('price_per_hour', models.PositiveIntegerField(blank=True, null=True, verbose_name='Цена анкеты за 1 час')),
                ('price_for_two_hours', models.PositiveIntegerField(blank=True, null=True, verbose_name='Цена анкеты за 2 часа')),
                ('price_for_night', models.PositiveIntegerField(blank=True, null=True, verbose_name='Цена анкеты за ночь')),
                ('is_hot', models.BooleanField(default=False, verbose_name='VIP/Топ анкета')),
                ('hot_until', models.DateField(blank=True, null=True, verbose_name='VIP активен до')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ServiceOption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(choices=[('escort', 'Для проституток'), ('massage', 'Для массажа')], max_length=20, verbose_name='Категория')),
                ('title', models.CharField(max_length=120, unique=True, verbose_name='Название')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активна')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Справочник услуг',
                'verbose_name_plural': 'Справочник услуг',
                'ordering': ('category', 'title'),
            },
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True, verbose_name='Комментарий')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='services', to='frontend.profile')),
                ('service_option', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='profile_services', to='frontend.serviceoption', verbose_name='Услуга')),
            ],
            options={
                'ordering': ('service_option__category', 'service_option__title'),
            },
        ),
        migrations.CreateModel(
            name='ProfileReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField(verbose_name='Комментарий')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='profile_reviews', to=settings.AUTH_USER_MODEL)),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='frontend.profile')),
            ],
            options={
                'verbose_name': 'Отзыв к анкете',
                'verbose_name_plural': 'Отзывы к анкетам',
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='ProfilePhoto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='profiles/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='frontend.profile')),
            ],
        ),
        migrations.AddConstraint(
            model_name='service',
            constraint=models.UniqueConstraint(fields=('profile', 'service_option'), name='unique_service_option_per_profile'),
        ),
    ]
