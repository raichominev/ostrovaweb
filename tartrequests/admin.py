import os

from datetime import datetime, timedelta

from django_object_actions import DjangoObjectActions

from datetimewidget.widgets import DateTimeWidget
from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.core.files.storage import default_storage
from django.core.urlresolvers import reverse_lazy
from django import forms
from django.forms import ModelForm, TextInput, Textarea

from clever_select_enhanced.clever_txt_field import ChainedTextInputField
from clever_select_enhanced.form_fields import ChainedModelChoiceField, ChainedChoiceField
from clever_select_enhanced.forms import ChainedChoicesModelForm
from ostrovaweb.utils import fix_code
from tartrequests.models import *


class TortaRequestInline(admin.StackedInline):
    model = TortaRequestPicture
    fieldsets = (
        ('', {
            'fields': ('filename',),
        }),
    )
    readonly_fields = ['last_update_date',]
    extra = 0

# class TortaRequestTasteForm(ChainedChoicesModelForm):
#     torta_rq_fk = forms.CharField()
#     torta_taste_fk = ChainedModelChoiceField(parent_field='code', inline_fk_to_master = 'torta_rq_fk', ajax_url=reverse_lazy('torta_request_ajax_chained_models'),
#                                              label = u'Пълнеж', empty_label=u'------', required=True, model=TortaTasteRegister)
#
#     price= ChainedTextInputField(parent_field='torta_taste_fk', ajax_url=reverse_lazy('torta_request_ajax_chained_models'),
#                                  label=u'Ед. Цена', required=False, widget_attrs={'readonly': 'true'})


# class TortaRequestInlineTastes(admin.TabularInline):
#     model = TortaRequestTaste
#     form = TortaRequestTasteForm
#     fieldsets = (
#         ('', {
#             'fields': ('rec', 'torta_taste_fk','price'),
#         }),
#     )
#
#     # Displays sequential record number, which
#     current_id = 0
#     def rec(self, obj):
#         self.current_id = self.current_id+1
#         return str(self.current_id)
#     rec.short_description='Етаж'
#
#     def code(self, obj):
#         return self.parent_model.code
#
#     readonly_fields = ('rec',)
#     extra = 1

# class ChainedChoiceFieldExtraWgtArgs(ChainedChoiceField):
#
#     attrs = {}
#
#     def __init__(self, widget_attrs = {}, *args, **kwargs):
#
#         self.attrs = widget_attrs
#         super(ChainedChoiceFieldExtraWgtArgs, self).__init__(*args, **kwargs)
#
#     def widget_attrs(self,widget):
#         return self.attrs


class TortaRequestForm(ChainedChoicesModelForm):

    delivery_address = forms.ModelChoiceField(label="Адрес на доставка", queryset=None, empty_label='-------', required=False)

    tart_type = ChainedTextInputField(parent_field='code', ajax_url=reverse_lazy('torta_request_ajax_chained_models'),
                                      label=u'Тип на торта', required=True, widget_attrs={'readonly': 'true'})

    tart_name = ChainedTextInputField(parent_field='code', ajax_url=reverse_lazy('torta_request_ajax_chained_models'),
                                      label=u'Категория', required=True, widget_attrs={'readonly': 'true'})

    tart_size = ChainedChoiceField(parent_field='tart_type', ajax_url=reverse_lazy('torta_request_ajax_chained_models'),
                                   label=u'Големина', required=True)

    torta_cnt = ChainedTextInputField(parent_field='tart_size', ajax_url=reverse_lazy('torta_request_ajax_chained_models'),
                                      label=u'Брой парчета', required=True, widget_attrs={'readonly': 'true'})

    #    price= ChainedTextInputField(parent_field='palnej', ajax_url=reverse_lazy('torta_request_ajax_chained_models'),
    #                                   label=u'Ед. Цена', required=False, widget_attrs={'readonly': 'true'})

    # def clean_code(self):
    #     self.cleaned_data['code'] = fix_code(self.cleaned_data['code']).upper()
    #     return self.cleaned_data['code']

    class Media:
        js = (
                 #'js/moment.min.js',
                 'js/moment-with-locales.min.js',
                 'js/bootstrap-datetimepicker.js'
             )
        css = {
            'all' : ('css/bootstrap-datetimepicker.min.css',),
        }

    class Meta:
        model = TortaRequest
        fields = '__all__'
        widgets = {
            'code': TextInput(attrs={'style':'width:80px'}),
            'nadpis': TextInput(attrs={'style':'width:500px'}),
            'notes': Textarea(attrs={'style':'width:500px'}),
            'dostavka_date': DateTimeWidget(options = {
                'format': 'yyyy-mm-dd hh:ii',
                'startDate': (datetime.now()+ timedelta(days=1)).strftime('%Y-%m-%d'),
                'initialDate': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d 09:00'),
                'minView':1,
                'hoursDisabled': '"0,1,2,3,4,5,6,7,8,10,12,14,16,18,20,21,22,23"',
            })
        }

