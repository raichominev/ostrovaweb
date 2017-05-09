from django.forms import TextInput, CharField, NumberInput
from django.utils.safestring import mark_safe


class ChainedTextInput(TextInput):
    def __init__(self, parent_field=None, ajax_url=None, field_prefix = None, *args, **kwargs):
        self.parent_field = parent_field
        self.ajax_url = ajax_url
        self.field_prefix = field_prefix
        self.inline_fk_to_master = None
        self.additional_related_field = None

        super(ChainedTextInput, self).__init__(*args, **kwargs)

#    class Media:
#        js = ['js/clever-selects.js']

    def render(self, name, value, attrs={}, choices=()):
        formset_prefix = attrs['id'][:attrs['id'].find('-') + 1]

        if self.field_prefix:
            parentfield_id = self.field_prefix + self.parent_field
        else:
            field_prefix = attrs['id'][:attrs['id'].rfind('-') + 1]

            if not field_prefix:
                parentfield_id = "id_" + self.parent_field
            else:
                parentfield_id = field_prefix + self.parent_field

        attrs.update(self.attrs)
        attrs['ajax_url'] = self.ajax_url

        output = super(ChainedTextInput, self).render(name, value, attrs=attrs)

        js = """
        <script type="text/javascript">
        //<![CDATA[
            $(document).ready(function(){
                var parent_field = $("#%(parentfield_id)s");
                parent_field.addClass('chained-parent-field-txt');
                var chained_ids = parent_field.attr('chained_ids');
                if(chained_ids == null)
                    parent_field.attr('chained_ids', "%(chained_id)s");
                else
                    parent_field.attr('chained_ids', chained_ids + ",%(chained_id)s");
            });
        //]]>
        </script>

        """ % {"parentfield_id": parentfield_id, 'chained_id': attrs['id']}

        output += js

        return mark_safe(output)


class ChainedTextInputField(CharField):
    attrs = {}

    def __init__(self, parent_field, ajax_url, widget_attrs = {}, empty_label='--------', *args, **kwargs):

        self.parent_field = parent_field
        self.ajax_url = ajax_url
        self.attrs = widget_attrs
        self.empty_label = empty_label
        self.inline_fk_to_master = None
        self.additional_related_field = None

        defaults = {
            'widget': ChainedTextInput(parent_field=parent_field, ajax_url=ajax_url, attrs={'empty_label': empty_label}),
        }
        defaults.update(kwargs)

        super(ChainedTextInputField, self).__init__(*args, **defaults)

    def widget_attrs(self,widget):
        attrs = super(CharField, self).widget_attrs(widget)
        attrs.update(self.attrs)
        return attrs

    def valid_value(self, value):
        """Dynamic choices so just return True for now"""
        return True



class ChainedNumberInput(NumberInput):
    def __init__(self, parent_field=None, ajax_url=None, *args, **kwargs):
        self.parent_field = parent_field
        self.ajax_url = ajax_url
        self.inline_fk_to_master = None
        self.additional_related_field = None

        super(ChainedNumberInput, self).__init__(*args, **kwargs)

    #    class Media:
    #        js = ['js/clever-selects.js']

    def render(self, name, value, attrs={}, choices=()):
        field_prefix = attrs['id'][:attrs['id'].rfind('-') + 1]
        formset_prefix = attrs['id'][:attrs['id'].find('-') + 1]

        if not field_prefix:
            parentfield_id = "id_" + self.parent_field
        else:
            parentfield_id = field_prefix + self.parent_field

        attrs.update(self.attrs)
        attrs['ajax_url'] = self.ajax_url

        output = super(ChainedNumberInput, self).render(name, value, attrs=attrs)

        js = """
        <script type="text/javascript">
        //<![CDATA[
            $(document).ready(function(){
                var parent_field = $("#%(parentfield_id)s");
                parent_field.addClass('chained-parent-field-txt');
                var chained_ids = parent_field.attr('chained_ids');
                if(chained_ids == null)
                    parent_field.attr('chained_ids', "%(chained_id)s");
                else
                    parent_field.attr('chained_ids', chained_ids + ",%(chained_id)s");
            });
        //]]>
        </script>

        """ % {"parentfield_id": parentfield_id, 'chained_id': attrs['id']}

        output += js

        return mark_safe(output)


class ChainedNumberInputField(CharField):
    attrs = {}

    def __init__(self, parent_field, ajax_url, widget_attrs = {}, empty_label='--------', *args, **kwargs):

        self.parent_field = parent_field
        self.ajax_url = ajax_url
        self.attrs = widget_attrs
        self.empty_label = empty_label
        self.inline_fk_to_master = None
        self.additional_related_field = None

        defaults = {
            'widget': ChainedNumberInput(parent_field=parent_field, ajax_url=ajax_url, attrs={'empty_label': empty_label}),
        }
        defaults.update(kwargs)

        super(ChainedNumberInputField, self).__init__(*args, **defaults)

    def widget_attrs(self,widget):
        attrs = super(CharField, self).widget_attrs(widget)
        attrs.update(self.attrs)
        return attrs

    def valid_value(self, value):
        """Dynamic choices so just return True for now"""
        return True