from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.http.response import HttpResponseNotFound
from django.shortcuts import render, redirect
from django.template import loader
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext as _

from djara.django.auth.models import User
from djara.django.auth.utils import login, logout


def login_view(request):
    """
    """

    return render(request, 'auth/user/login.html', {})


def login_action(request, view_name):
    """
    """

    username = request.POST.get('username', None)
    user_password = request.POST.get('user_password', None)
    
    user = User.objects.get(username=username)
    # User login
    if user and user.login(password=user_password):

        # Django session login
        login(request=request, user=user)
        return redirect(to=view_name)
    else:
        return render(request, 'auth/user/login.html', {})


def logout_action(request, view_name):
    """
    """

    # User logout
    request.user.logout()

    # Django logout
    if logout(request):
        return redirect(to=view_name)


def register_view(request):
    """
    """

    return render(request, 'auth/user/register.html', {})


def register_action(request, view_name):
    """
    """

    username = request.POST.get('username', None)
    email = request.POST.get('email', None)
    user_password = request.POST.get('user_password', None)
    user_password_again = request.POST.get('user_password_again', None)

    # Check username and email
    if User.objects.get(username=username) or User.objects.get(email_address=email):
        raise Exception('Username or email is already taken')

    # Check passwords
    if user_password != user_password_again:
        raise Exception('Passwords are not the same')

    activation_key = get_random_string(length=20)

    user = User()
    user.username = username
    user.email_address = email
    user.password = user_password
    user.activation_key = activation_key
    user.save()

    kwargs = {
        'activation_key': activation_key,
        'uuid': user.uuid,
        'view_name': view_name,
    }

    # register_msg
    register_template_string = loader.render_to_string('auth/user/register_email.html', dictionary={
        'logo_url': '%s%simages/logo.png' % (settings.BASE_URL, settings.STATIC_URL),
        'activate_account_url': '%s%s' % (settings.BASE_URL, reverse_lazy('auth:register-activate', kwargs=kwargs)),
    })

    user.email_user(subject=_('Registration'), message=register_template_string, from_email='noreply@dress-up.clothing')

    return render(request, 'auth/user/register_successful.html', {})


def register_activate(request, activation_key, uuid, view_name):
    """
    """

    user = User.objects.get(uuid=uuid, activation_key=activation_key)
    if not user or not activation_key or len(activation_key) < 5:
        return HttpResponseNotFound()

    user.is_active = True
    user.activation_key = ''
    user.save()

    return render(request, 'auth/user/register_finished.html', {})