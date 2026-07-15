"""Applies consistent Tailwind classes to every form field automatically,
so individual forms/templates never need to repeat widget styling.
"""

from typing import TYPE_CHECKING

from django import forms

_TEXT_LIKE = (
    forms.TextInput,
    forms.EmailInput,
    forms.PasswordInput,
    forms.NumberInput,
    forms.URLInput,
    forms.Textarea,
)

_BASE_INPUT_CLASSES = (
    "block w-full rounded-md border border-pvline bg-white px-3 py-2 text-sm "
    "text-pvink placeholder:text-pvslate/60 focus:border-pvblue focus:outline-none "
    "focus:ring-1 focus:ring-pvblue"
)
_SELECT_CLASSES = _BASE_INPUT_CLASSES
_CHECKBOX_CLASSES = "h-4 w-4 rounded border-pvline text-pvblue focus:ring-pvblue"


class TailwindStyledFormMixin:
    """Mixin cooperating with forms.Form/forms.ModelForm; ``self.fields``
    is provided by whichever of those this is combined with (see
    StyledModelForm/StyledForm below).
    """

    if TYPE_CHECKING:
        fields: dict[str, forms.Field]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            existing = widget.attrs.get("class", "")
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs["class"] = f"{existing} {_CHECKBOX_CLASSES}".strip()
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                widget.attrs["class"] = f"{existing} {_SELECT_CLASSES}".strip()
            elif isinstance(widget, _TEXT_LIKE):
                widget.attrs["class"] = f"{existing} {_BASE_INPUT_CLASSES}".strip()
            if isinstance(widget, forms.Textarea):
                widget.attrs.setdefault("rows", 3)


class StyledModelForm(TailwindStyledFormMixin, forms.ModelForm):
    pass


class StyledForm(TailwindStyledFormMixin, forms.Form):
    pass
