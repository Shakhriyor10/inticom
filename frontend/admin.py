from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    model = User
    ordering = ('id',)
    list_display = ('email', 'full_name', 'age', 'is_active_profile', 'is_staff')
    search_fields = ('email', 'full_name', 'phone_number', 'telegram_username')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (
            'Профиль',
            {
                'fields': (
                    'full_name',
                    'height',
                    'weight',
                    'age',
                    'phone_number',
                    'telegram_username',
                    'profile_description',
                    'profile_photo',
                    'is_active_profile',
                )
            },
        ),
        ('Права доступа', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email', 'password1', 'password2', 'is_staff', 'is_superuser'),
            },
        ),
    )
