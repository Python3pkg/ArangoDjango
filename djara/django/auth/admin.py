from djara.django.contrib import admin as unused_admin
from django.contrib import admin
from djara.django.contrib.admin.options import CollectionAdmin
from djara.django.auth.models import User

""" models """
class UserAdmin(CollectionAdmin):
    """
    User Admin
    """
    list_display = ('username', 'email_address', )
    list_filter = ('is_staff_member', 'is_owner', )
    exclude = ( 'groups', 'permissions', )

admin.site.register(User, UserAdmin)