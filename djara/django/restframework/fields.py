from django.conf import settings

from rest_framework.fields import FileField


class RestFileField(FileField):

    def to_native(self, value):
        return '%s%s' % (settings.MEDIA_URL,  value.split(settings.MEDIA_URL)[1])