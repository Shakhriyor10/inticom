from django.contrib import admin

from .models import Profile, ProfilePhoto, Service, ServiceOption


class ProfilePhotoInline(admin.TabularInline):
    model = ProfilePhoto
    extra = 0


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'age', 'profile_type', 'price_per_hour', 'price_for_two_hours', 'price_for_night', 'created_at')
    inlines = [ProfilePhotoInline]


@admin.register(ProfilePhoto)
class ProfilePhotoAdmin(admin.ModelAdmin):
    list_display = ('profile', 'uploaded_at')


@admin.register(ServiceOption)
class ServiceOptionAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_active', 'created_at')
    list_filter = ('category', 'is_active')
    search_fields = ('title', 'description')


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('profile', 'service_option')
    list_filter = ('service_option__category',)
    search_fields = ('profile__name', 'service_option__title')