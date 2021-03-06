from functools import lru_cache

from flask_wtf import Form
from sqlalchemy import inspect
from sqlalchemy.orm import Mapper
from wtforms_alchemy import (model_form_factory, null_or_unicode,
                             FormGenerator as _FormGenerator)


BaseModelForm = model_form_factory(Form)


class FormGenerator(_FormGenerator):

    def type_agnostic_parameters(self, key, column):
        kwargs = super().type_agnostic_parameters(key, column)
        # if the label wasn't explicitly defined in the column.info then make it
        # the capitalized version of the key with any special characters remove
        if 'label' not in column.info:
            trans_table = str.maketrans({'_': ' '})
            kwargs['label'] = column.name.translate(trans_table).capitalize()

        return kwargs


    def select_field_kwargs(self, column):
        kwargs = super().select_field_kwargs(column)
        if column.nullable and ('', '') not in kwargs.get('choices', []):
            # kwargs.setdefault('choices', []).insert(0, (None, None))
            kwargs.setdefault('choices', []).insert(0, ('', ''))
            # work around a bug with wtforms-alchemy's null_or_unicode
            # coercion function where it converts None to 'None'
            kwargs['coerce'] = lambda v: v if v is None else null_or_unicode(v)

        return kwargs


@lru_cache()
def form_class_factory(model_cls, base_form_cls=BaseModelForm, **kwargs):
    # equivalent to following but gives a nicer class name:
    # class UserForm(BaseModelForm):
    #     class Meta:
    #         model = User
    options = {
        'form_generator': FormGenerator,
        'model': model_cls,
        'exclude': ['created_at', 'updated_at'],
        'include_foreign_keys': True
    }
    options.update(kwargs)

    Meta = type('Meta', (object, ), options)

    # dynamically define our form type that extends base
    # print('model_cls: ', model_cls)
    ModelForm = type('{}Form'.format(model_cls.__name__), (base_form_cls, ), {
        'Meta': Meta
    })
    return ModelForm


def form_factory(model, **form_kwargs):
    mapper = inspect(model)
    model_cls = model
    if not isinstance(mapper, Mapper):
        model_cls = type(model)
        form_kwargs['obj'] = model

    return form_class_factory(model_cls)(**form_kwargs)
