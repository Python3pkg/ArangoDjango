from rest_framework import serializers, fields, relations
from arangodb.orm.fields import NumberField, CharField, ForeignKeyField, ManyToManyField


class CollectionModelSerializerOptions(serializers.SerializerOptions):
    """
    Meta class options for CollectionModelSerializer
    """
    def __init__(self, meta):
        super(CollectionModelSerializerOptions, self).__init__(meta)
        self.model = getattr(meta, 'model', None)
        self.read_only_fields = getattr(meta, 'read_only_fields', ())
        self.write_only_fields = getattr(meta, 'write_only_fields', ())

class CollectionModelSerializer(serializers.Serializer):
    """
    """

    _options_class = CollectionModelSerializerOptions

    field_mapping = {
        NumberField: fields.IntegerField,
        CharField: fields.CharField,
    }

    def get_fields(self):
        """
        """

        return_fields = {}

        model_class = self.opts.model

        model_class_fields = model_class.get_collection_fields_dict()

        for field_name in model_class_fields:
            field = model_class_fields[field_name]

            kwargs = {}

            if field.__class__ in self.field_mapping:
                restframework_field_class = self.field_mapping[field.__class__]
                restframework_field = restframework_field_class(**kwargs)

                return_fields[field_name] = restframework_field

            # get_related_field
            if isinstance(field, ForeignKeyField):
                return_fields[field_name] = self.get_related_field(model_field=field, related_model=field.relation_class, to_many=False)
            if isinstance(field, ManyToManyField):
                return_fields[field_name] = self.get_related_field(model_field=field, related_model=field.relation_class, to_many=True)

        return return_fields

    def get_field(self, model_field):
        """
        Creates a default instance of a basic non-relational field.
        """

    def get_related_field(self, model_field, related_model, to_many):
        """
        Creates a default instance of a flat relational field.

        Note that model_field will be `None` for reverse relationships.
        """
        # TODO: filter queryset using:
        # .using(db).complex_filter(self.rel.limit_choices_to)

        kwargs = {
            'queryset': related_model.objects,
            'many': to_many
        }

        if model_field:
            kwargs['required'] = not(model_field.null or model_field.blank)
            # if model_field.help_text is not None:
            #     kwargs['help_text'] = model_field.help_text
            # if model_field.verbose_name is not None:
            #     kwargs['label'] = model_field.verbose_name

            # if not model_field.editable:
            #     kwargs['read_only'] = True

            # if model_field.verbose_name is not None:
            #     kwargs['label'] = model_field.verbose_name

            # if model_field.help_text is not None:
            #     kwargs['help_text'] = model_field.help_text

        return relations.PrimaryKeyRelatedField(**kwargs)

    def save_object(self, obj, **kwargs):

        model_class = self.opts.model
        obj = model_class.objects._create_model_from_dict(obj)
        self.object = obj

        obj.save()

    def delete_object(self, obj):
        obj.delete()

    def save(self, **kwargs):
        """
        Save the deserialized object and return it.
        """
        # Clear cached _data, which may be invalidated by `save()`
        self._data = None

        if isinstance(self.object, list):
            [self.save_object(item, **kwargs) for item in self.object]

            if self.object._deleted:
                [self.delete_object(item) for item in self.object._deleted]
        else:
            self.save_object(self.object, **kwargs)

        return self.object