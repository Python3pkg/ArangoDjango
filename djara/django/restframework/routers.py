from rest_framework.routers import DefaultRouter



class CollectionModelRouter(DefaultRouter):

    def get_default_base_name(self, viewset):
        """
        If `base_name` is not specified, attempt to automatically determine
        it from the viewset.
        """
        # Note that `.model` attribute on views is deprecated, although we
        # enforce the deprecation on the view `get_serializer_class()` and
        # `get_queryset()` methods, rather than here.
        model_cls = getattr(viewset, 'model', None)

        if model_cls:
            return model_cls.__name__.lower()