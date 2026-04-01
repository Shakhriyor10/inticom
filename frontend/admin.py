from django.contrib import admin

from .models import Profile, ProfilePhoto


class ProfilePhotoInline(admin.TabularInline):
    model = ProfilePhoto
    extra = 0


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'age', 'profile_type', 'created_at')
    inlines = [ProfilePhotoInline]


@admin.register(ProfilePhoto)
class ProfilePhotoAdmin(admin.ModelAdmin):
    list_display = ('profile', 'uploaded_at')