from datetime import datetime

from django.contrib import admin
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.forms import ModelForm
from reversion_compare.admin import CompareVersionAdmin

from cashdesk.models import Cashdesk, Cashdesk_detail_expense
from clever_select_enhanced.forms import ChainedChoicesModelForm
from delivery.models import *
from nomenclature.models import Cashdesk_groups_expense, ArticleGroup
from store.models import stock_receipt_protocol, ArticleStore, stock_acceptance_detail


class DeliveryDetailForm(ChainedChoicesModelForm):

    price = ChainedNumberInputField(parent_field='article_fk', ajax_url=reverse_lazy('article_ajax_chained_models'),
                                    label=u'Цена', required=True)

    class Meta:
        model = DeliveryDetail
        fields = '__all__'


class DeliveryDetailInline(admin.TabularInline):
    model = DeliveryDetail
    form = DeliveryDetailForm

    fields = ('article_fk','cnt','price','price_final',)

    select_related = ('group', 'article')

    raw_id_fields = ( 'article_fk', )

    readonly_fields = ('price_final',)

    def price_final(self,obj):
        return nvl(obj.price, 0) * nvl(obj.cnt, 0)


class DeliveryAdmin(CompareVersionAdmin):
    list_display = ('id','club_fk','order_date', 'delivery_date', 'supplier_fk', 'invoice_no','firm_invoice_no','status', 'paid','delivery_amount',)
    # list_editable = ('club_fk','status')
    search_fields = ('club_fk','order_date','supplier_fk',)
    list_filter     = (
        'order_date','club_fk',
    )

    ordering        = ['-id']
    list_per_page = 50
    date_hierarchy = "order_date"

    def get_form(self, request, obj=None, **kwargs):

        form = super(DeliveryAdmin, self).get_form(request, obj,**kwargs)

        # if edditing (obj will be filled in with the exeistin model)
        if obj:
            # alternatives for readonly:
            # form.base_fields['supplier_fk'].widget.attrs.update({'readonly':'True','style':'pointer-events:none'})
            # form.base_fields['club_fk'].widget = django.forms.widgets.Select(attrs={'readonly':'True','onfocus':"this.defaultIndex=this.selectedIndex;", 'onchange':"this.selectedIndex=this.defaultIndex;"})
            form.base_fields['supplier_fk'].disabled = True
            form.base_fields['club_fk'].disabled = True
            if obj.status in ('DELIVERED','CANCELED'):
                form.base_fields['status'].disabled = True
                form.base_fields['status'].widget.attrs.update({'readonly':'True','style':'pointer-events:none'})


        # if club is specified for the current user (in the user model), do not allow choosing another club
        if request.user.employee.club_fk:
            form.base_fields['club_fk'].initial = request.user.employee.club_fk
            form.base_fields['club_fk'].widget.attrs.update({'readonly':'True','style':'pointer-events:none'})  # simulates readonly on the browser with the help of css
            #form.base_fields['club_fk'].disabled = True  - does not work well on add new operation's on save

        return form

    readonly_fields = ('id','delivery_amount','user', 'last_update_date', 'order_date', 'delivery_date')

    fieldsets = [
        (None, {
            'classes': ('suit-tab', 'suit-tab-provider',),
            'fields': ['id','supplier_fk','order_date','delivery_date','invoice_no','firm_invoice_no','club_fk','status','paid','delivery_amount',]
        }),

        ('Забележки', {
            'classes': ('suit-tab', 'suit-tab-notes',),
            'fields': ['notes','user','last_update_date',]
        }),
    ]

    suit_form_tabs = (('provider', 'Доставка'), ('notes', 'Забележки'))

    inlines = [
        DeliveryDetailInline,
    ]

    def save_model(self, request, obj, form, change):

        ###############################################################
        # Handle payment
        ###############################################################
        if 'paid' in form.changed_data and form.cleaned_data['paid'] == 'ДА':
            payment_doc = Cashdesk_detail_expense()

            payment_doc.delivery_fk = obj
            payment_doc.amount = obj.delivery_amount
            payment_doc.note = str(obj)
            payment_doc.group_fk = Cashdesk_groups_expense.objects.get(name='ДОСТАВКА',sub_name='ПЛАЩАНЕ')
            payment_doc.cashdesk = Cashdesk.objects.filter(club_fk=obj.club_fk).latest('id')

            payment_doc.save()

            messages.info(request,"Добавено плащане за %.2f лв. Номер:%d, Каса:%s " % (payment_doc.amount,payment_doc.id, str(payment_doc.cashdesk)))

        ###############################################################
        # Handle store record
        ###############################################################

        if 'status' in form.changed_data and form.cleaned_data['status'] == 'DELIVERED':

            # add stock_receipt_protocol
            delivery_doc = stock_receipt_protocol()
            delivery_doc.delivery_fk = obj
            delivery_doc.club_fk = obj.club_fk
            delivery_doc.delivery_date = datetime.now()
            delivery_doc.type = 'DELIVERY'
            delivery_doc.note = 'Протокол към доставка Номер %d Дата:%s' % (obj.id,obj.delivery_date)
            delivery_doc.closed = True
            delivery_doc.save()

            for delivery_dev in obj.deliverydetail_set.all():

                # lookup store from the other side
                try:
                    artstore = ArticleStore.objects.get(club_fk = obj.club_fk, article_fk = delivery_dev.article_fk)
                except ArticleStore.DoesNotExist:
                    artstore = ArticleStore()
                    artstore.club_fk = obj.club_fk
                    artstore.article_fk = delivery_dev.article_fk
                    artstore.cnt = 0
                    artstore.cnt_min = 0
                    artstore.cnt_bl = 0

                artstore.cnt +=  delivery_dev.cnt
                artstore.save()

                # add stock_acceptance_detail for each deliveydetail
                delivery_acc = stock_acceptance_detail()
                delivery_acc.stock_protocol_fk = delivery_doc
                delivery_acc.article_store_fk = artstore
                delivery_acc.cnt = delivery_dev.cnt
                delivery_acc.save()

                messages.info(request,"Добавен е запис за доставка в склада за %s. налични:%d, " % (str( delivery_dev.article_fk),artstore.cnt, ) )

        ###############################################################
        # Handle misc data
        ###############################################################

        obj.delivery_date = datetime.now()
        obj.last_update_date = datetime.now()
        obj.user = request.user
        if request.user.employee.club_fk:
            obj.club_fk = request.user.employee.club_fk

        super(DeliveryAdmin, self).save_model(request, obj, form, change)

admin.site.register(Delivery, DeliveryAdmin)


class ArticleDeliveryForm(ModelForm):

    def __init__(self,*args,**kwargs):
        super(ArticleDeliveryForm, self).__init__(*args,**kwargs)
        self.fields['group_fk'].queryset=ArticleGroup.objects.filter(delivery_type = True)


class ArticleDeliveryAdmin(admin.ModelAdmin):
    fields = ('id','name', 'description','measure','last_update_date','group_fk','delivery_price',)
    list_display =('name','group_fk','description','measure','delivery_price','sale_price',)
    readonly_fields = ('last_update_date','id',)
    form = ArticleDeliveryForm

    list_filter = (
        ('group_fk', admin.RelatedOnlyFieldListFilter),
    )
    search_fields = ('name', 'description')

admin.site.register(ArticleDelivery, ArticleDeliveryAdmin)
