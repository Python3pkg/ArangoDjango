from django import forms
from django.contrib.auth.forms import AuthenticationForm

from djara.django.auth.utils import authenticate


class CollectionAuthenticationForm(AuthenticationForm):


    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:

            self.user_cache = authenticate(username=username, password=password)

            # self.user_cache = authenticate(username=username,
            #                                password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
            elif not self.user_cache.is_active:
                raise forms.ValidationError(
                    self.error_messages['inactive'],
                    code='inactive',
                )
        return self.cleaned_data