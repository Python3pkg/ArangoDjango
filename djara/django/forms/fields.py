import os
import datetime

from django.core.files.storage import default_storage
from django.utils.encoding import force_str, force_text
from django.db.models.fields.files import FieldFile, FileDescriptor

from arangodb.orm.fields import TextField


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

        if file and not file._committed:
            # Commit the file to storage prior to saving the model
            file.save(file.name, file, save=False)
        return file


    def set(self, *args, **kwargs):
        """
        """

        if len(args) is 1:
            value = args[0]

            self.file_name = self.generate_filename(value)

    def dumps(self):
        """
        """

        return self.file.path


    def loads(self, string_val):
        """
        """

        try:
            self.file_name = string_val.split('/')[-1]
        except:
            pass


    def validate(self):
        """
        """

        super(FileField, self).validate()


    def get_directory_name(self):
        return os.path.normpath(force_text(datetime.datetime.now().strftime(force_str(self.upload_to))))

    def get_filename(self, filename):
        return os.path.normpath(self.storage.get_valid_name((filename)))

    def generate_filename(self, filename):
        return os.path.join(self.get_directory_name(), self.get_filename(filename))