class TortaRequestAdmin(ModelAdmin):

    form = TortaRequestForm
    model = TortaRequest

    list_display = ('code','tart_type','tart_name','palnej','torta_cnt','price','status', 'id', 'reg_date')
    search_fields = ('tart_name','code',)
    list_filter = (
        ('status', admin.ChoicesFieldListFilter),
        'reg_date',
        'dostavka_date',
    )
    ordering = ['-id']
    list_per_page = 50

    # this is necessary for the DateTimeWidget to save properly
    formfield_overrides = {
        models.DateTimeField: {
            'form_class': forms.DateTimeField,
        },
    }

    suit_form_includes = (
        ('admin/tortarequest/show_picture_include.html','top'),
    )

    fieldsets = (
        ('Торта', {
            'fields': ('code', 'tart_type', 'tart_name', 'tart_size','torta_cnt', 'nadpis', 'palnej'),
        }),

        ('Доставка', {
            'fields': ('dostavka_date', 'delivery_address', 'client_phone', 'status'),
        }),

        ('Допълнителна информация', {
            'fields': ( 'notes', ),
        }),

        ('Служебна информация', {
            'fields': ( 'reg_date','last_update_date', 'user_fk', 'club_fk'),
        }),

    )
    readonly_fields = ['last_update_date', 'user_fk','id','reg_date']

    inlines = [ TortaRequestInline, ]


    def get_form(self, request, obj=None, **kwargs):

        form = super(TortaRequestAdmin, self).get_form(request, obj,**kwargs)

        # if edditing (obj will be filled in with the exeistin model)
        if obj:
            # alternatives for readonly:
            # form.base_fields['supplier_fk'].widget.attrs.update({'readonly':'True','style':'pointer-events:none'})
            # form.base_fields['club_fk'].widget = django.forms.widgets.Select(attrs={'readonly':'True','onfocus':"this.defaultIndex=this.selectedIndex;", 'onchange':"this.selectedIndex=this.defaultIndex;"})
            form.base_fields['club_fk'].disabled = True

        # if club is specified for the current user (in the user model), do not allow choosing another club
        if request.user.employee.club_fk:
            form.base_fields['club_fk'].initial = request.user.employee.club_fk
            form.base_fields['club_fk'].widget.attrs.update({'readonly':'True','style':'pointer-events:none'})  # simulates readonly on the browser with the help of css
            #form.base_fields['club_fk'].disabled = True  - does not work well on add new operation's on save

            form.base_fields['status'].disabled = True

        form.base_fields['delivery_address'].queryset = TortaDeliveryAddress.objects.filter(group__in=request.user.groups.all())

        return form

    def save_model(self, request, obj, form, change):

        obj.user_fk = request.user
        obj.last_update_date = datetime.now().replace(microsecond=0)
        obj.save()


admin.site.register(TortaRequest, TortaRequestAdmin)


# class TortaPictureRegisterForm(ModelForm):
#     #category = forms.ChoiceField()
#
#     def __init__(self, *args, **kwargs):
#         super(TortaPictureRegisterForm, self).__init__(*args, **kwargs)
#
#
#         target_folder = ''
#
#         #directories = ['ЗАЯВКИ',]
#         # self.fields['category'].choices =  tuple(directories)


