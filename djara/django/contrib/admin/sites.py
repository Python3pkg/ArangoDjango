import django
from django.contrib.admin.sites import AdminSite as DjangoAdminSite


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


django.contrib.admin.site = CollectionAdminSite()