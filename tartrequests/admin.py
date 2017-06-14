from datetime import datetime, timedelta
from decimal import Decimal

from adminextensions.list_display import related_field
from django import forms
from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.admin import RelatedOnlyFieldListFilter
from django.contrib.admin import SimpleListFilter
from django.core.files.storage import default_storage
from django.core.urlresolvers import reverse_lazy
from django.forms import Textarea
from django_object_actions import DjangoObjectActions
from django_select2.forms import ModelSelect2Widget

from clever_select_enhanced.form_fields import ChainedModelChoiceField
from clever_select_enhanced.forms import ChainedChoicesModelForm
from datetimewidget.widgets import TimeWidget, DateWidget
from ostrovaweb.utils import fix_code
from tartrequests.models import *
from util.daterange_filter.filter import DateRangeFilter


class TortaRequestInline(admin.StackedInline):
    model = TortaRequestPicture
    fieldsets = (
        ('', {
            'fields': ('filename',),
        }),
    )
    readonly_fields = ['last_update_date',]
    extra = 3
    max_num = 3

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



class CodeFixingModelSelect2Widget(ModelSelect2Widget):
    def filter_queryset(self, term, queryset=None, **dependent_fields):
        term = fix_code(term).upper()
        return super(CodeFixingModelSelect2Widget, self).filter_queryset(term,queryset,**dependent_fields)

class TortaRequestForm(ChainedChoicesModelForm):

    delivery_address = forms.ModelChoiceField(label="Адрес на доставка", queryset=None, empty_label='-------',
                                              required=False)

    tart_size = ChainedModelChoiceField(parent_field='code',
                                        ajax_url=reverse_lazy('torta_request_ajax_chained_models'),
                                        label=u'Големина',
                                        required=True,
                                        widget_attrs={'style':'width:120px'},
                                        model=TortaPieceCoding)

    palnej = ChainedModelChoiceField(parent_field='tart_size',
                                     ajax_url=reverse_lazy('torta_request_ajax_chained_models'),
                                     label=u'Пълнеж',
                                     required=True,
                                     widget_attrs={'style':'width:240px;'},
                                     model=TortaTasteRegister)

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
            'nadpis': Textarea(attrs={'rows':1,'style':'width:340px;height:20px'}),
            'notes': Textarea(attrs={'rows':2, 'style':'height:50px;min-width:200px;width:450px'}),
            'dostavka_date': DateWidget(options = {
                'format': 'yyyy-mm-dd',
                'startDate': (datetime.now()+ timedelta(days=1)).strftime('%Y-%m-%d'),
                'initialDate': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
                'minView':2,
                'language':'bg'
            }),
            'dostavka_time': TimeWidget(options = {
                'format': 'hh:00',
#                'initialDate': '09:00',
                'minView':1,
                'maxView':2,
                'hoursDisabled': '"0,1,2,3,4,5,6,7,8,20,21,22,23"',
                'language':'bg'
            }),
            'code' : CodeFixingModelSelect2Widget(
                 model=TortaPictureRegister,
                 search_fields=['code__icontains','category__category__icontains', 'description__icontains'],
                 attrs={'style':'width:80px', 'data-maximumSelectionLength': '1','data-maximum-selection-length': '1', "multiple":"multiple"},
            )
        }

class ListFilterSeparator(SimpleListFilter):
    template = 'admin/tartrequests/tortarequest/list_filter_separator.html'
    title = '<br>'
    parameter_name = 'separator_dummy'

    def has_output(self):
        return True

    def lookups(self, request, model_admin):
        return ()

    def queryset(self, request, queryset):
        return queryset