class TortaPictureRegisterAdmin(DjangoObjectActions, ModelAdmin):

    search_fields = ('description','code','category')
    list_filter = (
        'category','tart_type'
    )
    list_display = ('code__code','tart_type','category','description')
    readonly_fields = ['last_update_date', ]
    ordering = ['code']
    list_per_page = 50

    suit_form_includes = (
        ('admin/tortapictureregister/show_picture_include.html',),
    )

    def reload_pics_from_storage(self, request, obj):

        for categoty_folder in default_storage.listdir(settings.TARTIMAGES_STORAGE)[0]:
            if not TortaPictureCategory.objects.filter(category=categoty_folder).exists():
                dbCat = TortaPictureCategory()
                dbCat.category = categoty_folder
                dbCat.save()
            else:
                dbCat = TortaPictureCategory.objects.get(category = categoty_folder)

            for fl in default_storage.listdir('/'.join((settings.TARTIMAGES_STORAGE,categoty_folder,)))[1]:
                if fl.split('.')[-1].upper() in ('PNG','JPG'):

                    code = fix_code(fl.split('.')[0]).upper()
                    if not TortaPictureRegister.objects.filter(code=code).exists():

                        pic = TortaPictureRegister()
                        pic.filename = settings.TARTIMAGES_STORAGE + "/" + categoty_folder + "/" + fl
                        pic.category = dbCat
                        pic.code = code

                        if code.startswith('D'):
                            pic.tart_type = '3D'
                        elif code.startswith('K'):
                            pic.tart_type = 'Захарна плака'
                        else:
                            pic.tart_type = 'Стандартна'

                        pic.save()

    reload_pics_from_storage.label = "Ръчно презареждане"
    reload_pics_from_storage.short_description = "Ръчно презареждане"

    change_actions = ('reload_pics_from_storage',)
    #changelist_actions = ('reload_pics_from_storage',)

    def save_model(self, request, obj, form, change):

        obj.code = fix_code(obj.code).upper()
        obj.last_update_date = datetime.now().replace(microsecond=0)
        obj.save()


admin.site.register(TortaPictureRegister, TortaPictureRegisterAdmin)

class TortaTasteRegisterAdmin(ModelAdmin):

    list_filter     = (
        'level','palnej'
    )
    list_display    = ('id', 'level','palnej','price')
    readonly_fields = ['last_update_date', ]
    list_editable   = ('palnej','level','price')
    ordering        = ['level', 'palnej']
    list_per_page = 50
    # exclude = []

    def save_model(self, request, obj, form, change):
        obj.last_update_date = datetime.now().replace(microsecond=0)
        obj.save()

admin.site.register(TortaTasteRegister, TortaTasteRegisterAdmin)


class TortaPieceCodingAdmin(ModelAdmin):

    list_filter = (
        'tart_type', 'levels', 'torta_cnt'
    )
    fields = ('tart_type', 'levels', 'torta_cnt')
    list_display = ('tart_size','tart_type', 'levels', 'torta_cnt')
    list_editable = ('tart_type', 'levels', 'torta_cnt')
    ordering = ['tart_type', 'levels', 'torta_cnt']
    list_per_page = 50

admin.site.register(TortaPieceCoding, TortaPieceCodingAdmin)


class TortaPictureCategoryAdmin(ModelAdmin):

    fields = ('category',)
    list_display = ('category',)
    list_editable = ('category',)
    ordering = ['category',]
    list_per_page = 50

admin.site.register(TortaPictureCategory, TortaPictureCategoryAdmin)

class TortaDeliveryAddressAdmin(ModelAdmin):

    fields = ('delivery_address','group')
    list_display = ('delivery_address','group',)
    list_editable = ('delivery_address','group',)
    ordering = ['group', 'delivery_address',]
    list_per_page = 50

admin.site.register(TortaDeliveryAddress, TortaDeliveryAddressAdmin)

