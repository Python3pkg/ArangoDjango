import django
from django.contrib.admin.sites import AdminSite as DjangoAdminSite
from django.core.urlresolvers import reverse, NoReverseMatch
from django.http.response import Http404
from django.template.defaultfilters import capfirst
from django.template.response import TemplateResponse
from django.views.decorators.cache import never_cache
from django.utils.translation import ugettext as _
import six


class CollectionAdminSite(DjangoAdminSite):


    def register(self, model_or_iterable, admin_class=None, **options):
        """
        Registers the given model(s) with the given admin class.

        The model(s) should be Model classes, not instances.

        If an admin class isn't given, it will use ModelAdmin (the default
        admin options). If keyword arguments are given -- e.g., list_display --
        they'll be applied as options to the admin class.

        If a model is already registered, this will raise AlreadyRegistered.

        If a model is abstract, this will raise ImproperlyConfigured.
        """
        # if not admin_class:
        #     admin_class = ModelAdmin

        if not isinstance(model_or_iterable, list):
            model_or_iterable = [model_or_iterable]
        for model in model_or_iterable:
        #     if model._meta.abstract:
        #         raise ImproperlyConfigured('The model %s is abstract, so it '
        #               'cannot be registered with admin.' % model.__name__)
        #
        #     if model in self._registry:
        #         raise AlreadyRegistered('The model %s is already registered' % model.__name__)
        #
        #     # Ignore the registration if the model has been
        #     # swapped out.
        #     if not model._meta.swapped:
        #         # If we got **options then dynamically construct a subclass of
        #         # admin_class with those **options.
        #         if options:
        #             # For reasons I don't quite understand, without a __module__
        #             # the created class appears to "live" in the wrong place,
        #             # which causes issues later on.
        #             options['__module__'] = __name__
        #             admin_class = type("%sAdmin" % model.__name__, (admin_class,), options)
        #
        #         if admin_class is not ModelAdmin and settings.DEBUG:
        #             admin_class.validate(model)
        #
        #         # Instantiate the admin class to save in the registry
            self._registry[model] = admin_class(model, self)

    @never_cache
    def index(self, request, extra_context=None):
        """
        Displays the main admin index page, which lists all of the installed
        apps that have been registered in this site.
        """
        app_dict = {}
        user = request.user
        for model, model_admin in self._registry.items():
            app_label = model._meta.app_label
            has_module_perms = user.has_module_perms(app_label)

            if has_module_perms:
                perms = model_admin.get_model_perms(request)

                # Check whether user has any perm for this module.
                # If so, add the module to the model_list.
                if True in perms.values():
                    info = (app_label, model._meta.model_name)
                    model_dict = {
                        'name': capfirst(model._meta.verbose_name_plural),
                        'object_name': model._meta.object_name,
                        'perms': perms,
                    }
                    if perms.get('change', False):
                        try:
                            model_dict['admin_url'] = reverse('admin:admin:%s_%s_changelist' % info, current_app=self.name)
                        except NoReverseMatch:
                            pass
                    if perms.get('add', False):
                        try:
                            model_dict['add_url'] = reverse('admin:admin:%s_%s_add' % info, current_app=self.name)
                        except NoReverseMatch:
                            pass
                    if app_label in app_dict:
                        print(model_dict)
                        app_dict[app_label]['models'].append(model_dict)
                    else:
                        app_dict[app_label] = {
                            'name': app_label.title(),
                            'app_label': app_label,
                            'app_url': reverse('admin:app_list', kwargs={'app_label': app_label}, current_app=self.name),
                            'has_module_perms': has_module_perms,
                            'models': [model_dict],
                        }

        # Sort the apps alphabetically.
        app_list = list(six.itervalues(app_dict))
        app_list.sort(key=lambda x: x['name'])

        # Sort the models alphabetically within each app.
        for app in app_list:
            app['models'].sort(key=lambda x: x['name'])

        context = {
            'title': _('Site administration'),
            'app_list': app_list,
        }
        context.update(extra_context or {})
        return TemplateResponse(request, self.index_template or
                                'admin/index.html', context,
                                current_app=self.name)


    def app_index(self, request, app_label, extra_context=None):
        user = request.user
        has_module_perms = user.has_module_perms(app_label)
        app_dict = {}
        for model, model_admin in self._registry.items():
            if app_label == model._meta.app_label:
                if has_module_perms:
                    perms = model_admin.get_model_perms(request)

                    # Check whether user has any perm for this module.
                    # If so, add the module to the model_list.
                    if True in perms.values():
                        info = (app_label, model._meta.model_name)
                        model_dict = {
                            'name': capfirst(model._meta.verbose_name_plural),
                            'object_name': model._meta.object_name,
                            'perms': perms,
                        }
                        if perms.get('change', False):
                            try:
                                model_dict['admin_url'] = reverse('admin:admin:%s_%s_changelist' % info, current_app=self.name)
                            except NoReverseMatch:
                                pass
                        if perms.get('add', False):
                            try:
                                model_dict['add_url'] = reverse('admin:admin:%s_%s_add' % info, current_app=self.name)
                            except NoReverseMatch:
                                pass
                        if app_dict:
                            app_dict['models'].append(model_dict),
                        else:
                            # First time around, now that we know there's
                            # something to display, add in the necessary meta
                            # information.
                            app_dict = {
                                'name': app_label.title(),
                                'app_label': app_label,
                                'app_url': '',
                                'has_module_perms': has_module_perms,
                                'models': [model_dict],
                            }
        if not app_dict:
            raise Http404('The requested admin page does not exist.')
        # Sort the models alphabetically within each app.
        app_dict['models'].sort(key=lambda x: x['name'])
        context = {
            'title': _('%s administration') % capfirst(app_label),
            'app_list': [app_dict],
        }
        context.update(extra_context or {})

        return TemplateResponse(request, self.app_index_template or [
            'admin/%s/app_index.html' % app_label,
            'admin/app_index.html'
        ], context, current_app=self.name)


django.contrib.admin.site = CollectionAdminSite()
site = django.contrib.admin.site