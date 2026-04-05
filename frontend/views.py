from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import EmailAuthenticationForm, ProfileForm, ProfilePriceForm, ServiceForm, SignUpForm
from .models import Profile, ProfilePhoto, Service


def home(request):
    default_page_size = 16
    try:
        visible_count = int(request.GET.get('count', default_page_size))
    except (TypeError, ValueError):
        visible_count = default_page_size

    if visible_count < default_page_size:
        visible_count = default_page_size

    profiles_qs = Profile.objects.prefetch_related('photos').order_by('-created_at')
    profiles = profiles_qs[:visible_count]
    has_more = profiles_qs.count() > visible_count

    return render(
        request,
        'home.html',
        {
            'profiles': profiles,
            'visible_count': visible_count,
            'page_size': default_page_size,
            'has_more': has_more,
        },
    )

def profile_detail(request, profile_id):
    profile = get_object_or_404(
        Profile.objects.prefetch_related('photos', 'services__service_option'),
        id=profile_id,
    )
    escort_services = profile.services.filter(service_option__category=Service.Category.ESCORT)
    massage_services = profile.services.filter(service_option__category=Service.Category.MASSAGE)
    return render(
        request,
        'profile_detail.html',
        {
            'profile': profile,
            'escort_services': escort_services,
            'massage_services': massage_services,
        },
    )


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
    profile = (
        Profile.objects.filter(user=request.user)
        .prefetch_related('services__service_option')
        .first()
    )
    available_categories = []
    if profile:
        if profile.profile_type in (Profile.ProfileType.ESCORT, Profile.ProfileType.BOTH):
            available_categories.append(Service.Category.ESCORT)
        if profile.profile_type in (Profile.ProfileType.MASSEUSE, Profile.ProfileType.BOTH):
            available_categories.append(Service.Category.MASSAGE)

    service_form = ServiceForm(profile=profile, available_categories=available_categories)
    price_form = ProfilePriceForm(instance=profile) if profile else None

    if request.method == 'POST' and profile:
        action = request.POST.get('action')

        if action == 'save_prices':
            price_form = ProfilePriceForm(request.POST, instance=profile)
            if price_form.is_valid():
                price_form.save()
                messages.success(request, 'Цены анкеты обновлены.')
                return redirect('my_services')
        else:
            service_form = ServiceForm(
                request.POST,
                profile=profile,
                available_categories=available_categories,
            )
            if service_form.is_valid():
                selected_options = service_form.cleaned_data['service_options']
                description = service_form.cleaned_data['description']
                Service.objects.bulk_create(
                    [
                        Service(
                            profile=profile,
                            service_option=service_option,
                            description=description,
                        )
                        for service_option in selected_options
                    ]
                )
                messages.success(request, 'Услуги добавлены.')
                return redirect('my_services')

    escort_services = (
        profile.services.filter(service_option__category=Service.Category.ESCORT) if profile else []
    )
    massage_services = (
        profile.services.filter(service_option__category=Service.Category.MASSAGE) if profile else []
    )

    return render(
        request,
        'my_services.html',
        {
            'profile': profile,
            'service_form': service_form,
            'price_form': price_form,
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