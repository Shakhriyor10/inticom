from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.db.models.functions import Abs
from django.http import Http404
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_GET, require_POST

from .forms import (
    EmailAuthenticationForm,
    ProfileForm,
    ProfilePriceForm,
    ProfileReviewForm,
    ServiceForm,
    SignUpForm,
)
from .models import Profile, ProfilePhoto, ProfileReview, Service


def home(request):
    default_page_size = 16
    try:
        visible_count = int(request.GET.get('count', default_page_size))
    except (TypeError, ValueError):
        visible_count = default_page_size

    if visible_count < default_page_size:
        visible_count = default_page_size

    Profile.deactivate_expired_hot_status()
    profiles_qs = Profile.objects.filter(status=Profile.Status.ACTIVE).prefetch_related('photos').order_by(
        '-is_hot',
        '-created_at',
    )
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
    review_page_size = 10
    Profile.deactivate_expired_hot_status()
    profile = get_object_or_404(
        Profile.objects.prefetch_related('photos', 'services__service_option'),
        id=profile_id,
    )
    if profile.status == Profile.Status.INACTIVE:
        if request.user.is_authenticated and request.user.id == profile.user_id:
            messages.warning(request, 'Ваша анкета отключена администратором и скрыта с главной страницы.')
            return redirect('my_questionnaire')
        raise Http404

    review_form = ProfileReviewForm()
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'Только зарегистрированные пользователи могут оставлять отзывы.')
            return redirect('auth_page')

        review_form = ProfileReviewForm(request.POST)
        if review_form.is_valid():
            ProfileReview.objects.create(
                profile=profile,
                author=request.user,
                comment=review_form.cleaned_data['comment'],
            )
            messages.success(request, f'Отзыв для анкеты "{profile.name}" сохранен.')
            return redirect('profile_detail', profile_id=profile_id)

    escort_services = profile.services.filter(service_option__category=Service.Category.ESCORT)
    massage_services = profile.services.filter(service_option__category=Service.Category.MASSAGE)
    similar_profiles = (
        Profile.objects.filter(
            status=Profile.Status.ACTIVE,
            height__gte=profile.height - 15,
            height__lte=profile.height + 15,
            weight__gte=profile.weight - 5,
            weight__lte=profile.weight + 5,
        )
        .exclude(id=profile.id)
        .prefetch_related('photos', 'reviews')
        .annotate(
            weight_diff=Abs(F('weight') - profile.weight),
            height_diff=Abs(F('height') - profile.height),
        )
        .annotate(match_score=F('weight_diff') + F('height_diff'))
        .order_by('match_score', 'weight_diff', 'height_diff', '-is_hot', '-created_at')[:8]
    )

    return render(
        request,
        'profile_detail.html',
        {
            'profile': profile,
            'escort_services': escort_services,
            'massage_services': massage_services,
            'similar_profiles': similar_profiles,
            'review_form': review_form,
            'profile_reviews': profile.reviews.select_related('author')[:review_page_size],
            'review_page_size': review_page_size,
            'has_more_reviews': profile.reviews.count() > review_page_size,
        },
    )


@login_required
@require_POST
def create_profile_review(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id, status=Profile.Status.ACTIVE)
    review_form = ProfileReviewForm(request.POST)
    if not review_form.is_valid():
        return JsonResponse({'error': 'Введите корректный комментарий.'}, status=400)

    review = ProfileReview.objects.create(
        profile=profile,
        author=request.user,
        comment=review_form.cleaned_data['comment'],
    )
    review_html = render_to_string(
        'partials/review_item.html',
        {'review': review, 'request': request},
    )
    return JsonResponse({'review_html': review_html, 'review_id': review.id})


@login_required
@require_POST
def delete_profile_review(request, review_id):
    review = get_object_or_404(ProfileReview, id=review_id)
    if review.author_id != request.user.id:
        return JsonResponse({'error': 'Можно удалять только свои комментарии.'}, status=403)

    review.delete()
    return JsonResponse({'status': 'ok'})


@require_GET
def profile_reviews_chunk(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id, status=Profile.Status.ACTIVE)
    try:
        offset = int(request.GET.get('offset', 0))
        limit = int(request.GET.get('limit', 10))
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Некорректные параметры пагинации.'}, status=400)

    if offset < 0:
        offset = 0
    if limit < 1:
        limit = 10
    if limit > 50:
        limit = 50

    reviews = list(profile.reviews.select_related('author')[offset : offset + limit])
    items = [
        render_to_string(
            'partials/review_item.html',
            {'review': review, 'request': request},
        )
        for review in reviews
    ]

    total_reviews = profile.reviews.count()
    next_offset = offset + len(reviews)

    return JsonResponse(
        {
            'items': items,
            'next_offset': next_offset,
            'has_more': next_offset < total_reviews,
        }
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
    profile = (
        Profile.objects.filter(user=request.user)
        .prefetch_related('photos', 'services__service_option')
        .first()
    )
    escort_count = 0
    massage_count = 0
    if profile:
        escort_count = profile.services.filter(service_option__category=Service.Category.ESCORT).count()
        massage_count = profile.services.filter(service_option__category=Service.Category.MASSAGE).count()

    return render(
        request,
        'my_profile.html',
        {
            'profile': profile,
            'escort_count': escort_count,
            'massage_count': massage_count,
        },
    )


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
            'services_total': len(escort_services) + len(massage_services),
        },
    )


@login_required
@require_POST
def delete_service(request, service_id):
    service = get_object_or_404(Service, id=service_id, profile__user=request.user)
    service.delete()
    messages.success(request, 'Услуга удалена. Вы можете добавить ее снова в любой момент.')
    return redirect('my_services')


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
