import six
import warnings

from django.core.exceptions import FieldError
from django.forms.util import ErrorList
from django.forms.widgets import media_property
from django.utils.datastructures import SortedDict
from django.forms.fields import CharField, FileField, ChoiceField
from django.forms.forms import BaseForm, get_declared_fields
from django.forms.models import ModelFormOptions, ALL_FIELDS


from arangodb.orm.fields import CharField as ArangoCharField, ChoiceField as ArangoChoiceField

from djara.django.forms.fields import FileField as ArangoFileField


def map_arangopy_field_to_form_field(model_field, **kwargs):
    """
    """

    if isinstance(model_field, ArangoCharField):
        field = CharField(max_length=model_field.max_length, **kwargs)
    elif isinstance(model_field, ArangoFileField):
        field = FileField(**kwargs)
    elif isinstance(model_field, ArangoChoiceField):
        field = ChoiceField(choices=model_field.choices)
    else:
        field = None

    return field


def fields_for_model(model, fields=None, exclude=None, widgets=None,
                     formfield_callback=None, localized_fields=None,
                     labels=None, help_texts=None, error_messages=None):
    """
    Returns a ``SortedDict`` containing form fields for the given model.

    ``fields`` is an optional list of field names. If provided, only the named
    fields will be included in the returned fields.

    ``exclude`` is an optional list of field names. If provided, the named
    fields will be excluded from the returned fields, even if they are listed
    in the ``fields`` argument.

    ``widgets`` is a dictionary of model field names mapped to a widget.

    ``localized_fields`` is a list of names of fields which should be localized.

    ``labels`` is a dictionary of model field names mapped to a label.

    ``help_texts`` is a dictionary of model field names mapped to a help text.

    ``error_messages`` is a dictionary of model field names mapped to a
    dictionary of error messages.

    ``formfield_callback`` is a callable that takes a model field and returns
    a form field.
    """
    field_list = []
    ignored = []
    # Avoid circular import
    # from django.db.models.fields import Field as ModelField
    # sortable_virtual_fields = [f for f in opts.virtual_fields
    #                            if isinstance(f, ModelField)]
    sortable_virtual_fields = model.get_collection_fields()
    for f in sorted(sortable_virtual_fields):
        if getattr(f, 'read_only', True):
            continue
        if fields is not None and not f.name in fields:
            continue
        if exclude and f.name in exclude:
            continue

        kwargs = {}
        if widgets and f.name in widgets:
            kwargs['widget'] = widgets[f.name]
        if localized_fields == ALL_FIELDS or (localized_fields and f.name in localized_fields):
            kwargs['localize'] = True
        if labels and f.name in labels:
            kwargs['label'] = labels[f.name]
        if help_texts and f.name in help_texts:
            kwargs['help_text'] = help_texts[f.name]
        if error_messages and f.name in error_messages:
            kwargs['error_messages'] = error_messages[f.name]

        if formfield_callback is None:
            formfield = map_arangopy_field_to_form_field(f, **kwargs)
            # formfield = f.formfield(**kwargs)
        elif not callable(formfield_callback):
            raise TypeError('formfield_callback must be a function or callable')
        else:
            formfield = formfield_callback(f, **kwargs)

        if formfield:
            field_list.append((f.name, formfield))
        else:
            ignored.append(f.name)
    field_dict = SortedDict(field_list)
    if fields:
        field_dict = SortedDict(
            [(f, field_dict.get(f)) for f in fields
                if ((not exclude) or (exclude and f not in exclude)) and (f not in ignored)]
        )
    return field_dict

class BaseCollectionForm(BaseForm):

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=ErrorList, label_suffix=None,
                 empty_permitted=False, instance=None):
        opts = self._meta
        if opts.model is None:
            raise ValueError('ModelForm has no model class specified.')
        if instance is None:
            # if we didn't get an instance, instantiate a new one
            self.instance = opts.model()
            object_data = {}
        else:
            self.instance = instance
            object_data = {}
            # object_data = model_to_dict(instance, opts.fields, opts.exclude)
        # if initial was provided, it should override the values from instance
        # if initial is not None:
        #     object_data.update(initial)
        # self._validate_unique will be set to True by BaseModelForm.clean().
        # It is False by default so overriding self.clean() and failing to call
        # super will stop validate_unique from being called.
        self._validate_unique = False
        super(BaseCollectionForm, self).__init__(data, files, auto_id, prefix, object_data,
                                            error_class, label_suffix, empty_permitted)

class CollectionFormMetaclass(type):
    def __new__(cls, name, bases, attrs):
        formfield_callback = attrs.pop('formfield_callback', None)
        try:
            parents = [b for b in bases if issubclass(b, CollectionForm)]
        except NameError:
            # We are defining ModelForm itself.
            parents = None

        declared_fields = get_declared_fields(bases, attrs, False)
        new_class = super(CollectionFormMetaclass, cls).__new__(cls, name, bases,
                attrs)
        if not parents:
            return new_class

        if 'media' not in attrs:
            new_class.media = media_property(new_class)
        opts = new_class._meta = ModelFormOptions(getattr(new_class, 'Meta', None))

        # We check if a string was passed to `fields` or `exclude`,
        # which is likely to be a mistake where the user typed ('foo') instead
        # of ('foo',)
        for opt in ['fields', 'exclude', 'localized_fields']:
            value = getattr(opts, opt)
            if isinstance(value, six.string_types) and value != ALL_FIELDS:
                msg = ("%(model)s.Meta.%(opt)s cannot be a string. "
                       "Did you mean to type: ('%(value)s',)?" % {
                           'model': new_class.__name__,
                           'opt': opt,
                           'value': value,
                       })
                raise TypeError(msg)

        if opts.model:
            # If a model is defined, extract form fields from it.

            if opts.fields is None and opts.exclude is None:
                # This should be some kind of assertion error once deprecation
                # cycle is complete.
                warnings.warn("Creating a ModelForm without either the 'fields' attribute "
                              "or the 'exclude' attribute is deprecated - form %s "
                              "needs updating" % name,
                              PendingDeprecationWarning, stacklevel=2)

            if opts.fields == ALL_FIELDS:
                # sentinel for fields_for_model to indicate "get the list of
                # fields from the model"
                opts.fields = None

            fields = fields_for_model(opts.model, opts.fields, opts.exclude,
                                      opts.widgets, formfield_callback,
                                      opts.localized_fields, opts.labels,
                                      opts.help_texts, opts.error_messages)

            # make sure opts.fields doesn't specify an invalid field
            none_model_fields = [k for k, v in six.iteritems(fields) if not v]
            missing_fields = set(none_model_fields) - \
                             set(declared_fields.keys())
            if missing_fields:
                message = 'Unknown field(s) (%s) specified for %s'
                message = message % (', '.join(missing_fields),
                                     opts.model.__name__)
                raise FieldError(message)
            # Override default model fields with any custom declared ones
            # (plus, include all the other declared fields).
            fields.update(declared_fields)
        else:
            fields = declared_fields
        new_class.declared_fields = declared_fields
        new_class.base_fields = fields
        return new_class

class CollectionForm(six.with_metaclass(CollectionFormMetaclass, BaseCollectionForm)):

    def save(self):
        """
        """

        for key, value in self.cleaned_data.items():
            setattr(self.instance, key, value)

        self.instance.save()