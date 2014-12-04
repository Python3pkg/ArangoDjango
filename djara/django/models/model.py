from django.db import models

from arangodb.orm.fields import ModelField
from arangodb.orm.models import CollectionModel, CollectionModelManager, CollectionQueryset
from arangodb.query.advanced import Query


class DjangoQuery(Query):
    """
    """

    def __init__(self):

        super(DjangoQuery, self).__init__()
        self.select_related = True


    def sort_by(self, field, order=None, collection=None):
        """
        """

        if field == 'pk':
            field = '_key'

        if order is None:
            order = self.SORTING_ASC

        self.sorting.append({
            'field': field,
            'order': order,
            'collection': collection,
        })

    def __getattribute__(self, item):
        """
        """

        if item == 'order_by':
            return object.__getattribute__(self, 'sorting')
        else:
            return super(DjangoQuery, self).__getattribute__(item)

class DjangoQueryset(CollectionQueryset):
    """
    """

    def __init__(self, manager):
        """
        """

        super(DjangoQueryset, self).__init__(manager)

        self._query = DjangoQuery()
        self.query = self._query
        
        self.model = manager.model


    def order_by(self, *args):
        """
        """

        # We want only django sorting
        for o in args:
            if o.startswith('-'):
                order = self._query.SORTING_ASC
                o = o.replace('-', '')
            else:
                order = self._query.SORTING_DESC

            field = o

            self._query.sort_by(field=field, order=order)

        self._has_cache = False

        return self


class DjangoModelManager(CollectionModelManager):


    queryset = DjangoQueryset

    def __init__(self, cls):
        """
        """

        super(DjangoModelManager, self).__init__(cls)

        self.model = cls

    def get(self, **kwargs):
        """
        """

        if 'pk' in kwargs:
            search_value = kwargs['pk']
            del kwargs['pk']
            kwargs['_key'] = search_value

        return super(DjangoModelManager, self).get(**kwargs)


class DjangoModel(CollectionModel):

    objects = DjangoModelManager

    @classmethod
    def extend_meta_data(cls, model_class, class_meta):
        """
        """

        def get_field_by_name(field_name):
            """
            """

            fields = model_class.get_all_fields()
            if field_name in fields:
                return [fields[field_name]]
            else:
                raise models.FieldDoesNotExist

        class_meta.get_field_by_name = get_field_by_name

        # Get field, by name
        class_meta.get_field = lambda field: get_field_by_name(field)[0]

        # PK field
        pk_model_field = ModelField()
        pk_model_field.on_init(model_class, 'pk')

        class_meta.pk = pk_model_field

        class_meta.related_fkey_lookups = []