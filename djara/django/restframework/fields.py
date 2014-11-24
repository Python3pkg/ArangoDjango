from rest_framework.fields import FileField


class RestFileField(FileField):

    def to_native(self, value):
        return value