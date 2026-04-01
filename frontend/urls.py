from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('auth/', views.auth_page, name='auth_page'),
    path('logout/', views.logout_view, name='logout'),
    path('my-profile/', views.my_profile, name='my_profile'),
    path('my-profile/questionnaire/', views.my_questionnaire, name='my_questionnaire'),
    path('my-profile/services/', views.my_services, name='my_services'),
    path('profile/edit/', views.create_or_edit_profile, name='edit_profile'),
    path('profile/photo/<int:photo_id>/delete/', views.delete_photo, name='delete_photo'),
]