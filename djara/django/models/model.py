from arangodb.orm.fields import ModelField
from arangodb.orm.models import CollectionModel


class DjangoModel(CollectionModel):

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
                return []

        class_meta.get_field_by_name = get_field_by_name

        # Get field, by name
        class_meta.get_field = lambda field: get_field_by_name(field)[0]

        # PK field
        pk_model_field = ModelField()
        pk_model_field.on_init(model_class, 'pk')

        class_meta.pk = pk_model_field