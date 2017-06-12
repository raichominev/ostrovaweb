# -*- coding: utf-8 -*-


'''
Has the filter that allows to filter by a date range.

'''
from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AdminDateWidget, AdminSplitDateTime
from django.db import models
from django.utils.translation import ugettext as _


class DateRangeForm(forms.Form):

    def __init__(self, *args, **kwargs):
        field_name = kwargs.pop('field_name')
        filter_title = kwargs.pop('filter_title')
        super(DateRangeForm, self).__init__(*args, **kwargs)

        self.fields['%s__gte' % field_name] = forms.DateField(
            label='', widget=AdminDateWidget(
                attrs={'placeholder': _('From ' + filter_title)}), localize=True,
            required=False)

        self.fields['%s__lte' % field_name] = forms.DateField(
            label='', widget=AdminDateWidget(
                attrs={'placeholder': _('To ' + filter_title )}), localize=True,
            required=False)


class DateTimeRangeForm(forms.Form):

    def __init__(self, *args, **kwargs):
        field_name = kwargs.pop('field_name')
        filter_title = kwargs.pop('filter_title')
        super(DateTimeRangeForm, self).__init__(*args, **kwargs)
        self.fields['%s__gte' % field_name] = forms.DateTimeField(
                                label='',
                                widget=AdminSplitDateTime(
                                    attrs={'placeholder': _('From ' + filter_title)}
                                ),
                                localize=True,
                                required=False)


class DateRangeFilter(admin.filters.FieldListFilter):

    def __init__(self, field, request, params, model, model_admin, field_path):
        self.lookup_kwarg_since = '%s__gte' % field_path
        self.lookup_kwarg_upto = '%s__lte' % field_path

        # This is to ensure that template with media is loaded only on the first DateRange filter
        # The problem is that when more than one field is displayed, DateTimeShortcuts.js is loaded multiple times
        # and it's init method creates multimple calendar links for *all* fields. To avoid this
        # the list_filter is checked and the media urls are loaded only for the *first* DateRange filter
        self.template = 'daterange_filter/filter_no_media.html'
        for flt in model_admin.list_filter:
            if isinstance(flt, (list, tuple)) and flt[1] == DateRangeFilter:
                if flt[0] == field.name:
                    self.template = 'daterange_filter/filter.html'
                break

        super(DateRangeFilter, self).__init__(
            field, request, params, model, model_admin, field_path)
        self.form = self.get_form(request)

    def choices(self, cl):
        return []

    def expected_parameters(self):
        return [self.lookup_kwarg_since, self.lookup_kwarg_upto]

    def get_form(self, request):
        return DateRangeForm(data=self.used_parameters,
                             field_name=self.field_path,
                             filter_title=self.title)

    def queryset(self, request, queryset):
        if self.form.is_valid():
            # get no null params
            filter_params = dict(filter(lambda x: bool(x[1]),
                                        self.form.cleaned_data.items()))
            return queryset.filter(**filter_params)
        else:
            return queryset


class DateTimeRangeFilter(admin.filters.FieldListFilter):
    #template = 'daterange_filter/filter.html'

    def __init__(self, field, request, params, model, model_admin, field_path):
        self.lookup_kwarg_since = '%s__gte' % field_path
        self.lookup_kwarg_upto = '%s__lte' % field_path

        # This is to ensure that template with media is loaded only on the first DateRange filter
        # The problem is that when more than one field is displayed, DateTimeShortcuts.js is loaded multiple times
        # and it's init method creates multimple calendar links for *all* fields. To avoid this
        # the list_filter is checked and the media urls are loaded only for the *first* DateRange filter
        self.template = 'daterange_filter/filter_no_media.html'
        for flt in model_admin.list_filter:
            if isinstance(flt, (list, tuple)) and flt[1] == DateTimeRangeFilter:
                if flt[0] == field.name:
                    self.template = 'daterange_filter/filter.html'
                break

        super(DateTimeRangeFilter, self).__init__(
            field, request, params, model, model_admin, field_path)
        self.form = self.get_form(request)

    def choices(self, cl):
        return []

    def expected_parameters(self):
        return [self.lookup_kwarg_since, self.lookup_kwarg_upto]

    def get_form(self, request):
        return DateTimeRangeForm(data=self.used_parameters,
                                 field_name=self.field_path)

    def queryset(self, request, queryset):
        if self.form.is_valid():
            # get no null params
            filter_params = dict(filter(lambda x: bool(x[1]),
                                        self.form.cleaned_data.items()))
            return queryset.filter(**filter_params)
        else:
            return queryset


# register the filters
admin.filters.FieldListFilter.register(
    lambda f: isinstance(f, models.DateField), DateRangeFilter)
admin.filters.FieldListFilter.register(
    lambda f: isinstance(f, models.DateTimeField), DateTimeRangeFilter)
