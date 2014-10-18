from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils.encoding import smart_text
from rest_framework.fields import is_simple_callable, get_component
from rest_framework.relations import PrimaryKeyRelatedField


class RelatedCollectionModelField(PrimaryKeyRelatedField):
    """
    Represents a relationship as a id value.
    """

    # TODO: Remove these field hacks...
    def prepare_value(self, obj):
        return self.to_native(self._get_object_id(obj=obj))

    def label_from_instance(self, obj):
        """
        Return a readable representation for use with eg. select widgets.
        """
        desc = smart_text(obj)
        ident = smart_text(self.to_native(obj.id))
        if desc == ident:
            return desc
        return "%s - %s" % (desc, ident)

    # TODO: Possibly change this to just take `obj`, through prob less performant
    def to_native(self, id):
        return id

    def from_native(self, data):
        if self.queryset is None:
            raise Exception('Writable related fields must include a `queryset` argument')

        try:
            single_object = self.queryset.get(id=data)
            if single_object is None:
                raise ObjectDoesNotExist()

        except ObjectDoesNotExist:
            msg = self.error_messages['does_not_exist'] % smart_text(data)
            raise ValidationError(msg)
        except (TypeError, ValueError):
            received = type(data).__name__
            msg = self.error_messages['incorrect_type'] % received
            raise ValidationError(msg)

    def field_to_native(self, obj, field_name):
        if self.many:
            # To-many relationship

            queryset = None
            if not self.source:
                # Prefer obj.serializable_value for performance reasons
                try:
                    queryset = obj.serializable_value(field_name)
                except AttributeError:
                    pass
            if queryset is None:
                # RelatedManager (reverse relationship)
                source = self.source or field_name
                queryset = obj
                for component in source.split('.'):
                    if queryset is None:
                        return []
                    queryset = get_component(queryset, component)

            # Forward relationship
            if is_simple_callable(getattr(queryset, 'all', None)):
                queryset.all()
                return [self.to_native(self._get_object_id(obj=item)) for item in queryset ]
            else:
                # Also support non-queryset iterables.
                # This allows us to also support plain lists of related items.
                return [self.to_native(self._get_object_id(obj=item)) for item in queryset]

        # To-one relationship
        try:
            # Prefer obj.serializable_value for performance reasons
            id = obj.serializable_value(self.source or field_name)
        except AttributeError:
            # RelatedObject (reverse relationship)
            try:
                id = getattr(obj, self.source or field_name).id
            except (ObjectDoesNotExist, AttributeError):
                return None

        # Forward relationship
        return self.to_native(id)

    def _get_object_id(self, obj):
        """
        """

        return obj.document.id