class TortaRequestAdmin(ModelAdmin):

    form = TortaRequestForm
    model = TortaRequest

    list_display = ('code',related_field('code__tart_type', None, 'Вид'),related_field('code__category', None, 'Описание'),'palnej','tart_size','full_price','status', 'dostavka_date', 'dostavka_time', 'club_fk', 'notes')
    search_fields = ('code__code', 'code__category__category', 'palnej__palnej', 'nadpis', 'notes')
    list_filter = (
        ('status', admin.ChoicesFieldListFilter),
        ('tart_size',RelatedOnlyFieldListFilter),
        'palnej',
        ('club_fk',RelatedOnlyFieldListFilter),
        ListFilterSeparator,
        ('reg_date', DateRangeFilter),
        ('dostavka_date', DateRangeFilter),
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
        #('admin/tartrequests/tortarequest/include_inlines.html','top'),
        ('admin/tartrequests/tortarequest/show_picture_include.html','top'),
    )

    fieldsets = (
        ('Торта', {
            'fields': ('code', 'tart_size', 'nadpis', 'palnej', 'full_price'),
        }),

        ('Допълнителна информация', {
            'fields': ( 'notes', ),
        }),

        ('Служебна информация', {
            'fields': ( 'dostavka_date','dostavka_time', 'reg_date','last_update_date', 'user_fk', 'club_fk', 'status'),
        }),

    )
    readonly_fields = ['last_update_date', 'user_fk','id','reg_date', 'full_price']

    inlines = [ TortaRequestInline, ]

    def full_price(self, obj):
        if obj and obj.club_fk and obj.tart_size and obj.code:
            priceData = TortaPricePerClub.objects.filter(club_fk = obj.club_fk, tart_type = obj.code.tart_type)
            if priceData:
                return Decimal(round(priceData[0].price * obj.tart_size.torta_cnt,2))
        return Decimal(0)

    full_price.short_description = 'Цена'

    def get_form(self, request, obj=None, **kwargs):

        form = super(TortaRequestAdmin, self).get_form(request, obj,**kwargs)

        # if edditing (obj will be filled in with the exeistin model)
        if obj:
            # alternatives for readonly:
            # form.base_fields['supplier_fk'].widget.attrs.update({'readonly':'True','style':'pointer-events:none'})
            # form.base_fields['club_fk'].widget = django.forms.widgets.Select(attrs={'readonly':'True','onfocus':"this.defaultIndex=this.selectedIndex;", 'onchange':"this.selectedIndex=this.defaultIndex;"})
            form.base_fields['club_fk'].disabled = True

        # if club is specified for the current user (in the user model), do not allow choosing another club
        if request.user.employee.club_m2m.exists():
            if request.user.employee.club_m2m.all().count() == 1:
                form.base_fields['club_fk'].initial = request.user.employee.club_m2m.all()[0]
                form.base_fields['club_fk'].widget.attrs.update({'readonly':'True','style':'pointer-events:none'})  # simulates readonly on the browser with the help of css
            else:
                form.base_fields['club_fk'].queryset = request.user.employee.club_m2m
            #form.base_fields['club_fk'].disabled = True  - does not work well on add new operation's on save

            form.base_fields['status'].disabled = True

        form.base_fields['delivery_address'].queryset = TortaDeliveryAddress.objects.filter(group__in=request.user.groups.all())

        return form

    def save_model(self, request, obj, form, change):

        obj.user_fk = request.user
        obj.last_update_date = datetime.now().replace(microsecond=0)
        obj.save()

    def get_queryset(self, request):
        qs = super(TortaRequestAdmin, self).get_queryset(request)
        if request.user.employee.club_m2m.exists():
            return qs.filter(club_fk__in = request.user.employee.club_m2m.all())

        return qs

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

    search_fields = ('description','code','category__category')
    list_filter = (
        'category','tart_type'
    )
    list_display = ('code','tart_type','category','description')
    readonly_fields = ['last_update_date', ]
    ordering = ['code']
    list_per_page = 50

    suit_form_includes = (
        ('admin/tortapictureregister/show_picture_include.html',),
    )

    def reload_pics_from_storage(self, request, obj):

        for categoty_folder in default_storage.listdir(settings.TARTIMAGES_STORAGE)[0]:

            if categoty_folder == 'ВЪНШНИ ЗАЯВКИ':
                continue

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

class TortaPricePerClubAdmin(ModelAdmin):

    list_filter = (
        'club_fk', 'tart_type'
    )
    list_display    = ('id', 'club_fk','tart_type','price')
    readonly_fields = ['last_update_date', ]
    list_editable   = ('club_fk','tart_type','price')
    ordering        = ['club_fk', 'tart_type']
    list_per_page = 50
    # exclude = []

    def save_model(self, request, obj, form, change):
        obj.last_update_date = datetime.now().replace(microsecond=0)
        obj.save()

admin.site.register(TortaPricePerClub, TortaPricePerClubAdmin)

class TortaTasteRegisterAdmin(ModelAdmin):

    list_filter     = (
        'level','palnej'
    )
    list_display    = ('id', 'level','palnej')
    readonly_fields = ['last_update_date', ]
    list_editable   = ('palnej','level')
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
    fields = ('tart_type', 'levels', 'torta_cnt', 'club_m2m')
    list_display = ('tart_size','tart_type', 'levels', 'torta_cnt')
    list_editable = ('tart_type', 'levels', 'torta_cnt')
    ordering = ['tart_type', 'levels', 'torta_cnt']

    filter_horizontal = ('club_m2m', )

    list_per_page = 50

admin.site.register(TortaPieceCoding, TortaPieceCodingAdmin)


class TortaPictureCategoryAdmin(ModelAdmin):

    fields = ('category',)
    list_display = ('id','category',)
    search_fields = ('category',)
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

