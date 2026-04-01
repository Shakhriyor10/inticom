from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import EmailAuthenticationForm, ProfileForm, ServiceForm, SignUpForm
from .models import Profile, ProfilePhoto


def home(request):
    profiles = Profile.objects.prefetch_related('photos').order_by('-created_at')
    return render(request, 'home.html', {'profiles': profiles})


def auth_page(request):
    mode = request.GET.get('mode', 'login')
    login_form = EmailAuthenticationForm(request, data=request.POST or None, prefix='login')
    signup_form = SignUpForm(request.POST or None, prefix='signup')

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'login' and login_form.is_valid():
            login(request, login_form.get_user())
            return redirect('my_profile')
        if action == 'signup' and signup_form.is_valid():
            user = signup_form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно.')
            return redirect('my_profile')
        mode = action

    return render(
        request,
        'auth.html',
        {'login_form': login_form, 'signup_form': signup_form, 'mode': mode},
    )


@login_required
def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def my_profile(request):
    profile = Profile.objects.filter(user=request.user).first()
    return render(request, 'my_profile.html', {'profile': profile})


@login_required
def my_questionnaire(request):
    profile = Profile.objects.filter(user=request.user).prefetch_related('photos').first()
    return render(request, 'my_questionnaire.html', {'profile': profile})


@login_required
def my_services(request):
    profile = Profile.objects.filter(user=request.user).prefetch_related('services').first()
    service_form = ServiceForm()

    if request.method == 'POST' and profile:
        service_form = ServiceForm(request.POST)
        if service_form.is_valid():
            service = service_form.save(commit=False)
            service.profile = profile
            service.save()
            messages.success(request, 'Услуга добавлена.')
            return redirect('my_services')

    escort_services = profile.services.filter(category='escort') if profile else []
    massage_services = profile.services.filter(category='massage') if profile else []

    return render(
        request,
        'my_services.html',
        {
            'profile': profile,
            'service_form': service_form,
            'escort_services': escort_services,
            'massage_services': massage_services,
        },
    )


@login_required
def create_or_edit_profile(request):
    profile = Profile.objects.filter(user=request.user).first()

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        files = request.FILES.getlist('photos')

        existing_count = profile.photos.count() if profile else 0
        if existing_count + len(files) > 5:
            form.add_error(None, 'Можно загрузить максимум 5 фотографий.')

        if form.is_valid():
            saved_profile = form.save(commit=False)
            saved_profile.user = request.user
            saved_profile.save()

            if profile is None:
                existing_count = 0
            if files:
                for photo in files[: 5 - existing_count]:
                    ProfilePhoto.objects.create(profile=saved_profile, image=photo)

            messages.success(request, 'Анкета сохранена.')
            return redirect('my_questionnaire')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'profile_form.html', {'form': form, 'profile': profile})


@login_required
def delete_photo(request, photo_id):
    photo = get_object_or_404(ProfilePhoto, id=photo_id, profile__user=request.user)
    photo.delete()
    messages.success(request, 'Фото удалено.')
    return redirect('edit_profile')
