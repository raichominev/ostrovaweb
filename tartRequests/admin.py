import os

from datetime import datetime
from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.core.files.storage import default_storage
from django.core.urlresolvers import reverse_lazy
from django import forms
from django.forms import ModelForm, TextInput

from clever_select_enhanced.clever_txt_field import ChainedTextInputField
from clever_select_enhanced.form_fields import ChainedModelChoiceField, ChainedChoiceField
from clever_select_enhanced.forms import ChainedChoicesModelForm
from tartRequests.models import *


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

    tart_type = ChainedTextInputField(parent_field='code', ajax_url=reverse_lazy('torta_request_ajax_chained_models'),
                                      label=u'Тип на торта', required=True, widget_attrs={'readonly': 'true'})

    tart_name = ChainedTextInputField(parent_field='code', ajax_url=reverse_lazy('torta_request_ajax_chained_models'),
                                      label=u'Наименование', required=True, widget_attrs={'readonly': 'true'})

    tart_size = ChainedChoiceField(parent_field='tart_type', ajax_url=reverse_lazy('torta_request_ajax_chained_models'),
                                   label=u'Големина', required=True)

    torta_cnt = ChainedTextInputField(parent_field='tart_size', ajax_url=reverse_lazy('torta_request_ajax_chained_models'),
                                      label=u'Брой парчета', required=True, widget_attrs={'readonly': 'true'})

    #    price= ChainedTextInputField(parent_field='palnej', ajax_url=reverse_lazy('torta_request_ajax_chained_models'),
    #                                   label=u'Ед. Цена', required=False, widget_attrs={'readonly': 'true'})

    class Meta:
        model = TortaRequest
        fields = '__all__'
        widgets = {
            #'tart_type': TextInput(attrs={'style':'width:80px'}),
            'code': TextInput(attrs={'style':'width:80px'}),
            #'torta_cnt': NumberInput(attrs={'style':'width:80px'}),
            #'tart_name': TextInput(attrs={'style':'width:200px'}),
            #'price': NumberInput(attrs={'style':'width:80px'}),
            'nadpis': TextInput(attrs={'style':'width:500px'}),
            #'palnej': TextInput(attrs={'style':'width:200px'}),
        }

class TortaRequestAdmin(ModelAdmin):
    #autocomplete is a work in progress for now.
    #form = autocomplete_light.modelform_factory(ArtikulTypes)

    form = TortaRequestForm
    model = TortaRequest

    list_display = ('code','tart_type','tart_name','torta_cnt','price','status', 'id', 'reg_date')
    search_fields = ('tart_name','code',)
    list_filter = (
        ('status', admin.ChoicesFieldListFilter),
        'reg_date',
        'dostavka_date',
    )
    ordering = ['-id']
    list_per_page = 50

    fieldsets = (
        ('Торта', {
            'fields': ('code', 'tart_type', 'tart_name', 'tart_size','torta_cnt', 'nadpis'),
        }),

        ('Доставка', {
            'fields': ('dostavka_date', 'delivery_address', 'client_phone', 'status'),
        }),

        ('Допълнителна информация', {
            'fields': ( 'notes', ),
        }),

        ('Служебна информация', {
            'fields': ('changes', 'reg_date','last_update_date', 'user_fk', 'club_fk'),
        }),

    )
    readonly_fields = ['changes','last_update_date', 'club_fk', 'user_fk','id']
    #list_editable   = ()
    # exclude = []


    # def get_changelist_form(self, request, **kwargs):
    #     kwargs.setdefault('form', self.form)
    #     return super(TortaRequestAdmin, self).get_changelist_form(request, **kwargs)

    inlines = [ TortaRequestInline, ]


    def get_changeform_initial_data(self, request):
        # auto-populate user
        get_data = super(TortaRequestAdmin, self).get_changeform_initial_data(request)
        get_data['user_id'] = request.user.pk
        return get_data

    def save_model(self, request, obj, form, change):

        obj.user_fk = request.user
        obj.last_update_date = datetime.now().replace(microsecond=0)
        obj.save()


admin.site.register(TortaRequest, TortaRequestAdmin)


class TortaPictureRegisterForm(ModelForm):
    category = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        super(TortaPictureRegisterForm, self).__init__(*args, **kwargs)


        # target_folder = settings.MEDIA_ROOT + "/" +

        directories = []
        for categoty_folder in default_storage.listdir(settings.TARTIMAGES_STORAGE):
            #if os.path.isdir('/'.join((target_folder,categoty_folder,))):
                directories.append((categoty_folder, categoty_folder),)

                # for fl in os.listdir('/'.join((target_folder,categoty_folder,))):
                #     if fl.split('.')[-1] in ('png','jpg'):
                #         pic = TortaPictureRegister()
                #         pic.filename = settings.TARTIMAGES_STORAGE + "/" + categoty_folder + "/" + fl
                #         pic.category = categoty_folder
                #         pic.code = fl.split('.')[0]
                #
                #         pic.save()

        self.fields['category'].choices =  tuple(directories)


class TortaPictureRegisterAdmin(ModelAdmin):

    search_fields = ('description','code','category')
    list_filter = (
        'category',
    )
    list_display = ('code','tart_type','category','description')
    readonly_fields = ['last_update_date', ]
    #list_editable   = ()
    ordering = ['code']
    list_per_page = 50
    # exclude = []

    suit_form_includes = (
        ('admin/tortapictureregister/show_picture_include.html',),
    )
    form = TortaPictureRegisterForm

    filter_horizontal = ('torta_tase_fk',)

    # def get_changelist_form(self, request, **kwargs):
    #     kwargs.setdefault('form', self.form)
    #     return super(TortaRequestAdmin, self).get_changelist_form(request, **kwargs)

    def save_model(self, request, obj, form, change):
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
