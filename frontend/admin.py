from django.contrib import admin

from .models import Profile, ProfilePhoto, ProfileReview, Service, ServiceOption


class ProfilePhotoInline(admin.TabularInline):
    model = ProfilePhoto
    extra = 0


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'user',
        'age',
        'profile_type',
        'status',
        'is_hot',
        'hot_until',
        'price_per_hour',
        'price_for_two_hours',
        'price_for_night',
        'created_at',
    )
    list_filter = ('profile_type', 'status', 'is_hot')
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


@admin.register(ProfileReview)
class ProfileReviewAdmin(admin.ModelAdmin):
    list_display = ('profile', 'author', 'created_at')
    search_fields = ('profile__name', 'author__username', 'comment')
