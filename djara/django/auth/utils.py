from auth.models import User
from django.middleware.csrf import rotate_token

SESSION_KEY = '_auth_user_id'

def get_session_user(request):
    """
    Returns the user model instance associated with the given request session.
    If no user is retrieved an instance of `AnonymousUser` is returned.
    """
    from .models import AnonymousUser
    try:
        user_id = request.session[SESSION_KEY]
        user = User.objects.get(_id=user_id) or AnonymousUser()
    except (KeyError, AssertionError):
        user = AnonymousUser()

    return user


def login(request, user):

    if user is None:
        user = request.user

    # TODO: It would be nice to support different login methods, like signed cookies.
    if SESSION_KEY in request.session:
        if request.session[SESSION_KEY] != user.id:
            # To avoid reusing another user's session, create a new, empty
            # session if the existing session corresponds to a different
            # authenticated user.
            request.session.flush()
    else:
        request.session.cycle_key()

    request.session[SESSION_KEY] = user.id

    if hasattr(request, 'user'):
        request.user = user

    rotate_token(request)

def logout(request):
    """
    Removes the authenticated user's ID from the request and flushes their
    session data.
    """
    # Dispatch the signal before the user is logged out so the receivers have a
    # chance to find out *who* logged out.
    user = getattr(request, 'user', None)

    # Check if the user has ever been logged out
    if hasattr(user, 'is_authenticated') and not user.is_authenticated():
        return False

    # remember language choice saved to session
    language = request.session.get('django_language')

    request.session.flush()

    if language is not None:
        request.session['django_language'] = language

    if hasattr(request, 'user'):
        from .models import AnonymousUser
        request.user = AnonymousUser()

    return True

def authenticate(username, password):
    """
    """

    user = User.objects.get(username=username)
    if not user.password.verify(password):
        return None
    else:
        return user