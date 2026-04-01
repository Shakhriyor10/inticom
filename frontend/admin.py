from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User, UserProfilePhoto


class UserProfilePhotoInline(admin.TabularInline):
    model = UserProfilePhoto
    extra = 1
    max_num = 6
    verbose_name = 'Фото профиля'
    verbose_name_plural = 'Фотографии профиля (до 6)'


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    model = User
    ordering = ('id',)
    list_display = ('email', 'full_name', 'age', 'is_active_profile', 'is_staff')
    search_fields = ('email', 'full_name', 'phone_number', 'telegram_username')
    inlines = (UserProfilePhotoInline,)

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


@admin.register(UserProfilePhoto)
class UserProfilePhotoAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at')
    search_fields = ('user__email', 'user__full_name')
    list_filter = ('created_at',)
