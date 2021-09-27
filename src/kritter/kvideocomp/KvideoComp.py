# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class KvideoComp(Component):
    """A KvideoComp component.
ExampleComponent is an example component.
It takes a property, `label`, and
displays it.
It renders an input with the property `value`
which is editable by the user.

Keyword arguments:
- image (list; optional): Image
- id (string; optional): The ID used to identify this component in Dash callbacks.
- width (number; optional): The width used to specify width of video window
- height (number; optional): The height used to specify height of video window"""
    @_explicitize_args
    def __init__(self, image=Component.UNDEFINED, id=Component.UNDEFINED, width=Component.UNDEFINED, height=Component.UNDEFINED, **kwargs):
        self._prop_names = ['image', 'id', 'width', 'height']
        self._type = 'KvideoComp'
        self._namespace = 'kvideocomp'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['image', 'id', 'width', 'height']
        self.available_wildcard_properties =            []

        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(KvideoComp, self).__init__(**args)
