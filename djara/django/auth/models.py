from arangodb.index.unique import HashIndex
from arangodb.orm.fields import CharField, BooleanField, DatetimeField, UuidField, ManyToManyField
from arangodb.orm.models import CollectionModel

from django.utils import timezone

from auth.fields import PasswordField
from mail.utils import send_html_email



class BaseModel(CollectionModel):

    uuid = UuidField()


class PermissionMixin(object):

    def has_permission(self, name):
        pass


class Permission(CollectionModel):

    name = CharField(null=False)


class Group(CollectionModel, PermissionMixin):

    permissions = ManyToManyField(to=Permission, related_name='groups')


class User(BaseModel, PermissionMixin):

    username_index = HashIndex(fields=['username'])
    email_address_index = HashIndex(fields=['email_address'])

    username = CharField(null=False)
    email_address = CharField(max_length=2048, null=False)

    password = PasswordField()

    activation_key = CharField(null=True, default=None)
    is_active = BooleanField(default=False, null=False)

    #
    is_staff_member = BooleanField(default=False, null=False)
    is_owner = BooleanField(default=False, null=False)

    # Login status
    is_logged_in = BooleanField(default=False, null=False)
    last_login_time = DatetimeField()

    groups = ManyToManyField(to=Group, related_name='users')
    permissions = ManyToManyField(to=Permission, related_name='users')


    # Helper methods
    def login(self, password):
        """
        """

        if not self.is_active:
            raise Exception('Not active')

        if not self.password.verify(password=password):
            raise Exception('Wrong password')

        self.is_logged_in = True
        self.last_login_time = timezone.now()
        self.save()

        return True

    def logout(self):
        """
        """

        if not self.is_active:
            raise Exception('Not active')

        if not self.is_logged_in:
            raise Exception('Not logged in')

        self.is_logged_in = False
        self.save()

    def is_authenticated(self):
        return True


    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        send_html_email(subject, message, from_email, [self.email_address])


    class Meta(object):
        app_label = 'auth'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ('username', )


class AnonymousUser(User, PermissionMixin):

    def is_authenticated(self):
        return False