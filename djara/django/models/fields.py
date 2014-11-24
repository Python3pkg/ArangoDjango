import os
import datetime

from django.core.files.base import File
from django.core.files.storage import default_storage
from django.utils.encoding import force_str, force_text
from django.db.models.fields.files import FileDescriptor

from arangodb.orm.fields import TextField


class FieldFile(File):
    def __init__(self, instance, field, name):
        super(FieldFile, self).__init__(None, name)
        self.instance = instance
        self.field = field
        self.storage = field.storage
        self._committed = True

    def __eq__(self, other):
        # Older code may be expecting FileField values to be simple strings.
        # By overriding the == operator, it can remain backwards compatibility.
        if hasattr(other, 'name'):
            return self.name == other.name
        return self.name == other

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.name)

    # The standard File contains most of the necessary properties, but
    # FieldFiles can be instantiated without a name, so that needs to
    # be checked for here.

    def _require_file(self):
        if not self:
            raise ValueError("The '%s' attribute has no file associated with it." % self.field.name)

    def _get_file(self):
        self._require_file()
        if not hasattr(self, '_file') or self._file is None:
            self._file = self.storage.open(self.name, 'rb')
        return self._file

    def _set_file(self, file):
        self._file = file

    def _del_file(self):
        del self._file

    file = property(_get_file, _set_file, _del_file)

    def _get_path(self):
        self._require_file()
        return self.storage.path(self.name)
    path = property(_get_path)

    def _get_url(self):
        self._require_file()
        return self.storage.url(self.name)
    url = property(_get_url)

    def _get_size(self):
        self._require_file()
        if not self._committed:
            return self.file.size
        return self.storage.size(self.name)
    size = property(_get_size)

    def open(self, mode='rb'):
        self._require_file()
        self.file.open(mode)
    # open() doesn't alter the file's contents, but it does reset the pointer
    open.alters_data = True

    # In addition to the standard File API, FieldFiles have extra methods
    # to further manipulate the underlying file, as well as update the
    # associated model instance.

    def save(self, name, content, save=True):
        name = self.field.generate_filename(self.instance, name)
        self.name = self.storage.save(name, content)
        setattr(self.instance, self.field.name, self.name)

        # Update the filesize cache
        self._size = content.size
        self._committed = True

        # Save the object because it has changed, unless save is False
        if save:
            self.instance.save()
    save.alters_data = True

    def delete(self, save=True):
        if not self:
            return
        # Only close the file if it's already open, which we know by the
        # presence of self._file
        if hasattr(self, '_file'):
            self.close()
            del self.file

        self.storage.delete(self.name)

        self.name = None
        setattr(self.instance, self.field.name, self.name)

        # Delete the filesize cache
        if hasattr(self, '_size'):
            del self._size
        self._committed = False

        if save:
            self.instance.save()
    delete.alters_data = True

    def _get_closed(self):
        file = getattr(self, '_file', None)
        return file is None or file.closed
    closed = property(_get_closed)

    def close(self):
        file = getattr(self, '_file', None)
        if file is not None:
            file.close()

    def __getstate__(self):
        # FieldFile needs access to its associated model field and an instance
        # it's attached to in order to work properly, but the only necessary
        # data to be pickled is the file's name itself. Everything else will
        # be restored later, by FileDescriptor below.
        return {'name': self.name, 'closed': False, '_committed': True, '_file': None}


class FileField(TextField):

    # The class to wrap instance attributes in. Accessing the file object off
    # the instance will always return an instance of attr_class.
    attr_cls = FieldFile

    # The descriptor to use for accessing the attribute off of the class.
    descriptor_class = FileDescriptor

    def __init__(self, upload_to='', storage=None, **kwargs):
        """
        """

        super(FileField, self).__init__(**kwargs)

        self.file_name = None

        self.storage = storage or default_storage
        self.upload_to = upload_to
        if callable(upload_to):
            self.generate_filename = upload_to


    def create_file_instance(self, model_instance):
        """
        """

        self.file = self.attr_cls(instance=model_instance, field=self, name=self.file_name)

    def on_save(self, model_instance):
        """
        """

        self.create_file_instance(model_instance)

        file = self.file

        if file:
            # Commit the file to storage prior to saving the model
            file.save(file.name, self.content_file, save=False)
        return file



    def get(self):
        """
        """

        return self.file_name


    def set(self, *args, **kwargs):
        """
        """

        if len(args) is 1:
            value = args[0]

            self.content_file = value
            self.file_name = self.generate_filename(self, value)

    def dumps(self):
        """
        """

        return self.file.path


    def loads(self, string_val):
        """
        """

        self.file_name = string_val


    def validate(self):
        """
        """

        super(FileField, self).validate()


    def get_directory_name(self):
        return os.path.normpath(force_text(datetime.datetime.now().strftime(force_str(self.upload_to))))

    def get_filename(self, filename):
        return os.path.normpath(self.storage.get_valid_name((filename)))

    def generate_filename(self, instance, filename):
        return os.path.join(self.get_directory_name(), self.get_filename(filename))
