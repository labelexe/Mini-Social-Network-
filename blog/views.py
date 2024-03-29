from django.contrib.auth import (get_user_model, login, logout,
                                 update_session_auth_hash)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import \
    default_token_generator as token_generator
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import urlsafe_base64_decode
from django.views import View
from django.views.generic import ListView

from mysite.settings import EMAIL_HOST_USER

from .forms import (AuthUser, CommentForm, ContactForm, EditProfile, Myprofile,
                    UserRegister)
from .models import Comment, Profil, Test
from .tasks import city_search, send_activation_notification

User = get_user_model()


class All_Pages(LoginRequiredMixin, ListView):
    model = Profil
    template_name = 'pages.html'
    context_object_name = 'pages'
    paginate_by = 2

    def get_queryset(self):
        return Profil.objects.select_related('profil')


@login_required
def test_view(request):
    if request.method == 'POST':
        value = request.POST
        for i in value.lists():
            if i[1] == ['on']:
                Test.objects.get(id=int(i[0])).delete()
        return redirect('test')
    else:
        test = Test.objects.all()
    return render(request, 'test.html', {'test': test})


@login_required
def profileview(request, id):
    P_id = get_object_or_404(Profil, pk=id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            new_f = form.save(commit=False)
            new_f.profil = P_id
            new_f.author = request.user.username
            new_f.save()
            return redirect('detail', id)
    else:
        form = CommentForm()
        comment = Comment.objects.filter(profil=id).select_related('profil')
        context = {'profil': P_id, 'comment': comment, 'form': form}
    return render(request, 'coment.html', context)


@login_required
def my_profile(request):
    my_p = Profil.objects.filter(profil=request.user)
    context = {'pages': my_p}
    return render(request, 'profil.html', context)


@login_required
def edit_profile(request, profile_id):
    profile = Profil.objects.filter(profil=request.user).get(id=profile_id)
    user = User.objects.get(id=request.user.id)
    if request.method == 'POST':
        form = EditProfile(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            new_form = form.save(commit=False)
            new_form.profil = user
            new_form.save()
            return redirect('home')
    else:
        form = EditProfile(instance=profile)
    return render(request, 'editprofile.html', {'form': form})


@login_required
def add_page(request):
    user = User.objects.get(id=request.user.id)
    if request.method == 'POST':
        form = Myprofile(request.POST, request.FILES)
        if form.is_valid():
            new_form = form.save(commit=False)
            new_form.profil = user
            new_form.ip = request.META['REMOTE_ADDR']
            new_form.city = city_search.delay(request.META['REMOTE_ADDR']).get(timeout=1)
            new_form.save()
            return redirect('profil')
    else:
        form = Myprofile()

    return render(request, 'newprofile.html', {'form': form})


def home(request):
    return render(request, 'home.html')


@login_required
def send_mes(request, user_id):
    user_send = User.objects.filter(profil__id=user_id)
    sender = User.objects.get(id=request.user.id)
    if request.method == 'POST':
        form = ContactForm(data=request.POST)
        if form.is_valid():
            mail_mes = f'Здравствуйте, {user_send.username} \nВам отправили письмо с сайта AleksZ8.\n ' \
                       f'Отправитель данного письма {sender.first_name} {sender.last_name} {sender.email}  \n {form.cleaned_data["body"]}'
            send_mail(form.cleaned_data['subject'], mail_mes, EMAIL_HOST_USER, [user_send.email])
            return redirect('pages')
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form, 'user': user_send})


@login_required
def delprofile(request, profile_id):
    Profil.objects.filter(profil=request.user).get(id=profile_id).delete()
    return redirect('profil')


def register(request):
    if request.method == 'POST':
        form = UserRegister(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            send_activation_notification.delay(user.pk)
            return redirect('home')
    else:
        form = UserRegister()
    return render(request, 'register.html', {'form': form})


def quit(request):
    logout(request)
    return redirect('auth')


def authentication(request):
    if request.method == "POST":
        form = AuthUser(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthUser()
    return render(request, 'auth.html', {'form': form})


def changepassword(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('profil')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change.html', {'form': form})


class EmailVerify(View):
    def get(self, request, uidb64, token):
        user = self.get_user(uidb64)

        if user is not None and token_generator.check_token(user, token):
            user.status = True
            user.save()
            login(request, user)
            return redirect('home')

    @staticmethod
    def get_user(uidb64):
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError,
                User.DoesNotExist, ValidationError):
            user = None
        return user
